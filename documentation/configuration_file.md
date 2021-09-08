# Mamonsu: configuration file

## Configuration Parameters
The agent.conf configuration file is located in the /etc/mamonsu directory by default. It provides several groups of parameters that control which metrics to collect and how to log the collected data:  
- [Connection Parameters](#connection-parameters);
- [Logging parameters](#logging-parameters);
- [Plugin Parameters](#plugin-parameters).

All parameters must be specified in the parameter = value format.

***

### Connection Parameters
**[postgres]**  
The [postgres] section controls PostgreSQL metrics collection and can contain the following parameters:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables PostgreSQL metrics collection if set to True or False, respectively.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

**user**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The user on behalf of which the cluster will be monitored. It must be the same user that you specified in the -M option of the bootstrap command, or a superuser if you skipped the bootstrap.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: postgres

**password**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The password for the specified user.

**database**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The database to connect to for metrics collection.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: postgres

**host**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The server address to connect to.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: localhost

**port**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The port to connect to.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 5432

**application_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Application name that identifies Mamonsu connected to the PostgreSQL cluster.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: mamonsu

**query_timeout**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[statement_timeout](https://postgrespro.com/docs/postgresql/13/runtime-config-client#GUC-STATEMENT-TIMEOUT) for the Mamonsu session, in seconds. If a PostgreSQL metric query does not complete within this time interval, it gets terminated.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 10

<p>&nbsp;</p>

**[system]**  
The [system] section controls system metrics collection and can contain the following parameters:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables system metrics collection if set to True or False, respectively.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

<p>&nbsp;</p>

**[zabbix]**  
The [zabbix] section provides connection settings for the Zabbix server and can contain the following parameters:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables sending the collected metric data to the Zabbix server if set to True or False, respectively.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

**client**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The name of the Zabbix host.

**address**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The address of the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 127.0.0.1

**port**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The port of the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 10051

<p>&nbsp;</p>

**[agent]**  
The [agent] section specifies the location of Mamonsu and whether it is allowed to access metrics from the command line:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables metrics collection from the command line using the agent command.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

**host**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The address of the system on which Mamonsu is running.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 127.0.0.1

**port**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The port on which Mamonsu is running.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 10052

<p>&nbsp;</p>

**[sender]**  
The [sender] section controls the queue size of the data to be sent to the Zabbix server:

**queue**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The maximum number of collected metric values that can be accumulated locally before mamonsu sends them to the Zabbix server. Once the accumulated data is sent, the queue is cleared.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 2048

***

### Logging Parameters
**[metric_log]**  
The [metric_log] section enables storing the collected metric data in text files locally. This section can contain the following parameters:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables storing the collected metric data in a text file. If this option is set to True, Mamonsu creates the localhost.log file for storing metric values.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: False

**directory**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specifies the directory where log files with metric data will be stored.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: /var/log/mamonsu

**max_size_mb**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The maximum size of a log file, in MB. When the specified size is reached, it is renamed to localhost.log.archive, and an empty localhost.log file is created.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 1024

<p>&nbsp;</p>

**[log]**  
The [log] section specifies logging settings for Mamonsu and can contain the following parameters:

**file**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specifies the log filename, which can be preceded by the full path.

**level**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specifies the debug level. This option can take DEBUG, ERROR, or INFO values.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: INFO

**format**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The format of the logged data.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: [%(levelname)s] %(asctime)s - %(name)s - %(message)s   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;where levelname is the debug level, asctime returns the current time, name specifies the plugin that emitted this log entry or root otherwise, and message provides the actual log message.

***

### Plugin Parameters
**[plugins]**  
The [plugins] section specifies custom plugins to be added for metrics collection and can contain the following parameters:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables using custom plugins for metrics collection if set to True or False, respectively.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: False

**directory**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specifies the directory that contains custom plugins for metrics collection. Setting this parameter to None forbids using custom plugins.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: /etc/mamonsu/plugins

If you need to configure any of the plugins you add to Mamonsu after installation, you have to add this plugin section to the agent.conf file.

The syntax of this section should follow the syntax used with the examples shown below in the section called “[Individual Plugin Sections](#individual-plugin-sections)”.

***

### Individual Plugin Sections
All built-in plugins are installed along with Mamonsu. To configure a built-in plugin you should find a corresponding section below the Individual Plugin Sections heading and edit its parameter values.

To disable any plugin you should set the enabled parameter to False and to enable it — set it to True. These values are case sensitive.

The example below shows individual plugin sections corresponding to the *preparedtransaction* and the *pgprobackup* built-in plugins:
```editorconfig
[preparedtransaction]
max_prepared_transaction_time = 60
interval = 60

[pgprobackup]
enabled = false
interval = 900
backup_dirs = /backup_dir1,/backup_dir2
pg_probackup_path = /usr/bin/pg_probackup-13
max_time_run_backup2alert_in_sec = 21600
max_time_lack_backup2alert_in_sec = 100800
```

**[preparedtransaction]**  
This plugin gets age in seconds of the oldest prepared transaction and number of all transactions prepared for a two-phase commit. For additional information refer to [PREPARE TRANSACTION](https://postgrespro.com/docs/postgresql/13/sql-prepare-transaction) and [pg_prepared_xacts](https://postgrespro.com/docs/postgresql/13/view-pg-prepared-xacts).

The *max_prepared_transaction_time parameter* specifies the threshold in seconds for the age of the prepared transaction.

The interval parameter allows you to change the metrics collection interval.

The plugin collects two metrics: *pgsql.prepared.count* (number of prepared transactions) and *pgsql.prepared.oldest* (oldest prepared transaction age in seconds).

If *pgsql.prepared.oldest* value exceeds the threshold specified by the *max_prepared_transaction_time* parameter, a trigger with the following message is fired: "PostgreSQL prepared transaction is too old on {host}".

**[pgprobackup]**  
This plugin uses pg_probackup to track its backups' state and gets size of backup directories which store all backup files.

Please note that this plugin counts the total size of all files in the target directory. Make sure that extraneous files are not stored in this directory.

The *backup_dirs* parameter specifies a comma-separated list of paths to directories for which metrics should be collected.

The *pg_probackup_path* parameter specifies the path to pg_probackup.

The *interval* parameter allows you to change the metrics collection interval.

By default this plugin is disabled. To enable it set the enabled parameter to True.

This plugin collects several metrics: 
- *pg_probackup.dir.size[#backup_directory]* (the size of the target directory) 
- *pg_probackup.dir.error[#backup_directory]* (backup errors) 
- other metrics for each specified *backup_directory*. 
See file metrics.md

If any generated backup has bad status, like ERROR, CORRUPT, ORPHAN, а trigger is fired.
