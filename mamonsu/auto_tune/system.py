# -*- coding: utf-8 -*-

import os
import logging

import mamonsu.lib.platform as platform
from mamonsu.auto_tune._info import SystemInfo


class AutoTuneSystem(object):

    _SYSCTL_FILE = '/tmp/sysctl.conf'
    _SYSCTL_MAGIC_LINE = "#### mamonsu auto tune ####\n"

    def __init__(self, args):
        self.sys_info = SystemInfo()
        self._sysctl_data = []
        self._dirty()
        self._min_free()
        self._write_sysctl_file()

    # dirty bytes
    def _dirty(self):

        if not platform.LINUX:
            return
        total = self.sys_info.get_memory_total()
        if total == 0:
            return

        # if total < 1Gb, dont tune dirty bytes
        if total < 1024 * 1024 * 1024:
            return

        self._add_sysctl('vm.dirty_background_bytes', 32 * 1024 * 1024)
        self._add_sysctl('vm.vm.dirty_bytes',         64 * 1024 * 1024)

    def _min_free(self):
        pass

    def _add_sysctl(self, key, value):
        self._sysctl_data.append("{0} = {1}\n".format(key, value))

    # write to sysctl
    def _write_sysctl_file(self):
        if not platform.LINUX:
            return
        if not os.path.isfile(self._SYSCTL_FILE):
            return
        try:
            all_sysctl = []
            with open(self._SYSCTL_FILE, 'r') as f:
                for line in f:
                    if self._SYSCTL_MAGIC_LINE == line:
                        break
                    all_sysctl.append(line)
            all_sysctl.append("\n{0}".format(self._SYSCTL_MAGIC_LINE))
            all_sysctl += self._sysctl_data
            with open(self._SYSCTL_FILE, 'w') as f:
                f.write(''.join(all_sysctl))
                f.flush()
        except Exception as e:
            logging.error("Write to sysctl error: {0}".format(e))
