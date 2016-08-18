# -*- coding: utf-8 -*-
import os
import logging

import mamonsu.lib.platform as platform


class SystemInfo(object):

    def get_memory_total(self):
        if platform.LINUX:
            return self._get_mem_total_linux()
        return 0

    def _get_mem_total_linux(self):
        if os.path.isfile('/proc/meminfo'):
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        data = line.split()
                        if not len(data) == 3:
                            continue
                        if data[0] == 'MemTotal:' and data[2] == 'kB':
                            return int(data[1]) * 1024
            except:
                logging.error('Can\'t read /proc/meminfo')
        return 0
