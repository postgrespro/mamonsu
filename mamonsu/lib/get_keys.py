# -*- coding: utf-8 -*-
import re


class GetKeys(object):

    mainTemplate = "{keys_and_queries}"

    # mainTemplate = "UserParameter={keys_and_queries}" # fix main template for zabbix-agent

    def txt(self, plugins=[]):
        # sort plugins!
        plugins.sort(key=lambda x: x.__class__.__name__)
        # create template
        template_data = {}
        #template_data['items'] = self._get_all('items', plugins)
        template_data['keys_and_queries'] = self._get_all('keys_and_queries', plugins)
        return self.mainTemplate.format(**template_data)

    def _get_all(self, keys_and_queries='keys_and_queries', plugins=[]):
        result = ''
        for plugin in plugins:
            row = getattr(plugin, keys_and_queries)(self)  # get Items of this particular plugin
            if row is None:
                continue
            result += row
        return result

    def key_and_query(self, args={}, xml_key='item'):
        quiry = '{0}'.format(args)
        result = re.sub('set\(\[', '', quiry)
        result = re.sub(r"[\\]", "", result)
        result = re.sub(r"\]\)", "", result)
        result = result[1:-1]
        return result


    def _format_args(self, defaults, override):   #fix for zabbix agent
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
