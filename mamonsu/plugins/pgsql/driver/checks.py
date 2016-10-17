# -*- coding: utf-8 -*-

from .pg8000 import connect


def is_conn_to_db(host, db, port, user, paswd):
    host, unix_sock = host, None
    if host.startswith('/'):
        unix_sock, host = host, None
    try:
        conn = connect(
            user=user,
            password=paswd,
            unix_sock=unix_sock,
            host=host,
            port=port,
            database=db)
        cur = conn.cursor()
        cur.execute('select 1')
        cur.close()
    except:
        return False
    else:
        return True
