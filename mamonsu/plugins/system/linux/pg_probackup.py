from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from mamonsu.lib.plugin import PluginDisableException
import json
import os
import subprocess
from datetime import datetime

class PgProbackup(Plugin):
    os_walk_error = None
    block_size = 4096
    Interval = 15 * 60
    key_main = 'pg_probackup.discovery{0}'
    key_dir_size = 'pg_probackup.dir.size{0}'
    key_dir_error = 'pg_probackup.dir.error{0}'
    key_dir_duration_full = 'pg_probackup.dir.duration_full{0}'
    key_dir_duration_inc = 'pg_probackup.dir.duration_inc{0}'
    key_dir_endtime_backup = 'pg_probackup.dir.end_time_backup{0}'
    key_dir_starttime_backup = 'pg_probackup.dir.start_time_backup{0}'
    key_dir_status_backup = 'pg_probackup.dir.status_backup{0}'
    key_dir_mode_backup = 'pg_probackup.dir.mode_backup{0}'
    AgentPluginType = 'pg'
    Type = "mamonsu"
    
    DEFAULT_CONFIG = {
        'max_time_run_backup2alert_in_sec': str(21600),   # The maximum time of running time of backup to Alert in seconds (6 hours)
        'max_time_lack_backup2alert_in_sec': str(100800), # The maximum time of lack of backup to Alert (28 hours)
    }

    def set_os_walk_error(self, e):
        self.os_walk_error = e

    def dir_size(self, path):
        self.os_walk_error = None
        tree = os.walk(path, onerror=self.set_os_walk_error)
        total_size = 0
        for dirpath, dirnames, filenames in tree:
            for file in filenames:
                try:
                    size = os.path.getsize(os.path.join(dirpath, file))
                    if 0 < size < self.block_size:
                        size = round(size / self.block_size) * self.block_size + self.block_size
                except FileNotFoundError as e:
                    self.log.debug(str(e))
                    size = 0
                total_size += size
            try:
                size = os.path.getsize(dirpath)
            except FileNotFoundError as e:
                self.log.debug(str(e))
                size = 0
            total_size += size
        return total_size

    def run(self, zbx):
        config_pg_probackup_path = self.plugin_config('pg_probackup_path')

        if config_pg_probackup_path is None or config_pg_probackup_path == '':
            self.disable()
            raise PluginDisableException(
                """Disable plugin and exit, because the parameter 'pg_probackup_path' in section [pgprobackup] is not 
                set. Set this parameter if needed and restart.""")
        config_backup_dirs = self._plugin_config.get('backup_dirs', None)

        if config_backup_dirs is None or config_backup_dirs == '':
            self.disable()
            raise PluginDisableException(
                """Disable plugin and exit, because the parameter 'backup_dirs' in section [pgprobackup] is not set. 
                Set this parameter if needed and restart.""")

        fmt_data = '%Y-%m-%d %H:%M:%S+03'
        backup_dirs = config_backup_dirs.split(',')
        dirs = []
        for _dir_top in backup_dirs:

            # Search for backups with bad status is done by running
            # "pg_probackup  show -B backup_dir" command
            command = [config_pg_probackup_path, 'show', '-B', _dir_top, '--format=json']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            return_code = process.returncode
            if return_code != 0:
                self.log.error(
                    "The command: {command} return code {return_code}. Error: {error}".format(command=command,
                                                                                            return_code=return_code,
                                                                                            error=stderr))
                continue
            try:
                result = json.loads(stdout.decode('utf-8'))
            except Exception as e:
                self.log.error('Error in convert data: {stdout} \n {e}'.format(stdout=stdout, e=e))
                continue

            no_error= True

            for instance in result:
                # We consider the sizes of each instance
                instance_name = instance['instance']
                _dir = _dir_top + '/' + instance_name
                dirs.append({'{#BACKUPDIR}': _dir})

                # sud-directory backups
                dir_size_backups = self.dir_size(_dir_top + '/backups/' + instance_name)
                if self.os_walk_error:
                    self.log.error(
                        "Error in count size pg_probackup dir: {backup_catalog}. Error: {error}".format(
                            backup_catalog=(_dir_top + '/backups/' + instance_name), error=str(self.os_walk_error)))
                else:
                    # We consider the size of the predefined directories - backups
                    zbx.send(self.key_dir_size.format('[' + _dir + '/backups]'), dir_size_backups)
                    
                # sud-directory wal
                dir_size_wal = self.dir_size(_dir_top + '/wal/' + instance_name)
                if self.os_walk_error:
                    self.log.error(
                        "Error in count size pg_probackup dir: {backup_catalog}. Error: {error}".format(
                            backup_catalog=(_dir_top + '/wal/' + instance_name), error=str(self.os_walk_error)))
                else:
                    # We consider the size of the predefined directories - wal
                    zbx.send(self.key_dir_size.format('[' + _dir + '/wal]'), dir_size_wal)
                
                # We consider the size of the predefined directories - backups and wal
                zbx.send(self.key_dir_size.format('[' + _dir + ']'), dir_size_backups+dir_size_wal)

                full_send = 0
                for idx, backup in enumerate(instance.get('backups', [])):
                    status = backup['status']
                    mode = backup['backup-mode']
                    if idx == 0:
                        # Status of the last backup
                        zbx.send(self.key_dir_status_backup.format('[' + _dir + ']'), status)
                        # Backup Creation Mode Full, Page, Delta and Ptrack of the last backup
                        zbx.send(self.key_dir_mode_backup.format('[' + _dir + ']'), mode)
                    if status in ['ERROR', 'CORRUPT', 'ORPHAN']:
                        error = 'Backup with id: {backup_id} in instance: {instance_name} in pg_probackup dir: ' \
                                '{backup_catalog} has status: {status}.'.format(backup_id=backup['id'],
                                                                                instance_name=instance_name,
                                                                                status=status, backup_catalog=_dir)
                        self.log.info(error)
                        no_error = False
                        zbx.send(self.key_dir_error.format('[' + _dir + ']'), error)
                    if idx == 0:
                        # the start time of the last backup at unixtime 
                        start = datetime.strptime(backup['start-time'], fmt_data)
                        zbx.send(self.key_dir_starttime_backup.format('[' + _dir + ']'), start.timestamp())
                        # check end-time and calculate duration
                        if 'end-time' in backup:
                            end = datetime.strptime(backup['end-time'], fmt_data)
                            delta = (end - start).total_seconds()
                            # the end time of the last backup at unixtime 
                            zbx.send(self.key_dir_endtime_backup.format('[' + _dir + ']'), end.timestamp())
                            # duration full or incremental of the last backup
                            if backup['backup-mode'] == "FULL":
                                zbx.send(self.key_dir_duration_full.format('[' + _dir + ']'), delta)
                                full_send = 1
                            else:
                                zbx.send(self.key_dir_duration_inc.format('[' + _dir + ']'), delta)
                    if full_send == 0 and 'end-time' in backup and backup['backup-mode'] == "FULL":
                        start = datetime.strptime(backup['start-time'], fmt_data)
                        end = datetime.strptime(backup['end-time'], fmt_data)
                        delta = (end - start).total_seconds()
                        zbx.send(self.key_dir_duration_full.format('[' + _dir + ']'), delta)
                        full_send = 1

                if no_error:
                    zbx.send(self.key_dir_error.format('[' + _dir + ']'), 'ok')

        zbx.send(self.key_main.format('[]'), zbx.json({'data': dirs}))
        del dirs

    def discovery_rules(self, template, dashboard=False):
        rule = {
            'name': 'Pg_probackup discovery',
            'key': self.key_main.format('[{0}]'.format(self.Macros[self.Type])),
        }
        if Plugin.old_zabbix:
            conditions = []
            rule['filter'] = '{#BACKUPDIR}:.*'
        else:
            conditions = [
                {
                    'condition': [
                        {'macro': '{#BACKUPDIR}',
                         'value': '.*',
                         'operator': 8,
                         'formulaid': 'A'}
                    ]
                }
            ]
        items = [
            {'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: size',
             'units': Plugin.UNITS.bytes,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'history': '31',
             'delay': self.plugin_config('interval'),
             'description': "Size of the entire catalog with backups"},
            {'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR}/backups,"),
             'name': 'Pg_probackup dir {#BACKUPDIR}/backups: size',
             'units': Plugin.UNITS.bytes,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'history': '31',
             'delay': self.plugin_config('interval'),
             'description': "The size of the entire subdirectory /backups"},
            {'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR}/wal,"),
             'name': 'Pg_probackup dir {#BACKUPDIR}/wal: size',
             'units': Plugin.UNITS.bytes,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'history': '31',
             'delay': self.plugin_config('interval'),
             'description': "The size of the entire subdirectory /wal"},
            {'key': self.right_type(self.key_dir_error, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: error',
             'value_type': Plugin.VALUE_TYPE.text,
             'delay': self.plugin_config('interval'),
             'description': "Sign of the erroneous completion of the backup: 'ERROR', 'CORRUPT', 'ORPHAN'"},
            {'key': self.right_type(self.key_dir_duration_full, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: duration full backup',
             'units': Plugin.UNITS.s,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'history': '31',
             'delay': self.plugin_config('interval'),
             'description': "The duration of the last full backup"},
            {'key': self.right_type(self.key_dir_duration_inc, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: duration incremental backup',
             'units': Plugin.UNITS.s,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'history': '31',
             'delay': self.plugin_config('interval'),
             'description': "The duration of the last incremental backup"},
            {'key': self.right_type(self.key_dir_endtime_backup, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: end time backup',
             'units': Plugin.UNITS.unixtime,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'delay': self.plugin_config('interval'),
             'description': "The end time of the last any backup"},
            {'key': self.right_type(self.key_dir_starttime_backup, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: start time backup',
             'units': Plugin.UNITS.unixtime,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'delay': self.plugin_config('interval'),
             'description': "The start time of the last any backup"},
            {'key': self.right_type(self.key_dir_status_backup, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: status',
             'value_type': Plugin.VALUE_TYPE.text,
             'delay': self.plugin_config('interval'),
             'description': "Sign of the status completion of the last backup:\n\n"
                            "OK — the backup is complete and valid.\n"
                            "DONE — the backup is complete, but was not validated.\n"
                            "RUNNING — the backup is in progress.\n"
                            "MERGING — the backup is being merged.\n"
                            "MERGED — the backup data files were successfully merged, but its metadata is in the process of being updated. Only full backups can have this status.\n"
                            "DELETING — the backup files are being deleted.\n"
                            "CORRUPT — some of the backup files are corrupt.\n"
                            "ERROR — the backup was aborted because of an unexpected error.\n"
                            "ORPHAN — the backup is invalid because one of its parent backups is corrupt or missing.\n\n"
                            "https://postgrespro.ru/docs/postgrespro/current/app-pgprobackup"
                            },
            {'key': self.right_type(self.key_dir_mode_backup, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: mode',
             'value_type': Plugin.VALUE_TYPE.text,
             'delay': self.plugin_config('interval'),
             'description': "Backup Creation Mode:\n\n"
                            "FULL — creates a full backup that contains all the data files of the cluster to be restored.\n"
                            "DELTA — reads all data files in the data directory and creates an incremental backup for pages that have changed since the previous backup.\n"
                            "PAGE — creates an incremental backup based on the WAL files that have been generated since the previous full or incremental backup was taken. Only changed blocks are read from data files.\n"
                            "PTRACK — creates an incremental backup tracking page changes on the fly.\n\n"
                            "https://postgrespro.ru/docs/postgrespro/current/app-pgprobackup"
                            },
        ]
        graphs = [
            {
                'name': 'Pg_probackup: backup dir: {#BACKUPDIR} duration',
                'type': 0,
                'items': [
                    {'color': '00897B',
                     'drawtype': 2,
                     'key': self.right_type(self.key_dir_duration_full, var_discovery="{#BACKUPDIR},")},
                    {'color': '66BB6A',
                     'drawtype': 2,
                     'key': self.right_type(self.key_dir_duration_inc, var_discovery="{#BACKUPDIR},"),
                     'yaxisside': 1}
                ]
            },
            {
                'name': 'Pg_probackup: backup dir: {#BACKUPDIR} size',
                'type': 0,
                'items': [
                    {'color': 'C8E6C9',
                     'drawtype': 1,
                     'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR},")},
                    {'color': '00897B',
                     'drawtype': 2,
                     'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR}/backups,")},
                    {'color': '66BB6A',
                     'drawtype': 2,
                     'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR}/wal,"),
                     'yaxisside': 1}
                ]
            },
        ]
        triggers = [
            {'name': 'Error in pg_probackup dir {#BACKUPDIR} (hostname={HOSTNAME} value={ITEM.LASTVALUE})',
             'expression': '{#TEMPLATE:pg_probackup.dir.error[{#BACKUPDIR}].str(ok)}&lt;&gt;1',
             'priority': 3,
             'description': 'Backup status: CORRUPT / ERROR / ORPHAN'},
            {'name': 'Long time no backups on {HOSTNAME} in pg_probackup dir {#BACKUPDIR}',
             'expression': '({#TEMPLATE:pg_probackup.dir.end_time_backup[{#BACKUPDIR}].now()}-{#TEMPLATE:pg_probackup.dir.end_time_backup[{#BACKUPDIR}].last()})&gt;'
                            + self.plugin_config('max_time_lack_backup2alert_in_sec'),
             'priority': 2,
             'description': 'From the moment of completion of the backup passed more than ' 
                            + str(int(int(self.plugin_config('max_time_lack_backup2alert_in_sec'))/3600)) + ' hours (' 
                            + self.plugin_config('max_time_lack_backup2alert_in_sec') + ' seconds)'},
            {'name': 'Backup runs too long on {HOSTNAME} in pg_probackup dir {#BACKUPDIR} (RUNNING)',
             'expression': '{#TEMPLATE:pg_probackup.dir.status_backup[{#BACKUPDIR}].last()}="RUNNING"'
                           ' and ({#TEMPLATE:pg_probackup.dir.start_time_backup[{#BACKUPDIR}].now()}-{#TEMPLATE:pg_probackup.dir.start_time_backup[{#BACKUPDIR}].last()})&gt;'
                           + self.plugin_config('max_time_run_backup2alert_in_sec'),
             'priority': 2,
             'description': 'From the moment of start of the backup passed more than ' 
                            + str(int(int(self.plugin_config('max_time_run_backup2alert_in_sec'))/3600)) + ' hours (' 
                            + self.plugin_config('max_time_run_backup2alert_in_sec') + ' seconds)'},
        ]
        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs, triggers=triggers)
