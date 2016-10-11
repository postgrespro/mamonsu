from mamonsu.lib.plugin import Plugin, PluginExitException
from .pool import Pooler


class PgsqlPlugin(Plugin):

    is_child = False

    def __init__(self, config):
        super(PgsqlPlugin, self).__init__(config)
        self._enabled = config.fetch('postgres', 'enabled', bool)
        self._ext_installed, self._ext_check_count = False, None

    @classmethod
    def only_child_subclasses(self):
        # return all childs
        return self.__subclasses__()

    def extension_installed(self, ext, db=None, silent=False):

        def check(self, ext):
            self._ext_installed = Pooler.extension_installed(ext, db)
            self._ext_check_count = 0
            if not self._ext_installed and not silent:
                self.log.error("Extension '{0}' is not installed".format(ext))

        if self._ext_check_count is None:
            # first check
            check(self, ext)
        elif self._ext_check_count > 5:
            # try to RE-check
            check(self, ext)
        self._ext_check_count += 1

        return self._ext_installed

    def disable_and_exit_if_extension_is_not_installed(self, ext, db=None):
        if not self.extension_installed(ext, db=db, silent=True):
            self.disable()
            raise PluginExitException("""
Disable plugin and exit, because '{0}' \
extension is not installed. Enable it in PostgreSQL instance: '{1}', \
if needed and restart.""".format(ext, Pooler.connection_string(db)))
