# -*- coding: utf-8 -*-
import sys
from mamonsu.lib.plugin import Plugin

from mamonsu.lib.const import API
import mamonsu.lib.platform as platform

if platform.PY3:
    from urllib.parse import urlparse as parse
    from urllib.parse import parse_qs
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import urllib.request as urllib2
else:
    from urlparse import urlparse as parse
    from urlparse import parse_qs
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    import urllib2


class AgentApi(Plugin):

    def __init__(self, config):
        super(AgentApi, self).__init__(config)
        self._enabled = config.fetch('agent', 'enabled', bool)
        self.host = config.fetch('agent', 'host')
        self.port = config.fetch('agent', 'port', int)

    def run(self, _=None):
        self.log.info('Starting at http://{0}:{1}'.format(
            self.host, self.port))
        self.server = AgentApiHttpServer(self)


class AgentApiHttpServer:

    def __init__(self, config):
        def handler(*args):
            AgentApiHandler(config, *args)
        server = HTTPServer((config.host, config.port), handler)
        server.serve_forever()


class AgentApiHandler(BaseHTTPRequestHandler):

    def __init__(self, config, *args):
        self.sender = config.sender
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        req = parse(self.path)
        if req.path in '/version':
            self.wfile.write(API.VERSION)
        elif req.path in API.METRIC_GET_URLS:
            query = parse_qs(req.query)
            key, host = None, None
            if 'key' in query:
                key = query['key'][0]
            if 'host' in query:
                host = query['host'][0]
            resp = self.sender.get_metric(key, host)
            if resp[0] is not None:
                self.wfile.write('{0}\t{1}\t{2}'.format(
                    key, resp[0], resp[1]))
            else:
                self.wfile.write(API.METRIC_NOT_FOUND)
        elif req.path in API.METRIC_LIST_URLS:
            query, host, result = parse_qs(req.query), None, ''
            if 'host' in query:
                host = query['host'][0]
            for val in self.sender.list_metrics(host):
                result += '{0}\t{1}\t{2}\n'.format(
                    val[0], val[1][0], val[1][1])
            self.wfile.write(result)
        else:
            # unknown path
            self.wfile.write(API.UNKNOWN_VERSION)


def _print_response(cfg, key=None, version=False):
    host = cfg.fetch('agent', 'host')
    port = cfg.fetch('agent', 'port', int)
    if version:
        url = 'http://{0}:{1}/version'.format(host, port)
    elif key is None:
        url = 'http://{0}:{1}/list'.format(host, port)
    else:
        url = 'http://{0}:{1}/get?key={2}'.format(host, port, key)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    if not response.code == 200:
        sys.stderr.write('Bad response code: {0}\n'.format(response.code))
        sys.exit(8)
    else:
        body = response.read()
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


def get_api_version(cfg):
    _print_response(cfg, version=True)


def get_api_metric(cfg, key):
    _print_response(cfg, key)


def get_api_metric_list(cfg):
    _print_response(cfg)
