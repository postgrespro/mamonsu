from mamonsu.lib.plugin import Plugin
from .pool import Pooler


class PgsqlPlugin(Plugin):

    _child = False

    def __init__(self, config):
        super(PgsqlPlugin, self).__init__(config)
        self._enabled = config.fetch('postgres', 'enabled', bool)
        self._ext_installed, self._ext_check_count = False, None

    @classmethod
    def get_childs(self):
        # return all childs
        return self.__subclasses__()

    def extension_installed(self, ext, db=None):

        def check(self, ext):
            self._ext_installed = Pooler.extension_installed(ext, db)
            self._ext_check_count = 0
            if not self._ext_installed:
                self.log.error("Extension '{0}' is not installed".format(ext))

        if self._ext_check_count is None:
            # first check
            check(self, ext)
        elif self._ext_check_count > 5:
            # try to RE-check
            check(self, ext)
        self._ext_check_count += 1

        return self._ext_installed
