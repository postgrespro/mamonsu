from collections import namedtuple

from mamonsu import __version__


class _template(object):
    # item delta
    _delta = namedtuple(
        'DELTA', ['as_is', 'speed_per_second', 'simple_change'])
    DELTA = _delta(0, 1, 2)
    # grap type
    _graph_type = namedtuple(
        'graph_type', ['normal', 'stacked', 'pie', 'exploded'])
    GRAPH_TYPE = _graph_type(0, 1, 2, 3)
    # value_type
    _value_type = namedtuple(
        'value_type',
        ['numeric_float', 'character', 'log',
            'numeric_unsigned', 'text'])
    VALUE_TYPE = _value_type(0, 1, 2, 3, 4)
    # item unit
    _item_type = namedtuple(
        'item_type', ['none', 'bytes', 's', 'ms', 'uptime', 'unixtime', 'percent'])
    UNITS = _item_type(None, 'b', 's', 'ms', 'uptime', 'unixtime', '%')
    # type of information
    _type = namedtuple(
        'type', ['ZABBIX_PASSIVE', 'TRAP', 'SIMPLE', 'INTERNAL', 'ZABBIX_ACTIVE',
                 'EXTERNAL', 'ODBC', 'IPMI', 'SSH', 'TELNET', 'CALCULATED', 'JMX',
                 'SNMP_TRAP', 'DEPENDENT', 'HTTP_AGENT', 'SNMP_AGENT', 'ITEM_TYPE_SCRIPT'])
    TYPE = _type(0, 2, 3, 5, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21)


class _api(object):

    UNKNOWN_VERSION = b'UNKNOWN_API_VERSION\n'

    METRIC_NOT_FOUND = b'METRIC_NOT_FOUND\n'

    VERSION = bytearray('{0}'.format(__version__), 'utf-8')

    METRIC_LIST_URLS = ['/list', '/list/']
    METRIC_GET_URLS = ['/get', '/get/']


Template = _template()
API = _api()
