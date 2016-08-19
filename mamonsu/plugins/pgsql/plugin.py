from mamonsu.lib.plugin import Plugin


class PgsqlPlugin(Plugin):

    _child = False

    def __init__(self, config):
        super(PgsqlPlugin, self).__init__(config)
        self._enabled = config.fetch('postgres', 'enabled', bool)

    @classmethod
    def childs(self):
        # return all childs
        return self.__subclasses__()
