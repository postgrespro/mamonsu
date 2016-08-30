# -*- coding: utf-8 -*-
import sys

from mamonsu.lib.const import API
import mamonsu.lib.platform as platform

if platform.PY3:
    import urllib.request as urllib2
else:
    import urllib2


def run_agent(cfg):

    def _print_help():
        msg = """mamonsu agent [version|metric-get <metric key>|metric-list]\n"""
        sys.stderr.write(msg)
        sys.exit(7)

    commands = cfg.commands
    commands.remove('agent')
    if len(commands) == 0:
        return _print_help()

    host = cfg.fetch('agent', 'host')
    port = cfg.fetch('agent', 'port', int)
    url, key = None, None

    if commands[0] == 'version':
        url = 'http://{0}:{1}/version'.format(host, port)
    elif commands[0] == 'metric-list':
        url = 'http://{0}:{1}/list'.format(host, port)
    elif commands[0] == 'metric-get':
        if not len(commands) == 2:
            return _print_help()
        key = commands[1]
        url = 'http://{0}:{1}/get?key={2}'.format(host, port, key)
    else:
        _print_help()

    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
    except Exception as e:
        sys.stderr.write('Open url: {0}, error: {1}\n'.format(
            url, e))
        sys.exit(9)

    if not response.code == 200:
        sys.stderr.write('Bad response from url {0}, code: {1}\n'.format(
            url,
            response.code))
        sys.exit(8)
    else:
        try:
            body = response.read()
        except Exception as e:
            sys.stderr.write('Read url: {0}, error: {1}\n'.format(
                url, e))
            sys.exit(9)
        if body == API.UNKNOWN_VERSION:
            sys.stderr.write('Unknown API version\n')
            sys.exit(9)
        elif body == API.METRIC_NOT_FOUND and key is not None:
            sys.stderr.write('Metric \'{0}\' not found\n'.format(key))
            sys.exit(9)
        elif body == API.METRIC_NOT_FOUND and key is None:
            sys.stderr.write('Unknown API version\n')
            sys.exit(9)
        else:
            print(body)
