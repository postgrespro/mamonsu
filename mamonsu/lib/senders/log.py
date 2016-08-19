# -*- coding: utf-8 -*-
import os
import sys
from mamonsu.lib.plugin import Plugin
from mamonsu.lib.queue import Queue


class LogSender(Plugin):

    Interval = 2
    _sender = True

    def __init__(self, config):
        super(LogSender, self).__init__(config)
        self.metric_log = config.fetch('metric_log', 'directory')
        if self.metric_log is None:
            self._enabled = False
        elif not self.config.fetch('metric_log', 'enabled', bool):
            self._enabled = False
        self._metric_log_fds = {}
        self.queue = Queue()
        self.max_queue_size = config.fetch('sender', 'queue', int)
        self.max_size = config.fetch('metric_log', 'max_size_mb', int)
        self.max_size = self.max_size * 1024 * 1024
        self._check_size_counter = 0

    def run(self, zbx):
        self._flush()

    def send(self, key, value, host=None, clock=None):
        metric = (key, value, host, clock)
        if self.queue.size() > self.max_queue_size:
            self.log.error('Queue size over limit, replace last metrics')
            self.queue.replace(metric)
        else:
            self.queue.add(metric)

    def _flush(self):
        metrics = self.queue.flush()
        if len(metrics) == 0:
            return
        for metric in metrics:
            self._write(metric)

    def _write(self, metric):

        key, value = metric[0], metric[1]
        host, clock = metric[2], metric[3]

        if not os.path.isdir(self.metric_log):
            try:
                os.makedirs(self.metric_log)
            except Exception as e:
                self.log.error('Create directory error: {0}'.format(e))
                sys.exit(7)

        if host is None:
            host = 'localhost'
        metric_log = os.path.join(
                self.metric_log, '{0}.log'.format(host))

        # rotate if reached max size limit
        if self._check_size_counter > 2:
            size = os.path.getsize(metric_log)
            if size > self.max_size:
                # rotate to file <METRIC_LOG>.archive
                backup_file = '{0}.archive'.format(metric_log)
                self.log.info(
                    'Move file {0} to {1} (max size limit reached: {2} b)'.
                    format(metric_log, backup_file, size))
                # close descriptor
                if host in self._metric_log_fds:
                    self._metric_log_fds[host].close()
                    del self._metric_log_fds[host]
                # rename
                os.rename(metric_log, backup_file)
            self._check_size_counter = 0
        self._check_size_counter += 1

        if host not in self._metric_log_fds:
            self._metric_log_fds[host] = open(metric_log, 'a')

        try:
            self._metric_log_fds[host].write("{0}\t{1}\t{2}\n".format(
                clock, value, key))
            self._metric_log_fds[host].flush()
        except Exception as e:
            self._metric_log_fds[host].close()
            del self._metric_log_fds[host]
            self.log.error('Write metric error: {0}'.format(e))
