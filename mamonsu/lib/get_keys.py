# -*- coding: utf-8 -*-
import re


class GetKeys(object):

    # mainTemplate = "{keys_and_queries}"
    plg_type = 'all'

    def txt(self, type, plugins=[]):
        # sort plugins!
        self.plg_type = type
        plugins.sort(key=lambda x: x.__class__.__name__)
        # create template
        #template_data['items'] = self._get_all('items', plugins)
        #template_data['keys_and_queries'] = self._get_all('keys_and_queries', plugins)
        # return self.mainTemplate.format(**template_data)
        template_data = self._get_all('keys_and_queries', plugins)   # get data from all plugins
        return template_data

    def _get_all(self, keys_and_queries='keys_and_queries', plugins=[]):
        result = ''
        for plugin in plugins:
            print("plugin.AgentPluginType",plugin.AgentPluginType)
            print("self.plg_type",self.plg_type)
            if plugin.AgentPluginType == self.plg_type or self.plg_type =='all': # check if plugin is required for current input option
                row = getattr(plugin, keys_and_queries)(self)  # get Items of this particular plugin
                if row is None:
                    continue
                if plugin.AgentPluginType == 'pg':
                    row  = re.sub(r"\,\"", ",/opt/pgpro/std-10/bin/psql -qAt -p 5433 -U postgres -d postgres -c \"",
                                     row )
                print("result", row )
                print("\n")
                result += row
        return result

    def key_and_query(self, args=[]):
        result = ""
        for one in args:
            one = re.sub(r"[\\]", "", str(one))  # convert list into string and replace '\' with empty symbol
            one = re.sub(r"\[\]", "",  one)  # for [] case
            one = re.sub(r"\]", "", one)
            one = re.sub(r"\[", ".", one)  # for zabbix-agent type of key representation
            # add parameters for psql to string
            result += 'UserParameter={0}\n'.format(one[2:-1])  # lose brackets
       # result = re.sub('set\(\[', '', quiry)
       # result = re.sub(r"[\\]", "", result)
       # result = re.sub(r"\]\)", "", result)
       # result = result[1:-1]
        return result
