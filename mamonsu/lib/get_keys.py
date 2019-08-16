# -*- coding: utf-8 -*-
import logging


class GetKeys(object):
    plg_type = 'all'

    def txt(self, type, plugins=[]):
        # sort plugins!
        self.plg_type = type
        plugins.sort(key=lambda x: x.__class__.__name__)
        # create template
        template_data = self._get_all('keys_and_queries', plugins)  # get data from all plugins
        return template_data

    def _get_all(self, keys_and_queries, plugins=[]):
        result = ''
        # don't need keys for zabbix agent from these classes
        non_keys_classes = ('AgentApi', 'LogSender', 'ZbxSender')
        for plugin in plugins:
            if plugin.__class__.__name__ not in non_keys_classes:
                # check if THIS plugin is required for current input option
                if plugin.AgentPluginType == self.plg_type or self.plg_type == 'all':
                    row = getattr(plugin, keys_and_queries)(self)  # get keys_and_queries of this particular plugin
                    if row is None:
                        logging.info('No keys for plugin {0}'.format(plugin.__class__.__name__))
                        continue
                    result += row
        return result

    def key_and_query(self, args=[]):
        result = ""
        for one in args:
            result += 'UserParameter={0}\n'.format(one)
        return result
