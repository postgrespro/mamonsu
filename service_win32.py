import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import servicemanager
import os

from threading import Thread
from mamonsu.lib.config import Config
from mamonsu.lib.supervisor import Supervisor


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

        # __file__ == 'service_win32.py'
        exe_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(exe_dir)

        win32evtlogutil.ReportEvent(
            self._svc_name_,
            servicemanager.PYS_SERVICE_STARTED,
            0,
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            (self._svc_name_, ''))

        config_file = os.path.join(exe_dir, 'agent.conf')
        config = Config(config_file)

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


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MamonsuSvc)
