# -*- coding: utf-8 -*-
import re


class GetKeys(object):

    plg_type = 'all'

    def txt(self, type, plugins=[]):
        # sort plugins!
        self.plg_type = type
        plugins.sort(key=lambda x: x.__class__.__name__)
        # create template
        template_data = self._get_all('keys_and_queries', plugins)   # get data from all plugins
        return template_data

    def _get_all(self, keys_and_queries='keys_and_queries', plugins=[]):
        result = ''
        for plugin in plugins:
            if plugin.AgentPluginType == self.plg_type or self.plg_type == 'all':
                # check if THIS plugin is required for current input option
                row = getattr(plugin, keys_and_queries)(self)  # get keys_and_queries of this particular plugin
                if row is None:
                    continue
                if plugin.AgentPluginType == 'pg':
                    row = re.sub(r"\,\"", ",/opt/pgpro/std-10/bin/psql -qAt -p 5433 -U postgres -d postgres -c \"", row)
                    row = re.sub(r"\,-f", ",/opt/pgpro/std-10/bin/psql -qAt -p 5433 -U postgres -d postgres -c -f", row)
                result += row
        return result

    def key_and_query(self, args=[]):
        result = ""
        for one in args:
            one = re.sub(r"\[\]", "",  one)  # for [] case
            #print(one)
            if re.search(r"[^*]\]", one):
                one = re.sub(r"\]", "", one)
            #print(one)
            if re.search(r"\[[^*]", one):
                one = re.sub(r"\[", ".", one)  # for zabbix-agent type of key representation
            #print(one)
            # add parameters for psql to string
            result += 'UserParameter={0}\n'.format(one)  # lose brackets
        return result
