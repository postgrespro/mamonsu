# mamonsu: configuration file

## Configuration Parameters
The *agent.conf* configuration file is located in the */etc/mamonsu* directory by default. It provides several groups of parameters that control which metrics to collect and how to log the collected data:  
- [Connection Parameters](#connection-parameters);
- [Logging parameters](#logging-parameters);
- [Plugin Parameters](#plugin-parameters).

All parameters must be specified in the `parameter = value` format.

> **_NOTE:_**  It is necessary to check permissions to the _mamonsu_ user to directories/files for correct interaction of agent with them. By default configuration file _agent.conf_ should have read/write permissions for _mamonsu_ user only.

> **_NOTE:_**  Config file supports string interpolation via _%()s_ syntax in parameter values. please see “[Parameter Values Interpolation](#parameter-values-interpolation)” below.

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
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Application name that identifies _mamonsu_ connected to the PostgreSQL cluster.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: mamonsu

**query_timeout**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[statement_timeout](https://postgrespro.com/docs/postgresql/14/runtime-config-client#GUC-STATEMENT-TIMEOUT) for the _mamonsu_ session, in seconds. If a PostgreSQL metric query does not complete within this time interval, it gets terminated.

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

**re_send**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Allow mamonsu to resend failed metrics to the Zabbix server.  

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: False  

**timeout**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Zabbix server connection timeout in seconds.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 15

<p>&nbsp;</p>

**[agent]**  
The [agent] section specifies the location of _mamonsu_ and whether it is allowed to access metrics from the command line:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables metrics collection from the command line using the agent command.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

**host**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The address of the system on which _mamonsu_ is running.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 127.0.0.1

**port**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The port on which _mamonsu_ is running.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 10052

<p>&nbsp;</p>

**[sender]**  
The [sender] section controls the queue size of the data to be sent to the Zabbix server:

**queue**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The maximum number of collected metric values that can be accumulated locally before _mamonsu_ sends them to the Zabbix server. Once the accumulated data is sent, the queue is cleared.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 2048

***

### Logging Parameters

**[metric_log]**  
The [metric_log] section enables storing the collected metric data in text files locally. This section can contain the following parameters:

**enabled**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enables/disables storing the collected metric data in a text file. If this option is set to True, _mamonsu_ creates the [zabbix.client].log file for storing metric values.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: False

**directory**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specifies the directory where log files with metric data will be stored.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: /var/log/mamonsu  


**max_size_mb**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The maximum size of a log file, in MB. When the specified size is reached, it is renamed to [zabbix.client].log.archive, and an empty [zabbix.client].log file is created.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 1024

<p>&nbsp;</p>

**[log]**  
The [log] section specifies logging settings for _mamonsu_ and can contain the following parameters:

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

If you need to configure any of the plugins you add to _mamonsu_ after installation, you have to add this plugin section to the agent.conf file.

The syntax of this section should follow the syntax used with the examples shown below in the section called “[Individual Plugin Sections](#individual-plugin-sections)”.

***

### Individual Plugin Sections
All built-in plugins are installed along with _mamonsu_. To configure a built-in plugin you should find a corresponding section below the Individual Plugin Sections heading and edit its parameter values.

To disable any plugin you should set the enabled parameter to False and to enable it — set it to True. These values are case sensitive.

The example below shows individual plugin sections corresponding to the *preparedtransaction* and the *pgprobackup* built-in plugins:
```editorconfig
[preparedtransaction]
max_prepared_transaction_time = 60
interval = 60

[pgprobackup]
enabled = false
interval = 300
backup_dirs = /backup_dir1,/backup_dir2
pg_probackup_path = /usr/bin/pg_probackup-11
```
Let's take a closer look at these examples:  

**[preparedtransaction]**  
This plugin gets age in seconds of the oldest prepared transaction and number of all transactions prepared for a two-phase commit. For additional information refer to [PREPARE TRANSACTION](https://postgrespro.com/docs/postgresql/14/sql-prepare-transaction) and [pg_prepared_xacts](https://postgrespro.com/docs/postgresql/14/view-pg-prepared-xacts).

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

This plugin collects two metrics: *pg_probackup.dir.size[#backup_directory]* (the size of the target directory) and *pg_probackup.dir.error[#backup_directory]* (backup errors) for each specified *backup_directory*.

If any generated backup has bad status, like ERROR, CORRUPT, ORPHAN, а trigger is fired.

### Parameter Values Interpolation

Mamonsu uses python3 built-in configparser library which allows defining arbitary variables in any config section and then reuse it within the same config section.

Example:
```editorconfig
[postgres]
pg = postgres
enabled = True
user = %(pg)s
password = %(pg)s
database = %(pg)s
port = 5432
application_name = %(pg)s
query_timeout = 10
```

What is important to note here is that you cannot use symbol _%_ in any parameter's value since it will be treated as an interolation syntax.
