# -*- coding: utf-8 -*-

import os
import logging

import mamonsu.lib.platform as platform
from mamonsu.tools.sysinfo.linux import SysInfoLinux


class AutoTuneSystem(SysInfoLinux):

    _SYSCTL_FILE = '/etc/sysctl.conf'
    _SYSCTL_MAGIC_LINE = "#### mamonsu auto tune ####\n"

    def __init__(self, args):

        sudo = False if (args.disable_sudo is False) else True
        super(AutoTuneSystem, self).__init__(use_sudo=sudo)

        self.args = args
        self._sysctl_data = []

        self._dirty()
        self._min_free()

        self._write_sysctl_file()

    # dirty bytes
    def _dirty(self):
        if not platform.LINUX:
            return
        total = self.meminfo['_TOTAL']
        # if total < 1Gb, dont tune dirty bytes
        if total > 1024 * 1024 * 1024:
            self._add_sysctl('vm.dirty_background_bytes', 32 * 1024 * 1024)
            self._add_sysctl('vm.dirty_bytes',            64 * 1024 * 1024)

    # defragment
    def _min_free(self):
        if not platform.LINUX:
            return
        total = self.meminfo['_TOTAL']
        self._add_sysctl('vm.min_free_kbytes', int(5*total/(100*1024)))

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
            if self.args.dry_run:
                logging.info('dry run (write sysctl vars: {0}):\n{1}'.format(
                    self._SYSCTL_FILE, ''.join(all_sysctl)))
                return
            with open(self._SYSCTL_FILE, 'w') as f:
                f.write(''.join(all_sysctl))
                f.flush()
        except Exception as e:
            logging.error('Write to sysctl error: {0}'.format(e))
