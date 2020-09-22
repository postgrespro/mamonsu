import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import servicemanager
import os
import sys

import logging

from threading import Thread
from mamonsu.lib.config import Config
from mamonsu.lib.supervisor import Supervisor

config = None

class MamonsuSvc(win32serviceutil.ServiceFramework):

    _svc_name_ = 'mamonsu'
    _svc_description_ = 'monitoring agent: mamonsu'
    _svc_display_name_ = 'monitoring agent: mamonsu'
    _svc_deps_ = ['EventLog']

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):

        win32evtlogutil.ReportEvent(
            self._svc_name_,
            servicemanager.PYS_SERVICE_STARTED,
            0,
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            (self._svc_name_, ''))

        supervisor = Supervisor(config)
        win32evtlogutil.ReportEvent(
            self._svc_name_,
            servicemanager.PYS_SERVICE_STOPPED,
            0,
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            (self._svc_name_, ''))

        thread = Thread(target=supervisor.start)
        thread.daemon = True
        thread.start()
        while True:
            rc = win32event.WaitForSingleObject(
                self.hWaitStop, win32event.INFINITE)
            if rc == win32event.WAIT_OBJECT_0:
                win32evtlogutil.ReportEvent(
                    self._svc_name_,
                    servicemanager.PYS_SERVICE_STOPPED,
                    0,
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    (self._svc_name_, ''))
                break


#if __name__ == '__main__':
#    win32serviceutil.HandleCommandLine(MamonsuSvc)

if __name__ == '__main__':
    # determine if application is a script file or frozen exe       
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    elif __file__:
        # exe_dir = C:\WINDOWS\system32 for service
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # initializing in this place for logging
    config_file = os.path.join(exe_dir, 'agent.conf')
    config = Config(config_file)

    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MamonsuSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MamonsuSvc)
