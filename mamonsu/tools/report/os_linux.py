# -*- coding: utf-8 -*-

import time
import math
import sys
import logging

from mamonsu import __version__ as mamonsu_version
from mamonsu.tools.sysinfo.linux import SysInfoLinux


class SystemInfo(SysInfoLinux):

    def __init__(self, args):
        sudo = False if (args.disable_sudo is False) else True
        super(SystemInfo, self).__init__(use_sudo=sudo)
        self.args = args

    def printable_info(self):

        def format_header(info):
            return "\n###### {0:20} ###########################\n".format(
                info)

        def format_out(key, val):
            return "{0:40}|    {1}\n".format(
                key, val)

        out = ''
        out += format_header('Report')
        out += format_out('Version', mamonsu_version)
        out += format_out('Platform', sys.platform)
        out += format_out('Python', ' '.join(sys.version.split("\n")))
        out += format_header('System')
        out += format_out('Date', self.date)
        out += format_out('Host', self.hostname)
        out += format_out('Uptime', self.uptime_raw)
        out += format_out('System', self.dmi_info['TOTAL'])
        out += format_out('Serial', self.dmi_info['SERIAL'])
        out += format_out('Release', self.release)
        out += format_out('Kernel', self.kernel)
        out += format_out('Arch', 'CPU = {0}, OS = {1}'.format(
            self.cpu_arch, self.os_arch))
        out += format_out('Virt', self.virtualization)
        out += format_header('Processors')
        out += format_out('Total', self.cpu_model['_TOTAL'])
        out += format_out('Speed', self.cpu_model['speed'])
        out += format_out('Model', self.cpu_model['model'])
        out += format_out('Cache', self.cpu_model['cache'])
        out += format_out('Bench', self.cpu_bench())
        out += format_header('TOP (by cpu)')
        out += self.top_by_cpu + "\n"
        out += format_header('Memory')
        out += format_out('Total', self._humansize(self.meminfo['_TOTAL']))
        out += format_out('Cached', self._humansize(self.meminfo['_CACHED']))
        out += format_out('Buffers', self._humansize(self.meminfo['_BUFFERS']))
        out += format_out('Dirty', self._humansize(self.meminfo['_DIRTY']))
        if 'vm.dirty_ratio' in self.sysctl:
            if 'vm.dirty_background_ratio' in self.sysctl:
                out += format_out('Dirty ratio', '{0} {1}'.format(
                    self.sysctl['vm.dirty_ratio'],
                    self.sysctl['vm.dirty_background_ratio']))
        if 'vm.dirty_bytes' in self.sysctl:
            if 'vm.dirty_background_bytes' in self.sysctl:
                out += format_out('Dirty bytes', '{0} {1}'.format(
                    self.sysctl['vm.dirty_bytes'],
                    self.sysctl['vm.dirty_background_bytes']))
        # todo: overcommit
        out += format_out('Swap', self._humansize(self.meminfo['_SWAP']))
        if 'vm.swappiness' in self.sysctl:
            out += format_out('Swappines', self.sysctl['vm.swappiness'])
        out += format_header('TOP (by memory)')
        out += self.top_by_memory + "\n"
        out += format_header('System settings')
        for k in self.systemd['_main']:
            out += format_out(k, self.systemd['_main'][k])
        out += format_header('Mount')
        out += self.df_raw + "\n"
        out += format_header('Disks')
        for disk in self.block_info:
            out += format_out(disk, 'Scheduler: {0} Queue: {1}'.format(
                self.block_info[disk]['scheduler'],
                self.block_info[disk]['nr_requests']))
        out += format_header('IOstat')
        out += self.iostat_raw + "\n"
        out += format_header('LVM')
        out += self.vgs_raw + "\n"
        out += self.lvs_raw + "\n"
        out += format_header('Raid')
        if not self.is_empty(self.raid):
            for raid in self.raid:
                out += format_out('Controller', raid)
        return out

    def store_raw(self):
        def format_out(info, val):
            return "# {0} ##################################\n{1}\n".format(
                info, val)
        out = format_out('SYSCTL', self.sysctl['_RAW'])
        out += format_out('DMESG', self.dmesg_raw)
        out += format_out('LSPCI', self.lspci_raw)
        out += format_out('CPUINFO', self.cpu_model['_RAW'])
        out += format_out('MEMINFO', self.meminfo['_RAW'])
        out += format_out('DMIDECODE', self.dmi_raw)
        out += format_out('DF', self.df_raw)
        out += format_out('MOUNT', self.mount_raw)
        out += format_out('MDSTAT', self.mdstat_raw)
        out += format_out('IOSTAT', self.iostat_raw)
        out += format_out('LVS', self.lvs_raw)
        out += format_out('VGS', self.vgs_raw)
        return out.encode('ascii', 'ignore').decode('ascii')

    def collect(self):
        info = self.printable_info()
        logging.error("\n{0}\n".format(self.store_raw()))
        return info.encode('ascii', 'ignore').decode('ascii')

    _suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def _humansize(self, nbytes):
        if nbytes == 0:
            return '0 B'
        i = 0
        while nbytes >= 1024 and i < len(self._suffixes) - 1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, self._suffixes[i])

    def cpu_bench(self):
        def _is_prime(n):
            if n % 2 == 0:
                return False
            sqrt_n = int(math.floor(math.sqrt(n)))
            for i in range(3, sqrt_n + 1, 2):
                if n % i == 0:
                    return False
            return True

        begin, y = time.time(), 0
        for x in range(1, 500000):
            if _is_prime(x):
                y = max(x, y)
        return str(round(100 * float(time.time() - begin)) / 100)
