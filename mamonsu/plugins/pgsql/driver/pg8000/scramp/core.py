from uuid import uuid4
import hashlib
from stringprep import (
    in_table_a1, in_table_b1, in_table_c21_c22, in_table_c3, in_table_c4,
    in_table_c5, in_table_c6, in_table_c7, in_table_c8, in_table_c9,
    in_table_c12, in_table_d1, in_table_d2)
import unicodedata
from os import urandom
from enum import IntEnum, unique
from .utils import hi, hmac, h, xor, b64enc, uenc, b64dec

# https://tools.ietf.org/html/rfc5802
# https://www.rfc-editor.org/rfc/rfc7677.txt


@unique
class ClientStage(IntEnum):
    get_client_first = 1
    set_server_first = 2
    get_client_final = 3
    set_server_final = 4


@unique
class ServerStage(IntEnum):
    set_client_first = 1
    get_server_first = 2
    set_client_final = 3
    get_server_final = 4


def _check_stage(Stages, current_stage, next_stage):
    if current_stage is None:
        if next_stage != 1:
            raise ScramException(
                "The method " + Stages(1).name + " must be called first.")
    elif current_stage == 4:
        raise ScramException(
            "The authentication sequence has already finished.")
    elif next_stage != current_stage + 1:
        raise ScramException(
            "The next method to be called is " + Stages(current_stage + 1) +
            ", not this method.")


class ScramException(Exception):
    pass


MECHANISMS = ('SCRAM-SHA-1', 'SCRAM-SHA-256')


HASHES = {
    'SCRAM-SHA-1': hashlib.sha1,
    'SCRAM-SHA-256': hashlib.sha256
}


class ScramMechanism():
    def __init__(self, mechanism='SCRAM-SHA-256'):
        if mechanism not in MECHANISMS:
            raise ScramException(
                "The only recognized mechanisms are " + str(MECHANISMS) +
                ".")
        self.mechanism = mechanism
        self.hf = HASHES[self.mechanism]

    def make_auth_info(self, password, iteration_count=4096, salt=None):
        salt, stored_key, server_key = _make_auth_info(
            self.hf, password, iteration_count, salt=salt)
        return salt, stored_key, server_key, iteration_count

    def make_stored_server_keys(self, salted_password):
        _, stored_key, server_key = _c_key_stored_key_s_key(
            self.hf, salted_password)
        return stored_key, server_key

    def make_server(self, auth_fn, s_nonce=None):
        return ScramServer(self, auth_fn, s_nonce=s_nonce)


def _make_auth_info(hf, password, i, salt=None):
    if salt is None:
        salt = urandom(16)

    salted_password = _make_salted_password(hf, password, salt, i)
    _, stored_key, server_key = _c_key_stored_key_s_key(hf, salted_password)
    return salt, stored_key, server_key


class ScramClient():
    def __init__(self, mechanisms, username, password, c_nonce=None):
        self.mech = None
        for mech in MECHANISMS:
            if mech in mechanisms:
                self.mech = mech

        if self.mech is None:
            raise ScramException(
                "The only recognized mechanisms are " + str(MECHANISMS) +
                "and none of those can be found in " + mechanisms + ".")

        self.hf = HASHES[self.mech]
        self.c_nonce = _make_nonce() if c_nonce is None else c_nonce
        self.username = username
        self.password = password
        self.stage = None

    def _set_stage(self, next_stage):
        _check_stage(ClientStage, self.stage, next_stage)
        self.stage = next_stage

    def get_client_first(self):
        self._set_stage(ClientStage.get_client_first)
        self.client_first_bare, client_first = _get_client_first(
            self.username, self.c_nonce)
        return client_first

    def set_server_first(self, message):
        self._set_stage(ClientStage.set_server_first)
        self.server_first = message
        self.auth_message, self.nonce, self.salt, self.iterations = \
            _set_server_first(message, self.c_nonce, self.client_first_bare)

    def get_client_final(self):
        self._set_stage(ClientStage.get_client_final)
        self.server_signature, cfinal = _get_client_final(
            self.hf, self.password, self.salt, self.iterations, self.nonce,
            self.auth_message)
        return cfinal

    def set_server_final(self, message):
        self._set_stage(ClientStage.set_server_final)
        _set_server_final(message, self.server_signature)


class ScramServer():
    def __init__(self, mechanism, auth_fn, s_nonce=None):
        self.m = mechanism
        self.s_nonce = _make_nonce() if s_nonce is None else s_nonce
        self.auth_fn = auth_fn
        self.stage = None

    def _set_stage(self, next_stage):
        _check_stage(ServerStage, self.stage, next_stage)
        self.stage = next_stage

    def set_client_first(self, client_first):
        self._set_stage(ServerStage.set_client_first)
        self.nonce, self.user, self.client_first_bare = _set_client_first(
            client_first, self.s_nonce)
        salt, self.stored_key, self.server_key, self.i = self.auth_fn(
            self.user)
        self.salt = b64enc(salt)

    def get_server_first(self):
        self._set_stage(ServerStage.get_server_first)
        self.auth_message, server_first = _get_server_first(
            self.nonce, self.salt, self.i, self.client_first_bare)
        return server_first

    def set_client_final(self, client_final):
        self._set_stage(ServerStage.set_client_final)
        self.server_signature = _set_client_final(
            self.m.hf, client_final, self.s_nonce, self.stored_key,
            self.server_key, self.auth_message)

    def get_server_final(self):
        self._set_stage(ServerStage.get_server_final)
        return _get_server_final(self.server_signature)


def _make_nonce():
    return str(uuid4()).replace('-', '')


