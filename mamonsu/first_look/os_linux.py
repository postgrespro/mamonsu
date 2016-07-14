# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import logging
import os
import re
import glob

from mamonsu import __version__

sudoWorking = None


def is_sudo_working():
    global sudoWorking
    if os.getuid() == 0:
        sudoWorking = True
        return
    if sudoWorking is None:
        sudoWorking = False
        p = subprocess.Popen(
            'sudo true',
            shell=True,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True)
        exec_time = 0
        while p.poll() is None:
            time.sleep(0.1)
            exec_time += 0.1
            if exec_time >= 1:
                return
        if p.returncode == 0:
            sudoWorking = True
    return sudoWorking


class Shell(object):

    # exit status of timeout code
    TimeoutCode = -1
    # local var
    _sudo_result = None

    def __init__(self, cmd, timeout=10, sudo=False):
        self.status = self.TimeoutCode
        self.cmd, self._real_command, self.sudo = cmd, cmd, sudo
        if sudo and is_sudo_working():
            self._real_command = 'sudo {0}'.format(cmd)
        self.stdout, self.stderr = '', ''
        self.wait_time, self.exec_time = timeout, 0
        p = subprocess.Popen(
            self._real_command,
            shell=True,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True)
        while p.poll() is None:
            time.sleep(0.1)
            self.exec_time += 0.1
            line = p.stdout.read()
            if not line == '':
                self.stdout += line.decode('utf-8')
            line = p.stderr.read()
            if not line == '':
                self.stderr += line.decode('utf-8')
            if self.wait_time > 0 and self.exec_time >= self.wait_time:
                return
        self.status = p.returncode
        for line in p.stdout.readlines():
            self.stdout += line.decode('utf-8')
        for line in p.stderr.readlines():
            self.stderr += line.decode('utf-8')
        self.stdout = self.stdout.strip()
        self.stderr = self.stderr.strip()

    def error(self):
        return 'Command `{0}` error code: {1}, sdterr: {2}'.format(
            self.cmd, self.status, self.stderr)


