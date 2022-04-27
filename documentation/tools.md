# Mamonsu: tools

List of Mamonsu commands and options:  

    mamonsu agent [agent_action] [-c | --config]  
    mamonsu bootstrap [-M mamonsu_user] [-x | --create-extensions] [-c | --config] [connection_options]  
    mamonsu export {template | config} filename [export_options]  
    mamonsu report [report_options] [connection_options]  
    mamonsu tune [tuning_options] [connection_options]  
    mamonsu upload [upload_options]  
    mamonsu zabbix {template | host | hostgroup} server_action  
    mamonsu zabbix item {error | lastvalue | lastclock} host_id
    mamonsu zabbix dashboard upload [template_name]
    mamonsu zabbix version  
    mamonsu --version  
    mamonsu --help

***

***Table of Contents***
- [Command-Line Reference](#command-line-reference)
  - [agent](#agent)
  - [bootstrap](#bootstrap)
  - [export](#export)
  - [export zabbix-parameters](#export-zabbix-parameters)
  - [report](#report)
  - [tune](#tune)
  - [upload](#upload)
  - [zabbix cli](#zabbix-cli):
    - [zabbix item](#zabbix-item)
    - [zabbix host](#zabbix-host)
    - [zabbix hostgroup](#zabbix-hostgroup)
    - [zabbix template](#zabbix-template)
    - [zabbix dashboard](#zabbix-dashboard)
- [Connection options](#connection-options)
- [Zabbix Server Actions](#zabbix-server-actions)
- [Usage](#usage)
  - [Collecting and Viewing Metrics Data](#collecting-and-viewing-metrics-data)
  - [Tuning PostgreSQL and System Configuration](#tuning-postgresql-and-system-configuration)
  - [Managing Zabbix Server Settings from the Command Line](#managing-zabbix-server-settings-from-the-command-line)
  - [Exporting Metrics for Native Zabbix Agent](#exporting-metrics-for-native-zabbix-agent)
***
## Command-Line Reference
## agent
Syntax:
```shell
mamonsu agent { metric-list | metric-get metric_name | version } [-c | --config]
```
Provides information on the collected metrics from the command line. You can specify one of the following parameters:  

**metric-list**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show the list of metrics that Mamonsu is collecting. The output of this command provides the item key of each metric, its latest value, and the time when this value was received.

**metric-get metric_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Check the latest value for the specified metric. You can get the list of available metrics using the metric-list option.

**version**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display Mamonsu version.

**-c/--config**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify mamonsu config file.  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default = '/etc/mamonsu/agent.conf'  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*mamonsu agent* gets info about default host and port from config file. 


## bootstrap
Syntax:
```shell
mamonsu bootstrap [-M mamonsu_user] [-x | --create-extensions] [-c | --config] [connection_options]
```
Bootstrap Mamonsu. This command can take the following options:

**-M**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify a non-privileged user that will own all Mamonsu processes.

**-x/--create-extensions**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Creates additional extensions and functions for collecting metrics using these extensions objects (currently, pg_buffercache and pgpro_stat_statements).  
 >**_NOTE:_**  *pg_buffercache* can sometimes generate overhead compared to the common behavior of other objects. To avoid this you can `SET work_mem` on *database* or *mamonsu user* level, but be careful not to affect other objects performance. 

**-c/--config**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify mamonsu config file.  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default = '/etc/mamonsu/agent.conf'  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*mamonsu bootstrap* gets info about mamonsu default database from config file.  

**connection_options**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Provide optional command-line connection parameters.

## export
Syntax:
```shell
mamonsu export config filename.conf  [--add-plugins=plugin_directory]
mamonsu export template filename.xml [--add-plugins=plugin_directory]
                                     [--template-name=template_name]
                                     [--application=application_name]
                                     [--old-zabbix]
```
Generate a template or configuration file for metrics collection. The optional parameters to customize metrics collection are as follows:

**--add-plugins=plugin_directory**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Collect metrics that are defined in custom plugins located in the specified plugin_directory. If you are going to use custom plugins, you must provide this option when generating both the configuration file and the template.

**--template-name=template_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the name of the template that will be displayed on the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: Mamonsu PostgreSQL OS, where OS is the name of your operating system.

**--application=application_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify an identifier under which the collected metrics will be displayed on the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: Mamonsu PostgreSQL OS, where OS is the name of your operating system.

**--old-zabbix**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Export a template for Zabbix server version 4.2 or lower.  

## export zabbix-parameters
Syntax:
```shell
mamonsu export zabbix-parameters filename.conf [--add-plugins=plugin_directory]
                                     [--plugin-type={pg | sys | all}]
                                     [--pg-version=version]
                                     [--config=config_file]
```
Export metrics configuration for use with the native Zabbix agent. The optional parameters to customize metrics collection are as follows:

**--add-plugins=plugin_directory**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Collect metrics that are defined in custom plugins located in the specified plugin_directory. If you are going to use custom plugins, you must provide this option when generating both the configuration file and the template.

**--plugin-type={pg | sys | all}**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the type of metrics to collect:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - 'pgsql' for PostgreSQL metrics.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - 'system' for system metrics.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - 'all' for both PostgreSQL and system metrics.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: all

**--pg-version=version**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the major version of the server for which to configure metrics collection. Mamonsu can collect metrics for PostgreSQL versions starting from 9.5.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 10

**--config=config_file**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the agent.conf file to be used as the source for metrics definitions.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: /etc/mamonsu/agent.conf

## export zabbix-template
Syntax:
```shell
mamonsu export zabbix-template filename.xml [--add-plugins=plugin_directory]
                                     [--plugin-type={pg | sys | all}]
                                     [--template-name=template_name]
                                     [--application=application_name]
                                     [--config=config_file]
                                     [--old-zabbix]
```

Export a template for use with the native Zabbix agent. The optional parameters to customize metrics collection are as follows:

**--add-plugins=plugin_directory**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Collect metrics that are defined in custom plugins located in the specified plugin_directory. If you are going to use custom plugins, you must provide this option when generating both the configuration file and the template.

**--plugin-type={pg | sys | all}**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the type of metrics to collect:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - 'pgsql' for PostgreSQL metrics.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - 'system' for system metrics.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - 'all' for both PostgreSQL and system metrics.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: all

**--template-name=template_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the name of the template that will be displayed on the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: Mamonsu PostgreSQL OS, where OS is the name of your operating system

**--application=application_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify an identifier under which the collected metrics will be displayed on the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: Mamonsu PostgreSQL OS, where OS is the name of your operating system

**--config=config_file**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Specify the agent.conf file to be used as the source for metrics definitions.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: /etc/mamonsu/agent.conf

**--old-zabbix**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Export a template for Zabbix server version 4.2 or lower.  

## report
Syntax:
```shell
mamonsu report [--run-system=Boolean] [--run-postgres=Boolean]
               [--print-report=Boolean] [--report-path=report_file]
               [--disable-sudo] [connection_options]
```

Generate a detailed report on the hardware, operating system, memory usage and other parameters of the monitored system, as well as PostgreSQL configuration.

The following optional parameters customize the report:

**--run-system=Boolean**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Include system information into the generated report.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

**--run-postgres=Boolean**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Include information on PostgreSQL into the generated report.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

**--print-report=Boolean**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Print the report to stdout.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: True

**--report-path=report_file**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Save the report into the specified file.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: /tmp/report.txt

**--disable-sudo**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Do not report data that can only be received with superuser rights. This option is only available for Linux systems.

**connection_options**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Provide optional command-line connection parameters.

## tune
Syntax:
```shell
mamonsu tune [--dry-run] [--disable-sudo] [--log-level {INFO|DEBUG|WARN}]
             [--dont-tune-pgbadger] [--dont-reload-postgresql]
             [connection_options]
```

Optimize PostgreSQL and system configuration based on the collected statistics. You can use the following options:

**--dry-run**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display the settings to be tuned without changing the actual system and PostgreSQL configuration.

**--disable-sudo**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Do not tune the settings that can only be changed by a superuser. This option is only available for Linux systems.

**--dont-tune-pgbadger**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Do not tune pgbadger parameters.

**--log-level { INFO | DEBUG | WARN}**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Change the logging level.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: INFO

**--dont-reload-postgresql**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Forbid Mamonsu to run the pg_reload_conf() function. If you specify this option, the modified settings that require reloading PostgreSQL configuration do not take effect immediately.

**connection_options**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Provide optional command-line connection parameters.

## upload
Syntax:
```shell
mamonsu upload [--zabbix-file=metrics_file]
               [--zabbix-address=zabbix_address] [--zabbix-port=port_number] 
               [--zabbix-client=zabbix_host_name] [--zabbix-log-level={INFO|DEBUG|WARN}]
```
Upload metrics data previously saved into a file onto a Zabbix server for visualization. For details on how to save metrics into a file, see the section called “Logging Parameters”.

This command can take the following options:

**--zabbix-address=zabbix_address**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The address of the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: localhost

**--zabbix-port=port_number**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The port of the Zabbix server.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 10051

**--zabbix-file=metrics_file**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A text file that stores the collected metric data to be visualized, such as localhost.log.

**--zabbix-client=zabbix_host_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The name of the Zabbix host.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: localhost

**--zabbix-log-level={INFO|DEBUG|WARN}**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Change the logging level.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: INFO

## zabbix cli
### zabbix item
Syntax:
```shell
mamonsu zabbix item {error | lastvalue | lastclock } host_name
```
View the specified property of the latest metrics data received by Zabbix for the specified host.

### zabbix version
Syntax:
```shell
mamonsu zabbix version
```
Get the version of the Zabbix server that mamonsu is connected to.

### zabbix host
Syntax:
```shell
mamonsu zabbix host list
mamonsu zabbix host show host_name
mamonsu zabbix host id host_name
mamonsu zabbix host delete host_id
mamonsu zabbix host create host_name hostgroup_id template_id mamonsu_address
mamonsu zabbix host info {templates | hostgroups | graphs | items} host_id
```
Manage Zabbix hosts using one of the actions described in the section called “[Zabbix Server Actions](#zabbix-server-actions)”.

### zabbix hostgroup
Syntax:
```shell
mamonsu zabbix hostgroup list
mamonsu zabbix hostgroup show hostgroup_name
mamonsu zabbix hostgroup id hostgroup_name
mamonsu zabbix hostgroup delete hostgroup_id
mamonsu zabbix hostgroup create hostgroup_name
```
Manage Zabbix host groups using one of the actions described in the section called “[Zabbix Server Actions](#zabbix-server-actions)”.

### zabbix template
Syntax:
```shell
mamonsu zabbix template list
mamonsu zabbix template show template_name
mamonsu zabbix template id template_name
mamonsu zabbix template delete template_id
mamonsu zabbix template export file
```
Manage Zabbix templates using one of the actions described in the section called “[Zabbix Server Actions](#zabbix-server-actions)”.

### zabbix dashboard
Syntax:
```shell
mamonsu zabbix dashboard upload [template_name]
```
Upload Zabbix Dashboard with necessary PostgreSQL and system metrics to Mamonsu template. Works only with Zabbix 6.0 and higher. Template example:  
<details>
    <summary>Click to view</summary>
    <img src="../examples/Mamonsu%20Dashboard.png" alt="Mamonsu Dashboard">
</details>

## --version
Syntax:
```shell
mamonsu --version
```
Display Mamonsu version.

## --help
Syntax:
```shell
mamonsu --help
```
Display Mamonsu command-line help.
***
## Connection Options
*connection_options* provide command-line connection parameters for the target PostgreSQL cluster. *connection_options* can be --host, --port, --dbname (-d), --username (-U), and --password (-W). The --dbname option should specify the *mamonsu_database* created for monitoring purposes. Note that the --username (-U) option must specify a superuser that can access the cluster.

If you omit *connection_options*, Mamonsu checks the corresponding environment variables for these settings. If they are missing, Mamonsu tries to connect to the *current_user* database of the server instance running locally on port 5432 on behalf of *current_user*, where *current_user* is the operating system user name. Make sure to provide the actual connection parameters if your PostgreSQL cluster is located elsewhere.

***

## Zabbix Server Actions
Using Mamonsu, you can control some of the Zabbix server functionality from the command line. Specifically, you can create or delete Zabbix hosts and host groups, as well as generate, import, and delete Zabbix templates using one of the following commands. The *object_name* to use must correspond to the type of the Zabbix object specified in the command: template, host, or hostgroup.

**list**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display the list of available templates, hosts, or host groups.

**show object_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display the details about the specified template, host, or host group.

**id object_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show the ID of the specified object, which is assigned automatically by the Zabbix server.

**delete object_id**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Delete the object with the specified ID.

**create hostgroup_name**  
**create host_name hostgroup_id template_id mamonsu_address**    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Create a new host or a host group.

**export template_name**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Generate a Zabbix template.

**info {templates | hostgroups | graphs | items} host_id**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display detailed information about the templates, host groups, graphs, and metrics available on the host with the specified ID.

***

## Usage

### Collecting and Viewing Metrics Data
Once started, Mamonsu begins collecting system and PostgreSQL metrics. The agent command enables you to get an overview of the collected metrics from the command line in real time.

To view the list of available metrics, use the agent metric-list command:
```shell
mamonsu agent metric-list
```
The output of this command provides the item key of each metric, its latest value, and the time when this value was received. For example:
```shell
system.memory[active]      7921004544    1564570818
system.memory[swap_cache]      868352    1564570818
pgsql.connections[idle]           6.0    1564570818
pgsql.archive_command[failed_trying_to_archive]    0    1564570818
```
To view the current value for a specific metric, you can use the agent metric-get command:
```shell
mamonsu agent metric-get metric_name
```
where *metric_name* is the item key of the metric to monitor, as returned by the metric-list command. For example, pgsql.connections[idle].

You can view graphs for the collected metrics in the Zabbix web interface under the **Graphs** menu. For details on working with Zabbix, see its official documentation at https://www.zabbix.com/documentation/current/.

If you have chosen to save all the collected metrics data into a file, as explained in the section called “Logging Parameters”, you can later upload these metrics onto a Zabbix server for visualization using the [upload](#upload) command.

### Tuning PostgreSQL and System Configuration
Based on the collected metrics data, Mamonsu can tune your PostgreSQL and system configuration for optimal performance.

You can get detailed information about the hardware, operating system, memory usage and other parameters of the monitored system, as well as PostgreSQL configuration, as follows:
```shell
mamonsu report
```
To view the suggested optimizations without applying them, run the tune command with the --dry-run option:
```shell
mamonsu tune --dry-run
```
To apply all the suggested changes, run the tune command without any parameters:
```shell
mamonsu tune
```
You can exclude some settings from the report or disable some of the optimizations by passing optional parameters. See the section called “[Command-Line Reference](#command-line-reference)” for the full list of parameters available for report and tune commands.

### Managing Zabbix Server Settings from the Command Line
Mamonsu enables you to work with the Zabbix server from the command line. You can upload template files to Zabbix, create and delete Zabbix hosts and host groups, link templates with hosts and check the latest metric values.

To set up your Zabbix host from scratch, you can follow these steps:

1. Optionally, specify your Zabbix account settings in the following environment variables on your monitoring system:

    - Set the ZABBIX_USER and ZABBIX_PASSWD variables to the login and password of your Zabbix account, respectively. 
    - Set the ZABBIX_URL to http://zabbix/

    If you skip this step, you will have to add the following options to all mamonsu zabbix commands that you run:
    ```shell
    --url=http://zabbix/ --user=zabbix_login --password=zabbix_password
    ```
2. Generate a new template file and upload it to the Zabbix server:
    ```shell
    mamonsu export template template.xml
    mamonsu zabbix template export template.xml
    ```
3. Create a new host group:
    ```shell
    mamonsu zabbix hostgroup create hostgroup_name
    ```
4. Check the IDs for this host group and the uploaded template, which are assigned automatically by the Zabbix server:
    ```shell
    mamonsu zabbix hostgroup id hostgroup_name
    mamonsu zabbix template id template_name
    ```
5. Create a host associated with this group and link it with the uploaded template using a single command:
    ```shell
    mamonsu zabbix host create host_name hostgroup_id template_id mamonsu_address
    ```
    where *host_name* is the name of the host, *hostgroup_id* and *template_id* are the unique IDs returned in the previous step, and *mamonsu_address* is the IP address of the system on which Mamonsu runs.

Once your Zabbix host is configured, complete the setup of your monitoring system as explained in sections “[Installation](../README.md#installation)" and "[Configuration](../README.md#configuration)”.

## Exporting Metrics for Native Zabbix Agent
Using Mamonsu, you can convert system and PostgreSQL metrics definitions to the format supported by the native [Zabbix agent](https://www.zabbix.com/documentation/current/manual/concepts/agent).

This feature currently has the following limitations:

- You cannot export metrics if you run Mamonsu on Windows systems.

- Metrics definitions for pg_wait_sampling and CFS features available in Postgres Pro Enterprise are not converted.

To collect metrics provided by Mamonsu using the native Zabbix agent, do the following:

1. Generate a configuration file that is compatible with the native Zabbix agent and place it under /etc/zabbix/zabbix_agent.d/. You can prepend the filename with the required path:
    ```shell
    mamonsu export zabbix-parameters /etc/zabbix/zabbix_agent.d/zabbix_agent.conf
    ```
    For all possible options of the export zabbix-parameters command, see the section called “[Command-Line Reference](#command-line-reference)”.
3. Generate a template for the native Zabbix agent:
    ```shell
    mamonsu export zabbix-template template.xml
    ```
    For all possible options of the export zabbix-template command, see the section called “[Command-Line Reference](#command-line-reference)”.

3. Upload the generated template to the Zabbix server, as explained in in sections “[Installation](../README.md#installation)" and "[Configuration](../README.md#configuration)”.

4. If you are going to collect PostgreSQL metrics, change the following macros in the template after the upload:
   - For {$PG_CONNINFO}, provide connection parameters for the PostgreSQL server to be monitored. 
   - For {$PG_PATH}, specify psql installation directory.