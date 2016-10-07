from mamonsu.lib.plugin import Plugin


class SystemPlugin(Plugin):

    is_child = False

    def __init__(self, config):
        super(SystemPlugin, self).__init__(config)
        self._enabled = config.fetch('system', 'enabled', bool)

    @classmethod
    def only_child_subclasses(self):
        # return all childs
        return self.__subclasses__()
