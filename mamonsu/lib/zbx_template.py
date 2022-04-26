# -*- coding: utf-8 -*-
import re
import mamonsu.lib.platform as platform
from mamonsu.lib.const import Template
from mamonsu.lib.plugin import Plugin


class ZbxTemplate(object):
    plg_type = 'all'
    mainTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<zabbix_export>
    <version>3.0</version>
    <groups>
        <group>
            <name>Templates</name>
        </group>
    </groups>
    <templates>
        <template>
            <template>{template}</template>
            <name>{template}</name>
            <description/>
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
            <screens>{screens}</screens>
            <macros>{macros}</macros>
        </template>
    </templates>
    <triggers>{triggers}</triggers>
    <graphs>{graphs}</graphs>
</zabbix_export>"""

    #

    macro_defaults = [
        ('macro', None), ('value', None)
    ]

    item_defaults = [
        ('name', None), ('type', 2), ('snmp_community', None),
        ('multiplier', 0), ('inventory_link', 0),
        ('key', None), ('snmp_oid', None), ('history', 7),
        ('trends', 365), ('status', 0), ('delay', 60),
        ('value_type', Template.VALUE_TYPE.numeric_float),
        ('allowed_hosts', None), ('valuemap', None),
        ('units', Template.UNITS.none), ('delta', Template.DELTA.as_is),
        ('snmpv3_contextname', None), ('snmpv3_securityname', None),
        ('snmpv3_securitylevel', 0), ('snmpv3_authprotocol', 0),
        ('snmpv3_authpassphrase', None), ('snmpv3_privprotocol', 0),
        ('snmpv3_privpassphrase', None), ('logtimefmt', None), ('formula', 1),
        ('delay_flex', None), ('params', None),
        ('ipmi_sensor', None), ('data_type', 0), ('authtype', 0),
        ('username', None), ('password', None), ('publickey', None),
        ('privatekey', None), ('port', None), ('description', None)
    ]

    item_prototype_defaults = [
        ('application_prototypes', None)
    ]

    trigger_defaults = [
        ('expression', None), ('name', None), ('url', None),
        ('status', 0), ('priority', 3), ('description', None),
        ('type', 0), ('dependencies', None)
    ]

    trigger_discovery_defaults = [
        ('expression', None), ('name', None), ('url', None),
        ('status', 0), ('priority', 3), ('description', None),
        ('type', 0)
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
        ('sortorder', None), ('drawtype', 0),
        ('color', '578159'), ('yaxisside', 0),
        ('calc_fnc', 2), ('type', Template.GRAPH_TYPE.normal)
    ]

    condition_defaults = [
        ('macro', None), ('value', 0),
        ('operator', None),
        ('formulaid', None)
    ]

    discovery_defaults = [
        ('name', None), ('type', 2), ('snmp_community', None),
        ('snmp_oid', None), ('delay', 60), ('status', 0),
        ('allowed_hosts', None), ('snmpv3_contextname', None),
        ('snmpv3_securityname', None), ('snmpv3_securitylevel', 0),
        ('snmpv3_authprotocol', 0), ('snmpv3_authpassphrase', None),
        ('snmpv3_privprotocol', 0), ('snmpv3_privpassphrase', None),
        ('delay_flex', None), ('params', None),
        ('ipmi_sensor', None), ('authtype', 0),
        ('username', None), ('password', None), ('publickey', None),
        ('privatekey', None), ('port', None), ('lifetime', 7),
        ('description', None), ('key', None), ('host_prototypes', None)
    ]

    dashboard_defaults = [
        ('display_period', 60)
    ]

    screen_graph_defaults = [
        ('colspan', 1),
        ('rowspan', 1),
        ('elements', 0),
        ('valign', 1),
        ('halign', 0),
        ('style', 0),
        ('dynamic', 0),
        ('sort_triggers', 0),
        ('max_columns', 3),
        ('url', ''),
        ('application', ''),
    ]

    dashboard_page_overview = {'name': 'Overview', 'hsize': 2, 'vsize': 5}
    dashboard_page_instance = {'name': 'PostgreSQL Instance', 'hsize': 2, 'vsize': 5}
    dashboard_page_wal = {'name': 'PostgreSQL WAL', 'hsize': 2, 'vsize': 5}
    dashboard_page_locks = {'name': 'PostgreSQL Locks', 'hsize': 3, 'vsize': 5}
    dashboard_page_transactions = {'name': 'PostgreSQL Transactions', 'hsize': 2, 'vsize': 5}
    dashboard_page_system_linux = {'name': 'System (Linux)', 'hsize': 2, 'vsize': 5}
    dashboard_page_system_windows = {'name': 'System (Windows)', 'hsize': 2, 'vsize': 5}

    dashboard_pages = [dashboard_page_overview,
                       dashboard_page_instance,
                       dashboard_page_wal,
                       dashboard_page_locks,
                       dashboard_page_transactions]
    if platform.UNIX:
        dashboard_pages.append(dashboard_page_system_linux)
    if platform.WINDOWS:
        dashboard_pages.append(dashboard_page_system_windows)

    dashboard_widget_size_large = {'width': 500, 'height': 250}
    dashboard_widget_size_medium = {'width': 500, 'height': 150}
    dashboard_widget_size_small = {'width': 330, 'height': 100}

    def __init__(self, name, app):
        self.Application = app
        self.Template = name

    def turn_agent_type(self, xml):
        # turn item into zabbix agent type
        xml = re.sub(r"<type>2", "<type>0", xml)
        return xml

    def xml(self, plg_type, plugins=None):
        # sort plugins!
        if plugins is None:
            plugins = []
        plugins.sort(key=lambda x: x.__class__.__name__)
        self.plg_type = plg_type
        # create template
        template_data = {'template': self.Template, 'application': self.Application}
        if Plugin.Type == 'agent':
            template_data['macros'] = self._macro()
        else:
            template_data['macros'] = ""
        template_data['triggers'] = self._get_all('triggers', plugins)
        template_data['items'] = self._get_all('items', plugins)
        template_data['graphs'] = self._get_all('graphs', plugins)
        template_data['discovery_rules'] = self._get_all('discovery_rules', plugins)
        template_data['screens'] = self.screen(plugins)
        output_xml = self.mainTemplate.format(**template_data)
        if Plugin.Type == 'agent':
            output_xml = ZbxTemplate.turn_agent_type(self, output_xml)
        return output_xml

    def _get_all(self, items='items', plugins=None, dashboard=False):
        if plugins is None:
            plugins = []
        result = ''
        dashboard_widgets = []
        if not dashboard:
            for plugin in plugins:
                if plugin.AgentPluginType == self.plg_type or self.plg_type == 'all':
                    row = getattr(plugin, items)(self, dashboard=False)  # get Items of this particular plugin
                    if row is None:
                        continue
                    result += row
            return result
        else:
            for plugin in plugins:
                if plugin.AgentPluginType == self.plg_type or self.plg_type == 'all':
                    row = getattr(plugin, items)(self, dashboard=True)  # get Items of this particular plugin
                    if row is None:
                        continue
                    dashboard_widgets.append(row)
            return dashboard_widgets

    # methods for Dashboard creating
    # Dashboards replaced screens and slideshows in Zabbix 5.4+, but since 5.4 there is one tricky required parameter - element uuid
    # def widgets(self, page=None, plugins=None, xml_key='widget'):
    #     if page is None:
    #         page = ''
    #     if plugins is None:
    #         plugins = []
    #     graphs = self._get_all('graphs', plugins, dashboard=True)
    #     result_graphs = ''
    #     for graph in graphs:
    #         if 'dashboard' in graph and graph['dashboard']['page'] == page:
    #             result_graphs += ('<{3}><type>GRAPH_CLASSIC</type><name>{0}</name><width>{1}</width>' +
    #                              '<height>{2}</height><fields><field><type>GRAPH</type><value>' +
    #                              '<name>{0}</name></value></field></fields></{3}>').format(graph['dashboard']['name'],
    #                                                                                       graph['dashboard']['size']['width'],
    #                                                                                       graph['dashboard']['size']['height'],
    #                                                                                       xml_key)
    #     return '<{1}s>{0}</{1}s>'.format(result_graphs,
    #                                      xml_key)
    #
    # def pages(self, args=None, plugins=None, xml_key='page'):
    #     if args is None:
    #         args = {}
    #     if plugins is None:
    #         plugins = []
    #     result = ''
    #     for page in args['pages']:
    #         result += '<{2}><name>{0}</name>{1}</{2}>'.format(page,
    #                                                           self.widgets(page, plugins),
    #                                                           xml_key)
    #     return '<{1}s>{0}</{1}s>'.format(result,
    #                                      xml_key)
    #
    # def dashboard(self, plugins=None, xml_key='dashboard'):
    #     if plugins is None:
    #         plugins = []
    #     return '<{3}><name>{0}</name>{1}{2}</{3}>'.format(self.Template + ' Dashboard',
    #                                                       self._format_args(self.dashboard_defaults, {}),
    #                                                       self.pages(self.dashboard_pages, plugins),
    #                                                       xml_key)

    def screen_items(self, page, plugins=None, xml_key='screen_item'):
        if plugins is None:
            plugins = []
        # indices = zabbix screen item type
        # 0 = graph
        # 1 = simple graph (from item)
        dashboard_widgets = sorted([(0, widget) for sublist in self._get_all('graphs', plugins, dashboard=True)
                                    for widget in sublist] +
                                   [(1, widget) for sublist in self._get_all('items', plugins, dashboard=True)
                                    for widget in sublist], key=lambda k: k[1]['dashboard']['position'])
        # page contains amount of columns (hsize) and rows (vsize)
        # 'x', 'y' are screen tags designated screen element left upper corner location
        # to generate proper grid it is necessary to shift x up to hsize with a step=1, then zeroes it and starts again
        # and shift y with step=1 every time when x was zeroed
        x = 0
        y = 0
        result = ''
        for resourcetype, graph in dashboard_widgets:
            if 'dashboard' in graph and graph['dashboard']['page'] == page['name']:
                result += ('<{5}><resourcetype>{8}</resourcetype>' +
                           '<width>{2}</width><height>{3}</height><x>{6}</x><y>{7}</y>{0}' +
                           '<resource><{9}>{1}</{9}><host>{4}</host></resource>' +
                           '</{5}>').format(self._format_args(self.screen_graph_defaults, {}),
                                            graph['dashboard']['name'],
                                            graph['dashboard']['size']['width'],
                                            graph['dashboard']['size']['height'],
                                            self.Template,
                                            xml_key,
                                            x,
                                            y,
                                            resourcetype,
                                            'name' if resourcetype == 0 else 'key')
                x = (x + 1) % page['hsize']
                if x == 0:
                    y += 1
        return '<{1}s>{0}</{1}s>'.format(result,
                                         xml_key)

    def screen(self, plugins=None, xml_key='screen'):
        if plugins is None:
            plugins = []
        result = ''
        for page in self.dashboard_pages:
            result += ('<{4}><name>{0}</name><hsize>{1}</hsize><vsize>' +
                      '{2}</vsize>{3}</{4}>').format('Mamonsu ' + page['name'],
                                                    page['hsize'],
                                                    page['vsize'],
                                                    self.screen_items(page, plugins),
                                                    xml_key)
        return result

    def _macro(self, xml_key='macro'):
        result = ''
        value = {'value': '-qAt -p 5433 -U postgres ', 'macro': "{$PG_CONNINFO}"}
        result += '<{1}>{0}</{1}>'.format(self._format_args(self.macro_defaults, value), xml_key)
        value = {'value': '/opt/pgpro/std-10/bin/psql', 'macro': "{$PG_PATH}"}
        result += '<{1}>{0}</{1}>'.format(self._format_args(self.macro_defaults, value), xml_key)
        return result

    def item(self, args=None, xml_key='item', prototype=False):
        if args is None:
            args = {}
        return '<{2}>{0}{1}</{2}>'.format(
            self._format_args(self.item_defaults if not prototype else self.item_defaults + self.item_prototype_defaults, args),
            self._application(), xml_key)

    def trigger(self, args=None, xml_key='trigger', defaults=None):
        if args is None:
            args = {}
        if defaults is None:
            defaults = self.trigger_defaults
        try:
            expression = args['expression']
        except KeyError:
            raise LookupError(
                'Miss expression in trigger: {0}.'.format(args))
        args['expression'] = expression.replace('#TEMPLATE', self.Template)
        return '<{1}>{0}</{1}>'.format(
            self._format_args(defaults, args),
            xml_key)

    def graph(self, args=None, xml_key='graph'):
        if args is None:
            args = {}
        try:
            items = args['items']
        except KeyError:
            raise LookupError(
                'Miss item in graph: {0}.'.format(args))
        graph_items = ''
        for idx, item in enumerate(items):
            try:
                key = item['key']
            except KeyError:
                raise LookupError(
                    'Missed key in graph item: {0}.'.format(item))
            if 'sortorder' not in item:
                item['sortorder'] = idx
            row = '<graph_item>{0}<item><host>{1}'
            row += '</host><key>{2}</key></item></graph_item>'
            graph_items += row.format(
                self._format_args(self.graph_items_defaults, item),
                self.Template, key)
        result = '<{2}>{0}<graph_items>{1}</graph_items></{2}>'
        return result.format(
            self._format_args(self.graph_values_defaults, args),
            graph_items, xml_key)

    # condition for template creation for zabbix version 4.4
    def condition(self, args=None, xml_key='condition'):
        if args is None:
            args = {}
        try:
            conditions = args['condition']
        except KeyError:
            raise LookupError(
                'Miss item in conditions: {0}.'.format(args))
        res = ''
        for idx, item in enumerate(conditions):
            res += '<{1}>{0}</{1}>'.format(
                self._format_args(self.condition_defaults, item),
                xml_key)
        res = '<conditions>' + res + '</conditions>' + '<formula/><evaltype>0</evaltype>'

        return res

    def discovery_rule(self, rule=None, conditions=None, items=None, triggers=None, graphs=None):
        if rule is None:
            rule = {}
        if conditions is None:
            conditions = []
        if items is None:
            items = []
        if triggers is None:
            triggers = []
        if graphs is None:
            graphs = []
        result_items = '<item_prototypes>'
        for item in items:
            result_items += self.item(item, xml_key='item_prototype', prototype=True)
        result_items += '</item_prototypes>'

        result_triggers = '<trigger_prototypes>'
        for trigger in triggers:
            result_triggers += self.trigger(
                trigger, xml_key='trigger_prototype',
                defaults=self.trigger_discovery_defaults)
        result_triggers += '</trigger_prototypes>'

        result_graphs = '<graph_prototypes>'
        for graph in graphs:
            result_graphs += self.graph(
                graph, xml_key='graph_prototype')
        result_graphs += '</graph_prototypes>'

        if len(conditions) > 0:
            result_conditions = '<filter>'
            for condition in conditions:
                result_conditions += self.condition(
                    condition, xml_key='condition')
            result_conditions += '</filter>'
        else:
            result = '<discovery_rule>{0}{1}{2}{3}</discovery_rule>'
            if ('filter', None) not in self.discovery_defaults:
                self.discovery_defaults.append(('filter', None))
            return result.format(
                self._format_args(self.discovery_defaults, rule),
                result_items, result_triggers, result_graphs)

        result = '<discovery_rule>{0}{1}{2}{3}{4}</discovery_rule>'
        return result.format(
            self._format_args(self.discovery_defaults, rule),
            result_conditions, result_items, result_triggers, result_graphs)

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
                row = '<{0}>{1}</{0}>'.format(key, pair[1]) if pair[1] else '<{0}/>'.format(key)
            else:
                row = '<{0}>{1}</{0}>'.format(key, val)
            result += row

        return result