def _make_auth_message(nonce, client_first_bare, server_first):
    msg = client_first_bare, server_first, 'c=' + b64enc(b'n,,'), 'r=' + nonce
    return ','.join(msg)


def _make_salted_password(hf, password, salt, iterations):
    return hi(hf, uenc(saslprep(password)), salt, iterations)


def _c_key_stored_key_s_key(hf, salted_password):
    client_key = hmac(hf, salted_password, b"Client Key")
    stored_key = h(hf, client_key)
    server_key = hmac(hf, salted_password, b"Server Key")

    return client_key, stored_key, server_key


def _check_client_key(hf, stored_key, auth_msg, proof):
    client_signature = hmac(hf, stored_key, auth_msg)
    client_key = xor(client_signature, b64dec(proof))
    key = h(hf, client_key)

    if key != stored_key:
        raise ScramException("The client keys don't match.")


def _parse_message(msg):
    return dict((e[0], e[2:]) for e in msg.split(',') if len(e) > 1)


def _get_client_first(username, c_nonce):
    bare = ','.join(('n=' + saslprep(username), 'r=' + c_nonce))
    return bare, 'n,,' + bare


def _set_client_first(client_first, s_nonce):
    msg = _parse_message(client_first)
    c_nonce = msg['r']
    nonce = c_nonce + s_nonce
    user = msg['n']
    client_first_bare = client_first[3:]

    return nonce, user, client_first_bare


def _get_server_first(nonce, salt, iterations, client_first_bare):
    sfirst = ','.join(('r=' + nonce, 's=' + salt, 'i=' + str(iterations)))
    auth_msg = _make_auth_message(nonce, client_first_bare, sfirst)
    return auth_msg, sfirst


def _set_server_first(server_first, c_nonce, client_first_bare):
    msg = _parse_message(server_first)
    nonce = msg['r']
    salt = msg['s']
    iterations = int(msg['i'])

    if not nonce.startswith(c_nonce):
        raise ScramException("Client nonce doesn't match.")

    auth_msg = _make_auth_message(nonce, client_first_bare, server_first)
    return auth_msg, nonce, salt, iterations


def _get_client_final(hf, password, salt_str, iterations, nonce, auth_msg_str):
    salt = b64dec(salt_str)
    salted_password = _make_salted_password(hf, password, salt, iterations)
    client_key, stored_key, server_key = _c_key_stored_key_s_key(
        hf, salted_password)

    auth_msg = uenc(auth_msg_str)

    client_signature = hmac(hf, stored_key, auth_msg)
    client_proof = xor(client_key, client_signature)
    server_signature = hmac(hf, server_key, auth_msg)

    msg = ['c=' + b64enc(b'n,,'), 'r=' + nonce, 'p=' + b64enc(client_proof)]
    return b64enc(server_signature), ','.join(msg)


def _set_client_final(
        hf, client_final, s_nonce, stored_key, server_key, auth_msg_str):
    auth_msg = uenc(auth_msg_str)

    msg = _parse_message(client_final)
    nonce = msg['r']
    proof = msg['p']

    if not nonce.endswith(s_nonce):
        raise ScramException("Server nonce doesn't match.")

    _check_client_key(hf, stored_key, auth_msg, proof)

    sig = hmac(hf, server_key, auth_msg)
    return b64enc(sig)


def _get_server_final(server_signature):
    return 'v=' + server_signature


def _set_server_final(message, server_signature):
    msg = _parse_message(message)
    if server_signature != msg['v']:
        raise ScramException("The server signature doesn't match.")


def saslprep(source):
    # mapping stage
    #   - map non-ascii spaces to U+0020 (stringprep C.1.2)
    #   - strip 'commonly mapped to nothing' chars (stringprep B.1)
    data = ''.join(
        ' ' if in_table_c12(c) else c for c in source if not in_table_b1(c))

    # normalize to KC form
    data = unicodedata.normalize('NFKC', data)
    if not data:
        return ''

    # check for invalid bi-directional strings.
    # stringprep requires the following:
    #   - chars in C.8 must be prohibited.
    #   - if any R/AL chars in string:
    #       - no L chars allowed in string
    #       - first and last must be R/AL chars
    # this checks if start/end are R/AL chars. if so, prohibited loop
    # will forbid all L chars. if not, prohibited loop will forbid all
    # R/AL chars instead. in both cases, prohibited loop takes care of C.8.
    is_ral_char = in_table_d1
    if is_ral_char(data[0]):
        if not is_ral_char(data[-1]):
            raise ValueError("malformed bidi sequence")
        # forbid L chars within R/AL sequence.
        is_forbidden_bidi_char = in_table_d2
    else:
        # forbid R/AL chars if start not setup correctly; L chars allowed.
        is_forbidden_bidi_char = is_ral_char

    # check for prohibited output
    # stringprep tables A.1, B.1, C.1.2, C.2 - C.9
    for c in data:
        # check for chars mapping stage should have removed
        assert not in_table_b1(c), "failed to strip B.1 in mapping stage"
        assert not in_table_c12(c), "failed to replace C.1.2 in mapping stage"

        # check for forbidden chars
        for f, msg in (
                (in_table_a1, "unassigned code points forbidden"),
                (in_table_c21_c22, "control characters forbidden"),
                (in_table_c3, "private use characters forbidden"),
                (in_table_c4, "non-char code points forbidden"),
                (in_table_c5, "surrogate codes forbidden"),
                (in_table_c6, "non-plaintext chars forbidden"),
                (in_table_c7, "non-canonical chars forbidden"),
                (in_table_c8, "display-modifying/deprecated chars forbidden"),
                (in_table_c9, "tagged characters forbidden"),
                (is_forbidden_bidi_char, "forbidden bidi character")):
            if f(c):
                raise ValueError(msg)

    return data
