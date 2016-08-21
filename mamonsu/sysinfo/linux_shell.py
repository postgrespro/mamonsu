# -*- coding: utf-8 -*-

import os
import subprocess
import time

# cache value
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
