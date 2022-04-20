# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin, PluginDisableException
from .pool import Pooler
import subprocess


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

        def check(self, extension):
            self._ext_installed = Pooler.extension_installed(extension, db)
            self._ext_check_count = 0
            if not self._ext_installed and not silent:
                self.log.info("Extension '{0}' is not installed".format(extension))

        if self._ext_check_count is None:
            # first check
            check(self, ext)
        elif self._ext_check_count > 5:
            # try to RE-check
            check(self, ext)
        self._ext_check_count += 1

        return self._ext_installed

    def extension_schema(self, extension, db=None):
        return Pooler.extension_schema(extension, db)

    def disable_and_exit_if_extension_is_not_installed(self, ext, db=None):
        if not self.extension_installed(ext, db=db, silent=True):
            self.disable()
            raise PluginDisableException("""Disable plugin and exit, because '{0}' \
extension is not installed. Enable it in PostgreSQL instance: '{1}',
if needed and restart.""".format(ext, Pooler.connection_string(db)))

    def disable_and_exit_if_not_pgpro_ee(self, db=None):
        if not Pooler.is_pgpro_ee(db):
            self.disable()
            raise PluginDisableException("""Disable plugin and exit, because \
PostgresPro Enterprise Edition is not detected [instance: '{0}']
""".format(Pooler.connection_string(db)))

    def disable_and_exit_if_archive_mode_is_not_on(self, db=None):
        param = Pooler.get_sys_param('archive_mode', db=db)
        if param != 'on' and param != 'always':
            self.disable()
            raise PluginDisableException("""Disable plugin and exit, because '{0}' \
parameter is neither 'on' nor 'always'. Enable it "{1}" or "{2}" in PostgreSQL instance, \
if needed and restart.""".format('archive_mode', 'alter system set archive_mode = on;',
                                 'alter system set archive_mode = always;'))

    def disable_and_exit_if_not_superuser(self, db=None):
        if not Pooler.is_superuser():
            self.disable()
            raise PluginDisableException("""Disable plugin and exit, because \
you need superuser rights or bootstrap to run this plugin [instance: '{0}']
""".format(Pooler.connection_string(db)))
