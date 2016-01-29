import datetime


class ZbxTemplate(object):

    mainTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<zabbix_export>
<version>2.0</version>
    <date>{date}</date>
    <groups>
        <group>
            <name>Templates</name>
        </group>
    </groups>
    <templates>
        <template>
            <template>{template}</template>
            <name>{template}</name>
            <groups>
                <group>
                    <name>Templates</name>
                </group>
            </groups>
            <applications>
                <application>
                    <name>{application}</name>
                </application>
            </applications>
            <items>{items}</items>
            <discovery_rules>{discovery_rules}</discovery_rules>
            <macros>{macros}</macros>
        </template>
    </templates>
    <triggers>{triggers}</triggers>
    <graphs>{graphs}</graphs>
</zabbix_export>"""

    item_defaults = [
        ('name', None), ('type', 7), ('snmp_community', None),
        ('key', None), ('snmp_oid', None), ('delay', 60),
        ('history', 7), ('trends', 365), ('status', 0),
        ('value_type', 0), ('allowed_hosts', None), ('valuemap', None),
        ('units', None), ('delta', 0), ('snmpv3_contextname', None),
        ('snmpv3_securityname', None), ('snmpv3_securitylevel', 0),
        ('snmpv3_authprotocol', 0), ('snmpv3_authpassphrase', None),
        ('snmpv3_privprotocol', 0), ('snmpv3_privpassphrase', None),
        ('formula', 1), ('delay_flex', None), ('params', None),
        ('ipmi_sensor', None), ('data_type', 0), ('authtype', 0),
        ('username', None), ('password', None), ('publickey', None),
        ('privatekey', None), ('port', None), ('description', None)
    ]

    trigger_defaults = [
        ('expression', None), ('name', None), ('url', None),
        ('status', 0), ('priority', 3), ('description', None),
        ('type', 0), ('dependencies', None)
    ]

    graph_values_defaults = [
        ('name', None), ('width', 900), ('height', 200),
        ('yaxismin', 0.0000), ('yaxismax', 100.0), ('show_work_period', 1),
        ('show_triggers', 1), ('type', 0), ('show_legend', 1),
        ('show_3d', 0), ('percent_left', 0.0), ('percent_right', 0.0),
        ('ymin_type_1', 0), ('ymax_type_1', 0), ('ymin_item_1', 0),
        ('ymax_item_1', 0)
    ]

    graph_items_defaults = [
        ('sortorder', 0), ('drawtype', 0), ('color', '00CC00'),
        ('yaxisside', 0), ('calc_fnc', 2), ('type', 0)
    ]

    discovery_defaults = [
        ('name', None), ('type', 7), ('snmp_community', None),
        ('snmp_oid', None), ('delay', 60), ('status', 0),
        ('allowed_hosts', None), ('snmpv3_contextname', None),
        ('snmpv3_securityname', None), ('snmpv3_securitylevel', 0),
        ('snmpv3_authprotocol', 0), ('snmpv3_authpassphrase', None),
        ('snmpv3_privprotocol', 0), ('snmpv3_privpassphrase', None),
        ('delay_flex', None), ('params', None), ('filter', None),
        ('ipmi_sensor', None), ('data_type', 0), ('authtype', 0),
        ('username', None), ('password', None), ('publickey', None),
        ('privatekey', None), ('port', None), ('lifetime', 7),
        ('description', None), ('key', None)
    ]

    def __init__(self, name, app):
        self.Application = app
        self.Template = name

    def xml(self, plugins=[]):
        template_data = {'date': datetime.datetime.now().isoformat()}
        template_data['template'] = self.Template
        template_data['application'] = self.Application
        template_data['items'] = self._get_all('items', plugins)
        template_data['macros'] = ''
        template_data['triggers'] = self._get_all('triggers', plugins)
        template_data['graphs'] = self._get_all('graphs', plugins)
        template_data['discovery_rules'] = self._get_all(
            'discovery_rules', plugins)
        return self.mainTemplate.format(**template_data)

    def _get_all(self, items='items', plugins=[]):
        result = ''
        for plugin in plugins:
            row = getattr(plugin, items)(self)
            if row is None:
                continue
            result += row
        return result

    def item(self, args={}, xml_key='item'):
        return '<{2}>{0}{1}</{2}>'.format(
            self._format_args(self.item_defaults, args),
            self._application(),
            xml_key)

    def trigger(self, args={}, xml_key='trigger'):
        try:
            expression = args['expression']
        except KeyError:
            raise LookupError(
                'Miss expression in trigger: {0}.'.format(args))
        args['expression'] = expression.replace('#TEMPLATE', self.Template)
        return '<{1}>{0}</{1}>'.format(
            self._format_args(self.trigger_defaults, args),
            xml_key)

    def graph(self, args={}, xml_key='graph'):
        try:
            items = args['items']
        except KeyError:
            raise LookupError(
                'Miss item in graph: {0}.'.format(args))
        graph_items = ''
        for item in items:
            try:
                key = item['key']
            except KeyError:
                raise LookupError(
                    'Missed key in graph item: {0}.'.format(item))
            row = '<graph_item>{0}<item><host>{1}'
            row += '</host><key>{2}</key></item></graph_item>'
            graph_items += row.format(
                self._format_args(self.graph_items_defaults, item),
                self.Template, key)
        result = '<{2}>{0}<graph_items>{1}</graph_items></{2}>'
        return result.format(
            self._format_args(self.graph_values_defaults, args),
            graph_items, xml_key)

    def discovery_rule(self, rule={}, items=[], triggers=[], graphs=[]):

        result_items = '<item_prototypes>'
        for item in items:
            result_items += self.item(item, xml_key='item_prototype')
        result_items += '</item_prototypes>'

        result_triggers = '<trigger_prototypes>'
        for trigger in triggers:
            result_triggers += self.trigger(
                trigger, xml_key='trigger_prototype')
        result_triggers += '</trigger_prototypes>'

        result_graphs = '<graph_prototypes>'
        for graph in graphs:
            result_graphs += self.graph(
                graph, xml_key='graph_prototype')
        result_graphs += '</graph_prototypes>'

        result = '<discovery_rule>{0}{1}{2}{3}</discovery_rule>'
        return result.format(
            self._format_args(self.discovery_defaults, rule),
            result_items, result_triggers, result_graphs)

    def _application(self):
        result = '<applications><application><name>{0}'
        result += '</name></application></applications>'
        return result.format(self.Application)

    def _format_args(self, defaults, override):
        result = ''
        for pair in defaults:
            key = pair[0]
            try:
                val = override[key]
            except KeyError:
                val = pair[1]
            if val is None:
                row = '<{0}/>'.format(key)
            else:
                row = '<{0}>{1}</{0}>'.format(key, val)
            result += row
        return result
