from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from mamonsu.lib.plugin import PluginDisableException
import json
import os
import subprocess


class PgProbackup(Plugin):
    os_walk_error = None
    block_size = 4096
    Interval = 5 * 60
    key_main = 'pg_probackup.discovery{0}'
    key_dir_size = 'pg_probackup.dir.size{0}'
    key_dir_error = 'pg_probackup.dir.error{0}'
    AgentPluginType = 'pg'
    Type = "mamonsu"

    def set_os_walk_error(self, e):
        self.os_walk_error = e

    def dir_size(self, path):
        self.os_walk_error = None
        tree = os.walk(path, onerror=self.set_os_walk_error)
        total_size = 0
        for dirpath, dirnames, filenames in tree:
            for file in filenames:
                size = os.path.getsize(os.path.join(dirpath, file))
                if 0 < size < self.block_size:
                    size = round(size / self.block_size) * self.block_size + self.block_size
                total_size += size
            size = os.path.getsize(dirpath)
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

        backup_dirs = config_backup_dirs.split(',')
        dirs = []
        for _dir in backup_dirs:
            dirs.append({'{#BACKUPDIR}': _dir})

            dir_size = self.dir_size(_dir)
            if self.os_walk_error:
                self.log.error(
                    "Error in count size pg_probackup dir: {backup_catalog}. Error: {error}".format(
                        backup_catalog=_dir, error=str(self.os_walk_error)))
            else:
                zbx.send(self.key_dir_size.format('[' + _dir + ']'), dir_size)

            # Search for backups with bad status is done by running
            # "pg_probackup  show -B backup_dir" command
            command = [config_pg_probackup_path, 'show', '-B', _dir, '--format=json']
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
                for backup in instance.get('backups', []):
                    status = backup['status']
                    if status in ['ERROR', 'CORRUPT', 'ORPHAN']:
                        error = 'Backup with id: {backup_id} in instance: {instance_name} in pg_probackup dir: ' \
                                '{backup_catalog}  has status: {status}.'.format(backup_id=backup['id'],
                                                                                 instance_name=instance['instance'],
                                                                                 status=status, backup_catalog=_dir)
                        self.log.info(error)
                        no_error = False
                        zbx.send(self.key_dir_error.format('[' + _dir + ']'), error)
            if no_error:
                zbx.send(self.key_dir_error.format('[' + _dir + ']'), 'ok')

        zbx.send(self.key_main.format('[]'), zbx.json({'data': dirs}))
        del dirs

    def discovery_rules(self, template):
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
                         'operator': None,
                         'formulaid': 'A'}
                    ]
                }
            ]
        items = [
            {'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: size',
             'units': Plugin.UNITS.bytes,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'delay': self.plugin_config('interval')},
            {'key': self.right_type(self.key_dir_error, var_discovery="{#BACKUPDIR},"),
             'name': 'Pg_probackup dir {#BACKUPDIR}: error',
             'value_type': Plugin.VALUE_TYPE.text,
             'delay': self.plugin_config('interval')},
        ]
        graphs = [
            {
                'name': 'Pg_probackup: backup dir: {#BACKUPDIR} size',
                'type': 1,
                'items': [
                    {'color': '00CC00',
                     'key': self.right_type(self.key_dir_size, var_discovery="{#BACKUPDIR},")}]
            },
        ]
        triggers = [{
            'name': 'Error in pg_probackup dir  '
                    '{#BACKUPDIR} (hostname={HOSTNAME} value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pg_probackup.dir.error[{#BACKUPDIR}].str(ok)}&lt;&gt;1'}
        ]
        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs, triggers=triggers)
