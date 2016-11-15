# -*- coding: utf-8 -*-

import time
import math
import sys
import logging

from mamonsu import __version__ as mamonsu_version
from mamonsu.tools.sysinfo.linux import SysInfoLinux
from mamonsu.tools.report.format import header_h1, header_h2, key_val_h1, key_val_h2, humansize_bytes, format_raw_h1


class SystemInfo(SysInfoLinux):

    def __init__(self, args):
        sudo = False if (args.disable_sudo is False) else True
        super(SystemInfo, self).__init__(use_sudo=sudo)
        self.args = args

    def printable_info(self):
        out = ''
        out += header_h1('Report')
        out += key_val_h1('Version', mamonsu_version)
        out += key_val_h1('Platform', sys.platform)
        out += key_val_h1('Python', ' '.join(sys.version.split("\n")))
        out += header_h1('System')
        out += key_val_h1('Date', self.date)
        out += key_val_h1('Host', self.hostname)
        out += key_val_h1('Uptime', self.uptime_raw)
        out += key_val_h1('Boot time', self.boot_time_raw)
        out += key_val_h1('System', self.dmi_info['TOTAL'])
        out += key_val_h1('Serial', self.dmi_info['SERIAL'])
        out += key_val_h1('Release', self.release)
        out += header_h2('Kernel:')
        out += key_val_h2('name', self.kernel)
        out += key_val_h2('cmdline', self.kernel_cmdline)
        out += key_val_h1('Arch', 'CPU = {0}, OS = {1}'.format(
            self.cpu_arch, self.os_arch))
        out += key_val_h1('Virt', self.virtualization)
        out += header_h1('Processors')
        out += key_val_h1('Total', self.cpu_model['_TOTAL'])
        out += key_val_h1('Speed', self.cpu_model['speed'])
        out += key_val_h1('Model', self.cpu_model['model'])
        out += key_val_h1('Flags', self.cpu_model['_FLAGS_IMPORTANT'])
        out += key_val_h1('Cache', self.cpu_model['cache'])
        out += key_val_h1('Bench', self.cpu_bench())
        out += header_h1('TOP (by cpu)')
        out += format_raw_h1(self.top_by_cpu)
        out += header_h1('Memory')
        out += key_val_h1('Total', humansize_bytes(self.meminfo['_TOTAL']))
        out += key_val_h1('Committed', humansize_bytes(self.meminfo['_COMMITTED']))
        out += key_val_h1('CommitLimit', humansize_bytes(self.meminfo['_COMMITLIMIT']))
        out += key_val_h1('Shmem', humansize_bytes(self.meminfo['_SHMEM']))
        out += key_val_h1('Slab', humansize_bytes(self.meminfo['_SLAB']))
        out += key_val_h1('PageTables', humansize_bytes(self.meminfo['_PAGETABLES']))
        out += key_val_h1('Free', humansize_bytes(self.meminfo['_FREE']))
        out += key_val_h1('Cached', humansize_bytes(self.meminfo['_CACHED']))
        out += key_val_h1('Buffers', humansize_bytes(self.meminfo['_BUFFERS']))
        out += key_val_h1('Dirty', humansize_bytes(self.meminfo['_DIRTY']))
        out += key_val_h1('HP Total', humansize_bytes(self.meminfo['_HUGEPAGES_SIZE']))
        out += key_val_h1('HP Free', humansize_bytes(self.meminfo['_HUGEPAGES_FREE']))
        out += key_val_h1('SwapTotal', humansize_bytes(self.meminfo['_SWAPTOTAL']))
        out += key_val_h1('SwapUsed', humansize_bytes(self.meminfo['_SWAPUSED']))
        out += header_h1('TOP (by memory)')
        out += format_raw_h1(self.top_by_memory)
        out += header_h1('System settings')
        for k in self.systemd['_main']:
            out += key_val_h1(k, self.systemd['_main'][k])
        out += header_h1('Sysctl')
        out += header_h2('kernel.')
        out += key_val_h2('hostname', self.sysctl_fetch('kernel.hostname'), ' = ')
        out += key_val_h2('osrelease', self.sysctl_fetch('kernel.osrelease'), ' = ')
        out += key_val_h2('shmall', self.sysctl_fetch('kernel.shmall'), ' [4-KiB pages, max size of shared memory] = ')
        out += key_val_h2('shmmax', self.sysctl_fetch('kernel.shmmax'), ' [max segment size in bytes] = ')
        out += key_val_h2('shmmni', self.sysctl_fetch('kernel.shmmni'), ' [max number of segments] = ')
        out += key_val_h2('sched_min_granularity_ns', self.sysctl_fetch('kernel.sched_min_granularity_ns'), ' [nanosecs, min execution time] = ')
        out += key_val_h2('sched_latency_ns', self.sysctl_fetch('kernel.sched_latency_ns'), ' [nanosecs, rescheduling] = ')
        out += header_h2('fs.')
        out += key_val_h2('file-max', self.sysctl_fetch('fs.file-max'), ' [fd system] = ')
        out += key_val_h2('nr_open', self.sysctl_fetch('fs.nr_open'), ' [fd per proc] = ')
        out += key_val_h2('file-nr', self.sysctl_fetch('fs.file-nr'), ' [fd: open, 0, max] = ')
        out += key_val_h2('inode-nr', self.sysctl_fetch('fs.inode-nr'), ' [inode cache: total, free] = ')
        out += header_h2('vm.')
        out += key_val_h2('dirty_ratio', self.sysctl_fetch('vm.dirty_ratio'), ' [% of RAM for dirty pages, only if dirty_bytes=0] = ')
        out += key_val_h2('dirty_bytes', self.sysctl_fetch('vm.dirty_bytes'), ' [bytes for dirty pages] = ')
        out += key_val_h2('dirty_background_ratio', self.sysctl_fetch('vm.dirty_background_ratio'), ' [% of RAM then flusher start, only if dirty_background_bytes=0] = ')
        out += key_val_h2('dirty_background_bytes', self.sysctl_fetch('vm.dirty_background_bytes'), ' [bytes then flusher start] = ')
        out += key_val_h2('dirty_expire_centisecs', self.sysctl_fetch('vm.dirty_expire_centisecs'), ' [max age of dirty data] = ')
        out += key_val_h2('dirty_writeback_centisecs', self.sysctl_fetch('vm.dirty_writeback_centisecs'), ' [flusher wakeup timer] = ')
        out += key_val_h2('overcommit_memory', self.sysctl_fetch('vm.overcommit_memory'), ' [overcommit policy] = ')
        out += key_val_h2('overcommit_ratio', self.sysctl_fetch('vm.overcommit_ratio'), ' [% physical RAM, if policy=2] = ')
        out += key_val_h2('oom_kill_allocating_task', self.sysctl_fetch('vm.oom_kill_allocating_task'), ' [0 - heuristics, else simple kill task who triggered] = ')
        out += key_val_h2('panic_on_oom', self.sysctl_fetch('vm.panic_on_oom'), ' [0 - no panic, 1 - panic only if only not limited (mempolicy/cpusets), 2 - panic] = ')
        out += key_val_h2('swappiness', self.sysctl_fetch('vm.swappiness'), ' [how aggressive use swap] = ')
        out += key_val_h2('nr_hugepages', self.sysctl_fetch('vm.nr_hugepages'), ' [count of persistent huge page pool] = ')
        out += key_val_h2('nr_overcommit_hugepages', self.sysctl_fetch('vm.nr_overcommit_hugepages'), ' [max count of additional huge pages] = ')
        out += header_h1('Mount')
        out += format_raw_h1(self.df_raw)
        out += header_h1('Disks')
        for disk in self.block_info:
            out += key_val_h1(disk, 'Scheduler: {0} Queue: {1}'.format(
                self.block_info[disk]['scheduler'],
                self.block_info[disk]['nr_requests']))
        out += header_h1('IOstat')
        if not self.is_empty(self.iostat_raw):
            out += format_raw_h1(self.iostat_raw)
        out += header_h1('LVM')
        if not self.is_empty(self.vgs_raw):
            out += format_raw_h1(self.vgs_raw)
        if not self.is_empty(self.lvs_raw):
            out += format_raw_h1(self.lvs_raw)
        out += header_h1('Raid')
        if not self.is_empty(self.raid):
            for raid in self.raid:
                out += key_val_h1('Controller', raid)
        out += header_h1('Sockstat')
        for line in self.sockstat.split("\n"):
            try:
                key, val = line.split(":")
                out += key_val_h1(key, val)
            except:
                pass
        out += header_h1('LSPCI')
        for line in self.pci_network_devices:
            out += key_val_h1('net', line)
        for line in self.pci_storage_devices:
            out += key_val_h1('storage', line)
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
