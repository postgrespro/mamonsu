from collections import namedtuple


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
        'item_type', ['none', 'bytes', 'ms', 'uptime', 'percent'])
    UNITS = _item_type(None, 'b', 'ms', 'uptime', '%')


Template = _template()
