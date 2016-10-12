# -*- coding: utf-8 -*-

import os
import re
import glob
import logging

from mamonsu.tools.sysinfo.linux_shell import Shell

NA = 'N/A'
UNKNOWN = 'Unknown'

VIRT_VMWARE = 'VMWare'
VIRT_QEMU = 'QEmu'
VIRT_KVM = 'KVM'
VIRT_MICROSOFT_VIRTUALPC = 'MS-VirtualPC'
VIRT_MICROSOFT_HYPERV = 'Hyper-V'
VIRT_VIRTUALBOX = 'VirtualBox'
VIRT_XEN = 'Xen'
VIRT_PARALLELS = 'Parallels'

VIRT_VZ = 'OpenVZ/Virtuozzo'
VIRT_LXC = 'LXC'
VIRT_DOCKER = 'Docker'

RAID_LSI = 'LSI Logic MegaRAID SAS'
RAID_HP_SMART = 'HP Smart Array'
RAID_ADAPTEC = 'AACRAID'
RAID_3WARE = '3Ware'
RAID_FUSION_SAS = 'Fusion-MPT SAS'


class SysInfoLinux(object):

    @classmethod
    def is_empty(self, val):
        if val is None or val == NA or val == '':
            return True
        return False

    def __init__(self, use_sudo=True):
        self._cache = {}
        logging.debug('Use sudo: {0}'.format(use_sudo))
        self.use_sudo = use_sudo

    def __getattr__(self, name):

        def remember(self, name, value):
            self._cache[name] = value
            return self._cache[name]

        if name in self._cache:
            return self._cache[name]
        try:
            if name == 'hostname':
                return remember(self, name, self._shell_out('uname -n'))
            elif name == 'date':
                return remember(self, name, self._date())
            elif name == 'sysctl':
                return remember(self, name, self._sysctl())
            elif name == 'dmesg_raw':
                return remember(self, name, self._dmesg_raw())
            elif name == 'kernel':
                return remember(self, name, self._shell_out('uname -r'))
            elif name == 'uptime_raw':
                return remember(self, name, self._shell_out('uptime'))
            elif name == 'mount_raw':
                return remember(self, name, self._shell_out('mount'))
            elif name == 'iostat_raw':
                return remember(self, name, self._shell_out(
                        'iostat -x -N -m 1 2', timeout=3))
            elif name == 'df_raw':
                return remember(self, name, self._shell_out('df -h -P'))
            elif name == 'lspci_raw':
                return remember(self, name, self._shell_out('lspci'))
            elif name == 'mdstat_raw':
                return remember(self, name, self._read_file('/proc/mdstat'))
            elif name == 'lvs_raw':
                return remember(self, name, self._shell_out('lvs', sudo=True))
            elif name == 'vgs_raw':
                return remember(self, name, self._shell_out(
                    'vgs -o vg_name,vg_size,vg_free', sudo=True))
            elif name == 'os_arch':
                return remember(self, name, self._os_arch())
            elif name == 'cpu_arch':
                return remember(self, name, self._cpu_arch())
            elif name == 'dmi_raw':
                return remember(self, name, self._shell_out(
                    'dmidecode', sudo=True))
            elif name == 'dmi_info':
                return remember(self, name, self._dmi_info())
            elif name == 'cpu_model':
                return remember(self, name, self._cpu_model())
            elif name == 'meminfo':
                return remember(self, name, self._meminfo())
            elif name == 'virtualization':
                return remember(self, name, self._virtualization())
            elif name == 'release':
                return remember(self, name, self._release())
            elif name == 'raid':
                return remember(self, name, self._raid())
            elif name == 'block_info':
                return remember(self, name, self._block_info())
            elif name == 'systemd':
                return remember(self, name, self._systemd())
            elif name == 'top_by_cpu':
                return remember(self, name, self._shell_out(
                    'ps aux --sort=-pcpu | head -n 21'))
            elif name == 'top_by_memory':
                return remember(self, name, self._shell_out(
                    'ps aux --sort=-rss | head -n 21'))
        except KeyError:
            raise Exception('Unknown parameter: {0}'.format(name))

    def _shell_out(self, cmd, timeout=1, sudo=False):
        sudo = sudo and self.use_sudo
        shell = Shell(cmd, timeout=timeout, sudo=sudo)
        sudo_cmd = 'sudo -n {0}'.format(cmd) if sudo else cmd
        logging.debug('Shell "{0}" status: {1}'.format(sudo_cmd, shell.status))
        if shell.status == 0:
            return shell.stdout
        return NA

    def is_sudo_working(self):
        return not self.is_empty(
            self._shell_out('echo sudo is worked', sudo=True))

    def _uniq(self, values):
        output = []
        seen = set()
        for value in values:
            if value not in seen:
                output.append(value)
                seen.add(value)
        return output

    def _read_file(self, file):
        result = NA
        if os.path.isfile(file):
            try:
                result = open(file, 'r').read()
            except Exception as e:
                logging.debug('File "{0}" read error: {1}'.format(file, e))
                pass
        return result

    def _cpu_arch(self):
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
        return NA

    def _os_arch(self):
        shell = Shell('getconf LONG_BIT')
        if shell.status == 0:
            if re.search('64', shell.stdout):
                return '64-bit'
            if re.search('32', shell.stdout):
                return '32-bit'
        return NA

    def _date(self):
        result = ''
        shell = Shell("date -u +'%F %T UTC'")
        if shell.status == 0:
            result += shell.stdout
        shell = Shell("date +'%Z %z'")
        if shell.status == 0:
            result = "{0} (local TZ:{1})".format(result, shell.stdout)
        return result

    def _sysctl(self):
        result = {'_RAW': NA}
        shell = Shell('sysctl -a')
        if not shell.status == 0:
            return result
        result['_RAW'] = shell.stdout
        for out in shell.stdout.split("\n"):
            try:
                k, v = out.split(" = ")
                result[k] = v
            except:
                continue
        return result

    def _dmesg_raw(self):
        shell = Shell('journalctl -k -n 1000')
        if shell.status == 0:
            return shell.stdout
        shell = Shell('dmesg')
        if shell.status == 0:
            return shell.stdout
        result = self._read_file('var/log/dmesg')
        return result

    def _dmidecode(self, key):
        return self._shell_out('dmidecode -s \'{0}\''.format(key), sudo=True)

    def _dmi_info(self):
        result = {}
        result['vendor'] = self._dmidecode('system-manufacturer')
        result['product'] = self._dmidecode('system-product-name')
        result['version'] = self._dmidecode('system-version')
        result['chassis'] = self._dmidecode('chassis-type')
        result['SERIAL'] = self._dmidecode('system-serial-number')
        result['TOTAL'] = '{0}; {1}; {2} ({3})'.format(
            result['vendor'], result['product'],
            result['chassis'], result['version'])
        return result

    def _cpu_model(self):

        def fetch_first(reg, info):
            val = re.search(reg, info, re.M)
            if val is not None:
                return val.group(1)
            else:
                return NA

        info, result = self._read_file('/proc/cpuinfo'), {'_RAW': NA}
        if self.is_empty(info):
            return result
        result['_RAW'] = info

        result['virtual'] = len(
            re.findall(r'(^|\n)processor', info))
        result['physical'] = len(self._uniq(
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

    def _meminfo(self):

        data, result = self._read_file('/proc/meminfo'), {}
        result['_RAW'] = NA
        result['_TOTAL'] = NA
        result['_SWAP'] = NA
        result['_CACHED'] = NA
        result['_DIRTY'] = NA
        result['_BUFFERS'] = NA
        if self.is_empty(data):
            return result

        result['_RAW'] = data
        for info in re.findall(r'^(\S+)\:\s+(\d+)\s+kB$', data, re.M):
            result[info[0]] = int(info[1])*1024
        if 'MemTotal' in result:
            result['_TOTAL'] = result['MemTotal']
        if 'SwapTotal' in result:
            result['_SWAP'] = result['SwapTotal']
        if 'Cached' in result:
            result['_CACHED'] = result['Cached']
        if 'Dirty' in result:
            result['_DIRTY'] = result['Dirty']
        if 'Buffers' in result:
            result['_BUFFERS'] = result['Buffers']

        return result

    def _virtualization(self):

        result = self._shell_out('systemd-detect-virt')
        if result == 'qemu':
            return VIRT_QEMU
        if result == 'kvm':
            return VIRT_KVM
        if result == 'vmware':
            return VIRT_VMWARE
        if result == 'microsoft':
            return VIRT_MICROSOFT_HYPERV
        if result == 'oracle':
            return VIRT_VIRTUALBOX
        if result == 'xen':
            return VIRT_XEN
        if result == 'parallels':
            return VIRT_PARALLELS
        if result == 'openvz':
            return VIRT_VZ
        if result == 'lxc':
            return VIRT_LXC
        if result == 'docker':
            return VIRT_DOCKER

        if os.path.isfile('/proc/user_beancounters'):
            return VIRT_VZ

        dmit_product = self.dmi_info['product']
        if re.search(r'VMware', dmit_product, re.I):
            return VIRT_VMWARE
        if re.search(r'VirtualBox', dmit_product, re.I):
            return 'VirtualBox'
        if re.search(r'Bochs', dmit_product, re.I):
            return VIRT_QEMU

        if re.search(
                r'Manufacturer\: Microsoft Corporation', self.dmi_raw, re.I):
            return VIRT_MICROSOFT_VIRTUALPC
        if re.search(r'domU', self.dmi_raw, re.I):
            return VIRT_XEN

        if re.search(r'vmware', self.dmesg_raw, re.I):
            return VIRT_VMWARE
        if re.search(r'vmxnet', self.dmesg_raw, re.I):
            return VIRT_VMWARE
        if re.search(r'paravirtualized kernel on vmi', self.dmesg_raw, re.I):
            return VIRT_VMWARE
        if re.search(r'Xen virtual console', self.dmesg_raw, re.I):
            return VIRT_XEN
        if re.search(r'paravirtualized kernel on xen', self.dmesg_raw, re.I):
            return VIRT_XEN
        if re.search(r'qemu', self.dmesg_raw, re.I):
            return VIRT_QEMU
        if re.search(r'paravirtualized kernel on KVM', self.dmesg_raw, re.I):
            return VIRT_KVM
        if re.search(r'VBOX', self.dmesg_raw, re.I):
            return VIRT_VIRTUALBOX
        if re.search(r'hd.: Virtual .., ATA.*drive', self.dmesg_raw, re.I):
            return VIRT_MICROSOFT_VIRTUALPC

        return NA

    def _release(self):
        result = self._shell_out('lsb_release -ds')
        if not self.is_empty(result):
            return result

        for file in ['/etc/fedora-release', '/etc/redhat-release',
                     '/etc/system-release']:
            if os.path.isfile(file):
                try:
                    with open(file, 'r') as f:
                        result = f.read()
                    return result.strip()
                except:
                    pass
        if os.path.isfile('/etc/debian_version'):
            try:
                with open('/etc/debian_version', 'r') as f:
                    result = f.read()
                    return 'Debian-based version {0}'.format(result).strip()
            except:
                pass
        return NA

    def _block_info(self):
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
                data['fdisk'] = self._shell_out(
                    'fdisk -l /dev/{0}'.format(disk), sudo=True)
            except:
                continue
            result[disk] = data
        return result

    def _raid(self):
        controllers = []
        if not self.is_empty(self.lspci_raw):
            if re.search(
                r'RAID bus controller: LSI Logic / Symbios Logic MegaRAID SAS',
                    self.lspci_raw, re.I):
                controllers.append(RAID_LSI)
            if re.search(
                r'RAID bus controller: LSI Logic / Symbios Logic LSI MegaSAS',
                    self.lspci_raw, re.I):
                controllers.append(RAID_LSI)
            if re.search(
                r'Fusion-MPT SAS',
                    self.lspci_raw, re.I):
                controllers.append(RAID_FUSION_SAS)
            if re.search(
                r'RAID bus controller: LSI Logic / Symbios Logic Unknown',
                    self.lspci_raw, re.I):
                controllers.append(RAID_LSI)
            if re.search(
                r'RAID bus controller: Adaptec AAC-RAID',
                    self.lspci_raw, re.I):
                controllers.append(RAID_ADAPTEC)
            if re.search(
                r'3ware [0-9]* Storage Controller',
                    self.lspci_raw, re.I):
                controllers.append(RAID_3WARE)
            if re.search(
                r'Hewlett-Packard Company Smart Array',
                    self.lspci_raw, re.I):
                controllers.append(RAID_HP_SMART)
            if re.search(
                r'Hewlett-Packard Company Smart Array',
                    self.lspci_raw, re.I):
                controllers.append(RAID_HP_SMART)
        if not self.is_empty(self.dmesg_raw):
            if re.search(r'scsi[0-9].*: .*megaraid', self.dmesg_raw, re.I):
                controllers.append(RAID_LSI)
            if re.search(r'Fusion MPT SAS', self.dmesg_raw):
                controllers.append(RAID_FUSION_SAS)
            if re.search(r'scsi[0-9].*: .*aacraid', self.dmesg_raw, re.I):
                controllers.append(RAID_ADAPTEC)
            if re.search(
                r'scsi[0-9].*: .*3ware [0-9]* Storage Controller',
                    self.dmesg_raw, re.I):
                controllers.append(RAID_3WARE)
        if len(controllers) == 0:
            return NA
        return controllers

    def _systemd(self):
        result = {'_main': {}, 'logind': {}}
        data = self._read_file('/etc/systemd/logind.conf')
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