class SystemInfo(object):

    def __init__(self, args):
        self.args = args
        # disable sudo
        global sudoWorking
        if not self.args.use_sudo:
            sudoWorking = False
        logging.info('Test if sudo is working: {0}'.format(is_sudo_working()))
        logging.info('Collecting date...')
        self.date = self._fetch_date()
        logging.info('Collecting hostname...')
        self.hostname = self._fetch_hostname()
        logging.info('Collecting sysctl...')
        self.raw_sysctl = self._fetch_sysctl()
        logging.info('Collecting sysctl...')
        self.sysctl = self._parse_sysctl(self.raw_sysctl)
        logging.info('Collecting dmesg...')
        self.dmesg = self._fetch_dmesg()
        logging.info('Collecting lspci...')
        self.lspci = self._fetch_lspci()
        logging.info('Collecting release version...')
        self.system_release = self._fetch_release().strip()
        logging.info('Collecting kernel version...')
        self.kernel = self._fetch_kernel()
        logging.info('Collecting virtualization...')
        self.virtualization = self._fetch_virtualization(self.dmesg)
        logging.info('Collecting raid...')
        self.parsed_raid = self._parse_raid(self.lspci, self.dmesg)
        logging.info('Collecting uptime...')
        self.uptime = self._fetch_uptime()
        logging.info('Collecting cpu arch...')
        self.cpu_arch = self._fetch_cpu_arch()
        logging.info('Collecting os arch...')
        self.os_arch = self._fetch_os_arch()
        logging.info('Collecting dmidecode info...')
        self.dmidecode = self._fetch_dmidecode()
        logging.info('Collecting system info via dmidecode...')
        self.system_info = self._fetch_system_info()
        logging.info('Collecting mount points...')
        self.mount = self._fetch_mount()
        logging.info('Collecting df...')
        self.df = self._fetch_df()
        logging.info('Collecting cpu info...')
        self.cpu_info = self._fetch_cpu_info()
        logging.info('Parsing cpu info...')
        self.parsed_cpu_info = self._parse_cpu_info(self.cpu_info)
        logging.info('Collecting meminfo...')
        self.meminfo = self._fetch_meminfo()
        logging.info('Parsing meminfo...')
        self.parsed_meminfo = self._parse_meminfo(self.meminfo, self.sysctl)
        logging.info('Collecting disks info...')
        self.disks = self._fetch_disk_info()
        logging.info('Collecting iostat...')
        self.iostat = self._fetch_iostat()
        logging.info('Collecting lvs info...')
        self.lvs = self._fetch_lvs()
        logging.info('Collecting vgs info...')
        self.vgs = self._fetch_vgs()
        logging.info('Collecting mdstat info...')
        self.mdstat = self._fetch_mdstat()
        logging.info('Collecting systemd settings...')
        self.systemd = self._fetch_systemd()

    def printable_info(self):

        def format_header(info):
            return "\n###### {0:20} ###########################\n".format(info)

        def format_out(key, val):
            return "{0:40}|    {1}\n".format(key, val)

        out = ''
        out += format_header('Report')
        out += format_out('Version', __version__)
        out += format_out('Platform', sys.platform)
        out += format_out('Python', sys.version_info)
        out += format_header('System')
        out += format_out('Date', self.date)
        out += format_out('Host', self.hostname)
        out += format_out('Uptime', self.uptime)
        out += format_out('System', self.system_info['TOTAL'])
        out += format_out('Serial', self.system_info['SERIAL'])
        out += format_out('Release', self.system_release)
        out += format_out('Kernel', self.kernel)
        out += format_out('Arch', 'CPU = {0}, OS = {1}'.format(
            self.cpu_arch, self.os_arch))
        out += format_out('Virt', self.virtualization)
        out += format_header('Processors')
        out += format_out('Total', self.parsed_cpu_info['_TOTAL'])
        out += format_out('Speed', self.parsed_cpu_info['speed'])
        out += format_out('Model', self.parsed_cpu_info['model'])
        out += format_out('Cache', self.parsed_cpu_info['cache'])
        out += format_header('Memory')
        out += format_out('Total', self.parsed_meminfo['_TOTAL'])
        out += format_out('Cached', self.parsed_meminfo['_CACHED'])
        out += format_out('Dirty', self.parsed_meminfo['_DIRTY'])
        out += format_out('Dirty ratio', self.parsed_meminfo['_DIRTY_RATIO'])
        out += format_out('Dirty bytes', self.parsed_meminfo['_DIRTY_BYTES'])
        out += format_out('Swap', self.parsed_meminfo['_SWAP'])
        out += format_out('Swappines', self.parsed_meminfo['_SWAPPINESS'])
        out += format_header('System settings')
        for k in self.systemd['_main']:
            out += format_out(k, self.systemd['_main'][k])
        out += format_header('Mount')
        out += self.df + "\n"
        out += format_header('Disks')
        for disk in self.disks:
            out += format_out(disk, 'Scheduler: {0} Queue: {1}'.format(
                self.disks[disk]['scheduler'],
                self.disks[disk]['nr_requests']))
        out += format_header('IOstat')
        out += self.iostat + "\n"
        out += format_header('LVM')
        out += self.vgs + "\n"
        out += self.lvs + "\n"
        out += format_header('Raid')
        for raid in self.parsed_raid:
            out += format_out('Controller', raid)
        return out

    def store_raw(self):
        def format_out(info, val):
            return "# {0} ##################################\n{1}\n".format(
                info, val)
        out = format_out('SYSCTL', self.raw_sysctl)
        out += format_out('DMESG', self.dmesg)
        out += format_out('LSPCI', self.lspci)
        out += format_out('CPUINFO', self.cpu_info)
        out += format_out('MEMINFO', self.meminfo)
        out += format_out('DMIDECODE', self.dmidecode)
        out += format_out('DF', self.df)
        out += format_out('MOUNT', self.mount)
        out += format_out('MDSTAT', self.mdstat)
        out += format_out('IOSTAT', self.iostat)
        out += format_out('LVS', self.lvs)
        out += format_out('VGS', self.vgs)
        return out

    def collect(self):
        info = self.printable_info()
        logging.error("\n{0}\n".format(self.store_raw()))
        return info

    _suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def _humansize(self, nbytes):
        if nbytes == 0:
            return '0 B'
        i = 0
        while nbytes >= 1024 and i < len(self._suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, self._suffixes[i])

    def _remove_duplicates(self, values):
        output = []
        seen = set()
        for value in values:
            if value not in seen:
                output.append(value)
                seen.add(value)
        return output

    def _fetch_hostname(self):
        shell = Shell('uname -n')
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
        return 'N/A'

    def _fetch_date(self):
        result = ''
        shell = Shell("date -u +'%F %T UTC'")
        if shell.status == 0:
            result += shell.stdout
        shell = Shell("date +'%Z %z'")
        if shell.status == 0:
            result = "{0} (local TZ:{1})".format(result, shell.stdout)
        return result

    def _fetch_sysctl(self):
        shell = Shell('sysctl -a')
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
        return ''

    def _parse_sysctl(self, sysctl):
        result = {}
        if sysctl == '':
            return result
        for out in sysctl.split("\n"):
            try:
                k, v = out.split(" = ")
                result[k] = v
            except:
                logging.error(
                    "unexpected `systcl -a` output: '{0}'".format(out))
                continue
        return result

    def _fetch_dmesg(self):
        try:
            if os.path.isfile('/var/log/dmesg'):
                with open('/var/log/dmesg', 'r') as content_file:
                    content = content_file.read()
                    return content
        except:
            pass
        shell = Shell('dmesg')
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_virtualization(self, dmesg):
        if dmesg == '':
            return 'N/A'
        if os.path.isfile('/proc/user_beancounters'):
            return 'OpenVZ/Virtuozzo'
        if re.search(r'vmware', dmesg, re.I):
            return 'VMWare'
        if re.search(r'vmxnet', dmesg, re.I):
            return 'VMWare'
        if re.search(r'paravirtualized kernel on vmi', dmesg, re.I):
            return 'VMWare'
        if re.search(r'Xen virtual console', dmesg, re.I):
            return 'Xen'
        if re.search(r'paravirtualized kernel on xen', dmesg, re.I):
            return 'Xen'
        if re.search(r'qemu', dmesg, re.I):
            return 'QEmu'
        if re.search(r'paravirtualized kernel on KVM', dmesg, re.I):
            return 'KVM'
        if re.search(r'VBOX', dmesg, re.I):
            return 'VirtualBox'
        if re.search(r'hd.: Virtual .., ATA.*drive', dmesg, re.I):
            return 'Microsoft VirtualPC'
        return 'N/A'

    def _fetch_lspci(self):
        shell = Shell('lspci')
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_release(self):
        for file in ['/etc/fedora-release', '/etc/redhat-release',
                     '/etc/system-release']:
                if os.path.isfile(file):
                    try:
                        with open(file, 'r') as content_file:
                            content = content_file.read()
                            return content
                    except:
                        pass
        if os.path.isfile('/etc/lsb-release'):
            try:
                with open('/etc/lsb-release', 'r') as f:
                    for line in f:
                        if not re.search(r'DISTRIB_DESCRIPTION', line):
                            continue
                        _, content = line.split('=')
                        return content
            except:
                pass
        if os.path.isfile('/etc/debian_version'):
            try:
                with open('/etc/debian_version', 'r') as f:
                    content = content_file.read()
                    return 'Debian-based version {0}'.format(content)
            except:
                pass
        return 'Unknown'

    def _fetch_kernel(self):
        shell = Shell('uname -r')
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _parse_raid(self, lspci, dmesg):
        controllers = []
        if lspci != '':
            if re.search(
                r'RAID bus controller: LSI Logic / Symbios Logic MegaRAID SAS',
                    lspci, re.I):
                controllers.append('LSI Logic MegaRAID SAS')
            if re.search(
                r'RAID bus controller: LSI Logic / Symbios Logic LSI MegaSAS',
                    lspci, re.I):
                controllers.append('LSI Logic MegaRAID SAS')
            if re.search(
                r'Fusion-MPT SAS',
                    lspci, re.I):
                controllers.append('Fusion-MPT SAS')
            if re.search(
                r'RAID bus controller: LSI Logic / Symbios Logic Unknown',
                    lspci, re.I):
                controllers.append('LSI Logic Unknown')
            if re.search(
                r'RAID bus controller: Adaptec AAC-RAID',
                    lspci, re.I):
                controllers.append('AACRAID')
            if re.search(
                r'3ware [0-9]* Storage Controller',
                    lspci, re.I):
                controllers.append('3Ware')
            if re.search(
                r'Hewlett-Packard Company Smart Array',
                    lspci, re.I):
                controllers.append('HP Smart Array')
            if re.search(
                r'Hewlett-Packard Company Smart Array',
                    lspci, re.I):
                controllers.append('HP Smart Array')
        if dmesg != '':
            if re.search(r'scsi[0-9].*: .*megaraid', dmesg, re.I):
                controllers.append('LSI Logic MegaRAID SAS')
            if re.search(r'Fusion MPT SAS', dmesg):
                controllers.append('Fusion-MPT SAS')
            if re.search(r'scsi[0-9].*: .*aacraid', dmesg, re.I):
                controllers.append('AACRAID')
            if re.search(
                r'scsi[0-9].*: .*3ware [0-9]* Storage Controller',
                    dmesg, re.I):
                controllers.append('3Ware')
        return self._remove_duplicates(controllers)

    def _fetch_uptime(self):
        shell = Shell('uptime')
        if not shell.status == 0:
            logging.error(shell.error())
        return shell.stdout

    def _fetch_cpu_arch(self):
        if os.path.isfile('/proc/cpuinfo'):
            try:
                with open('/proc/cpuinfo', 'r') as content_file:
                    content = content_file.read()
                    if re.search(r' lm ', content):
                        return '64-bit'
                    else:
                        return '32-bit'
            except:
                pass
        return 'N/A'

    def _fetch_os_arch(self):
        shell = Shell('getconf LONG_BIT')
        if shell.status == 0:
            if re.search('64', shell.stdout):
                return '64-bit'
            if re.search('32', shell.stdout):
                return '32-bit'
        else:
            logging.error(shell.error())
        return 'N/A'

    def _fetch_dmidecode(self):
        shell = Shell('dmidecode', sudo=True)
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_system_info(self):

        def dmidecode(key):
            shell = Shell('dmidecode -s "{0}"'.format(key), sudo=True)
            if shell.status == 0:
                return shell.stdout
            else:
                logging.error(shell.error())
                return ''

        result = {}
        result['vendor'] = dmidecode('system-manufacturer')
        result['product'] = dmidecode('system-product-name')
        result['version'] = dmidecode('system-version')
        result['chassis'] = dmidecode('chassis-type')
        result['SERIAL'] = dmidecode('system-serial-number')
        result['TOTAL'] = '{0}; {1}; {2} ({3})'.format(
            result['vendor'], result['product'],
            result['chassis'], result['version'])
        return result

    def _fetch_mount(self):
        shell = Shell('mount')
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_df(self):
        shell = Shell('df -h -P')
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_cpu_info(self):
        if os.path.isfile('/proc/cpuinfo'):
            try:
                with open('/proc/cpuinfo', 'r') as content_file:
                    content = content_file.read()
                    return content
            except:
                logging.error('Can\'t read /proc/cpuinfo')
                return ''
        else:
            logging.error('Can\'t find /proc/cpuinfo')
        return ''

    def _parse_cpu_info(self, info):

        def fetch_first(reg, info):
            val = re.search(reg, info, re.M)
            if val is not None:
                return val.group(1)
            else:
                return 'N/A'

        if info == '':
            return {}

        result = {}
        result['virtual'] = len(
            re.findall(r'(^|\n)processor', info))
        result['physical'] = len(self._remove_duplicates(
            re.findall(
                r'^physical id\s+\:\s+(\d+)', info, re.M)))
        cores = re.search(
            r'^cpu cores\s+\:\s+(\d+)', info, re.M)
        if cores is not None:
            result['cores'] = int(cores.group(1))
        else:
            result['cores'] = 0
        if result['physical'] == 0:
            result['physical'] = result['virtual']
        result['hyperthreading'] = False
        if result['cores'] > 0:
            if result['cores'] < result['virtual']:
                result['hyperthreading'] = True
        result['model'] = fetch_first(r'model name\s+\:\s+(.*)$', info)
        result['cache'] = fetch_first(r'cache size\s+\:\s+(.*)$', info)
        result['speed'] = fetch_first(
            r'^cpu MHz\s+\:\s+(\d+\.\d+)$', info) + ' MHz'
        result['_TOTAL'] = 'physical = {0}, cores = {1}, '\
            'virtual = {2}, hyperthreading = {3}'.format(
                result['physical'], result['cores'],
                result['virtual'], result['hyperthreading']
            )
        return result

    def _fetch_meminfo(self):
        if os.path.isfile('/proc/meminfo'):
            try:
                with open('/proc/meminfo', 'r') as content_file:
                    content = content_file.read()
                    return content
            except:
                logging.error('Can\'t read /proc/meminfo')
                return ''
        else:
            logging.error('Can\'t find /proc/meminfo')
        return ''

    def _parse_meminfo(self, data, sysctl):
        if data == '':
            return {}
        result = {}
        for info in re.findall(r'^(\S+)\:\s+(\d+)\s+kB$', data, re.M):
            result[info[0]] = int(info[1])*1024
        result['_TOTAL'] = ''
        if 'MemTotal' in result:
            result['_TOTAL'] = self._humansize(result['MemTotal'])
        result['_SWAP'] = ''
        if 'SwapTotal' in result:
            result['_SWAP'] = self._humansize(result['SwapTotal'])
        result['_CACHED'] = ''
        if 'Cached' in result:
            result['_CACHED'] = self._humansize(result['Cached'])
        result['_DIRTY'] = ''
        if 'Dirty' in result:
            result['_DIRTY'] = self._humansize(result['Dirty'])
        result['_SWAPPINESS'] = ''
        if 'vm.swappiness' in sysctl:
            result['_SWAPPINESS'] = sysctl['vm.swappiness']
        result['_DIRTY_RATIO'] = '0 0'
        if 'vm.dirty_ratio' in sysctl:
            if 'vm.dirty_background_ratio' in sysctl:
                result['_DIRTY_RATIO'] = '{0} {1}'.format(
                    sysctl['vm.dirty_ratio'],
                    sysctl['vm.dirty_background_ratio'])
        result['_DIRTY_BYTES'] = '0 0'
        if 'vm.dirty_bytes' in sysctl:
            if 'vm.dirty_background_bytes' in sysctl:
                result['_DIRTY_BYTES'] = '{0} {1}'.format(
                    sysctl['vm.dirty_bytes'],
                    sysctl['vm.dirty_background_bytes'])
        return result

    def _fetch_disk_info(self):
        result = {}
        for block in glob.glob('/sys/block/*'):
            data, disk = {}, block.replace('/sys/block/', '')
            if re.search('(ram|loop)', disk):
                continue
            scheduler = '{0}/queue/scheduler'.format(block)
            nr_requests = '{0}/queue/nr_requests'.format(block)
            try:
                if os.path.isfile(scheduler):
                    data['scheduler'] = open(scheduler, 'r').read().strip()
                if os.path.isfile(nr_requests):
                    data['nr_requests'] = open(nr_requests, 'r').read().strip()
                shell = Shell('fdisk -l /dev/{0}'.format(disk), sudo=True)
                if shell.status == 0:
                    data['fdisk'] = shell.stdout
                else:
                    logging.error(shell.error())
                    data['fdisk'] = ''
            except:
                continue
            result[disk] = data
        return result

    def _fetch_iostat(self):
        shell = Shell('iostat -x -N -m 1 2', timeout=3)
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_lvs(self):
        shell = Shell('lvs', sudo=True)
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_vgs(self):
        shell = Shell('vgs -o vg_name,vg_size,vg_free', sudo=True)
        if shell.status == 0:
            return shell.stdout
        else:
            logging.error(shell.error())
            return ''

    def _fetch_mdstat(self):
        if os.path.isfile('/proc/mdstat'):
            try:
                content = open('/proc/mdstat', 'r').read()
                return content
            except:
                logging.error('Can\'t read /proc/mdstat')
                return ''
        return 'N/A'

    def _fetch_systemd(self):
        result = {'_main': {}, 'logind': {}}
        if os.path.isfile('/etc/systemd/logind.conf'):
            try:
                with open('/etc/systemd/logind.conf', 'r') as f:
                    for line in f:
                        data = line.split('=')
                        if not len(data) == 2:
                            continue
                        k, v = data[0].replace('#', ''), data[1]
                        result['logind'][k] = v
                if 'RemoveIPC' in result['logind']:
                    result['_main']['RemoveIPC'] = \
                        result['logind']['RemoveIPC']
            except:
                pass
        return result
