Name:           mamonsu
Version:        3.5.10
Release:        1%{?dist}
Summary:        Monitoring agent for PostgreSQL
Group:          Applications/Internet
License:        BSD
Source0:        http://pypi.python.org/packages/source/m/mamonsu/mamonsu-%{version}.tar.gz
Source1:        mamonsu.init
Source2:        mamonsu-logrotate.in
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildArch:      noarch
Requires:       python3-setuptools

%description
Monitoring agent for PostgreSQL.

%prep
%setup -q

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --skip-build --root %{buildroot}
export PYTHONPATH=%{buildroot}%{python3_sitelib}

%{__mkdir} -p %{buildroot}/%{_sysconfdir}/%{name}
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/init.d
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/logrotate.d
%{__mkdir} -p %{buildroot}/%{_datarootdir}/%{name}

%{__install} -m 0600 -p packaging/conf/example_linux.conf %{buildroot}/%{_sysconfdir}/%{name}/agent.conf
%{__install} -m 0644 -p packaging/conf/template_linux.xml %{buildroot}/%{_datarootdir}/%{name}/template.xml
%{__install} -m 0644 -p examples/*.py %{buildroot}/%{_datarootdir}/%{name}/
%{__install} -m 0755 -p %{SOURCE1} %{buildroot}/%{_sysconfdir}/init.d/%{name}
%{__install} -m 0644 -p %{SOURCE2} %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}

%files
%doc README.md
%config(noreplace) %{_sysconfdir}/%{name}/agent.conf
%{python3_sitelib}/%{name}/
%{python3_sitelib}/%{name}-%{version}*
%{_sysconfdir}/%{name}
%{_datarootdir}/%{name}
%{_sysconfdir}/init.d/%{name}
%{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group mamonsu > /dev/null || groupadd -r mamonsu
getent passwd mamonsu > /dev/null || \
    useradd -r -g mamonsu -d /var/run/mamonsu -s /sbin/nologin \
    -c "mamonsu monitoring user" mamonsu

mkdir -p /var/run/mamonsu
chown -R mamonsu:mamonsu /var/run/mamonsu

mkdir -p /etc/mamonsu/plugins
touch /etc/mamonsu/plugins/__init__.py

mkdir -p /var/log/mamonsu
chown -R mamonsu:mamonsu /var/log/mamonsu

%preun
/sbin/service mamonsu stop >/dev/null 2>&1
/sbin/chkconfig --del mamonsu

%post
chown -R mamonsu:mamonsu /etc/mamonsu

%changelog
* Sat Dec 14 2024 Maxim Styushin <m.styushin@postgrespro.ru>  - 3.5.10-1
  - Updated checkpoint plugin: added support for new view pg_stat_checkpointer;
  - Updated bgwriter plugin: consider updated view pg_stat_bgwriter in postgres 17;
  - Run zabbix cli tools with latest setuptools installed (>67.7.2);

* Mon Aug 19 2024 Maxim Styushin <m.styushin@postgrespro.ru>  - 3.5.9-1
  - Run on systems with latest setuptools installed (>67.7.2);
  - Drop using dotted user:group specification in RPM pre-install stage;

* Thu Apr 18 2024 Maxim Styushin <m.styushin@postgrespro.ru>  - 3.5.8-1
  - Prepare for python 3.12: remove deprecated distutils imports;

* Fri Apr 5 2024 Maxim Styushin <m.styushin@postgrespro.ru>  - 3.5.7-1
  - added support for Zabbix 6.4 API: handle deprecated parameters for auth request;
  - removed caching of pgsql.connections[max_connections] metric;
  - update default logrotate rules;

* Thu Jan 11 2024 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.5.6-1
  - changed pg_locks plugin metrics names. Warning: custom user-defined triggers and processing functions may be broken if they use item.name parameter.;

* Tue Jun 13 2023 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.5.5-1
  - fixed types mismatch for pgpro_stats and pg_wait_sampling;

* Wed May 17 2023 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.5.4-1
  - fixed privileges for mamonsu role created by bootstrap;

* Thu Mar 16 2023 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.5.3-1
  - removed the owner check for the mamonsu agent.conf file (previously this was not flexible and only required the user "mamonsu");
  - removed metrics that conflict with the native Zabbix agent metrics (only in agent mode, in regular mode it works as usual);
  - added pg_stat_wal queries for native Zabbix agent;
  - fixed native Zabbix agent queries;

* Tue Aug 16 2022 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.5.2-1
  - fixed Statements plugin list of metrics creation;
  - fixed Zabbix API requests to fit new Dashboard Template section rules;
  - fixed Replication plugin metrics - null values are now taken into account;
  - added new autovacuum utilization metrics: instant and average per 5, 15 and 30 minutes;
  - moved plugin custom parameters to Zabbix Macros;

* Fri Jul 29 2022 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.5.1-1
  - fixed delta speed metrics evaluation;

* Wed Jul 6 2022 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.5.0-1
  - divided Instance Rate graph into two graphs - Blocks Rate, Transactions Rate;
  - divided XLOG plugin into two plugins - WAL, Replication;
  - changed 'pg_wait_sampling' plugin name to 'Wait Sampling';
  - changed 'pg_stat_statements' plugin name to 'Statements';
  - changed default agent.conf file permissions: now it read/write only for mamonsu user;
  - added new Replication plugin metrics: Send Lag, Receive Lagadded pgpro_stats support to PostgresPro cluster (automatic switch from pg_stat_statements and pg_wait_sampling);
  - added new bootstrap features: now the '-x' option also configures pg_stat_statements, pg_wait_sampling and pgpro_stats extensions;
  - added custom schema check for pg_stat_statements, pg_wait_sampling and pgpro_stats extensions;
  - added new lock types to the Wait Sampling plugin to fit PostgreSQL 10+: Extension Locks, Client Locks, Other Locks (e.g. IPC, Timeout, IO), Autovacuum Locks, Logical Replication Locks;
  - added new 'System Free/Used Memory' graph;
  - added new active locking queries feature to the report tool;
  - replaced 'System Memory Overview' graph with 'System Free/Used Memory' in dashboards;
  - fixed Statements plugin items generation for native zabbix agent;
  - fixed Rollbacks item delta type;
  - fixed WAL metrics delta types;
  - fixed PostgreSQL Uptime trigger;
  - improved Replication metrics evaluation algorithm;
  - unified Zabbix objects names;
  - unified config file sections and parameters names;
  - set new color scheme;

* Mon Feb 21 2022 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.4.0-1
  - added Server Version metric;
  - added Available Memory metric;
  - fixed native Zabbix Agent user parameters format;
  - added new Mamonsu zabbix tool: 'mamonsu zabbix dashboard upload' for Zabbix 6.0+;

* Wed Feb 2 2022 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.3.1-1
  - fixed logrotate script;
  - added Server Mode metric and trigger;

* Mon Jan 17 2022 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.3.0-1
  - fixed auxiliary extension schema search;
  - fixed WAL metrics definition for native Zabbix agent;
  - upgraded Autovacuum and Connection metrics for PG 10+: now it is evaluating using pg_stat_activity.backend_type which makes the calculation more accurate;
  - added new Other Connections metric for PG 10+ to count metrics like auxiliary extension backends;
  - added new configuration parameter to the [zabbix] section: timeout (in seconds);
  - fixed Plugin Errors metric time interval to fit default '60 seconds' value;
  - fixed Slave Replication Lag metric to exclude master server from calculation;

* Mon Dec 13 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.2.1-1
  - fixed Non-active Replication Slots trigger syntax;
  - upgraded Archive Queue Size and Archive Queue Length metrics to ignore non-standard WAL files (e.g. XXX.history);
  - upgraded template syntax to fit Zabbix 3.0+;

* Fri Nov 26 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.2.0-1
  - added new Invalid Indexes metric and trigger to Databases discovery rule;
  - added version number output to log;
  - fixed template syntax;
  - fixed Archive plugin to fit PostgreSQL 10 or lower;
  - fixed Cache Hit Ratio and Sync Duty Zabbix item formula;

* Mon Nov 8 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.1.2-1
  - fixed Files Need To Archivee and Size Of Files Need To Archive evaluation;

* Wed Nov 3 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.1.1-1
  - fixed template generation for Windows platform;
  - added System screen for Windows platform;

* Tue Oct 19 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.1.0-1
  - fixed unknown options check in mamonsu tools;
  - fixed item units with Speed Per Second delta;
  - fixed Walreceiver Lag items name generation;
  - fixed item Total Replication Lag delta evaluation;
  - fixed slave replication lag evaluation;
  - set 'dbname' bootstrap parameter required, added default value from config file;
  - fixed extension functions calling without special mamonsu user and schema;
  - refactoring;

* Mon Oct 11 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.0.2-1
  - fixed Archive Command bootstrap functions;
  - fixed Archive Command plugin compability with PostgreSQL 9.6 and lower;
  - added GitHub Actions CI/CD scripts - now you can build and test Mamonsu by yourself without special instruments;
  - fixed PostgreSQL 14 metrics delta;

* Mon Sep 6 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.0.1-1
  - fixed 'PostgreSQL: Archive Command archive status' graph y axis
  - fixed bootstrap -x option: now it checks installed extensions
  - fixed 'pgsql.count_files_to_archive' and 'pgsql.size_files_to_archive' items: now their evaluation depending on type of server (master or replica)

* Mon Aug 16 2021 Alexandra Kuznetsova <a.kuznetsova@postgrespro.ru>  - 3.0.0-1
  - change template name to 'Mamonsu PostgreSQL [PLATFORM]'
  - change metric name 'PostgreSQL transactions: total' to 'PostgreSQL transactions: committed'
  - fix Cache Hit Ratio metric calculating
  - fix ArchiveCommand plugin metrics calculating
  - fix Zabbix API support
  - add PostgreSQL 14 support (pg_stat_statements_info, pg_stat_wal metrics)
  - add new graphs: PostgreSQL bgwriter buffers, PostgreSQL bgwriter write/sync, PostgreSQL checkpoints count, PostgreSQL checkpoints write/sync
  - add Zabbix screens (Overview, PostgreSQL Locks, PostgreSQL WAL, PostgreSQL Instance, PostgreSQL Transactions, System)
  - add new mamonsu boostrap option: '-x/--create-extensions' for optional extensions creation
  - add new mamonsu bootstrap features: boostrap by default creates mamonsu user mamonsu/mamonsu, bootstrap by default creates mamonsu own schema 'mamonsu'
  - rm graphs with only one metric

* Wed May 19 2021 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.7.1-1
- rm metric to count children of PostgreSQL parent pid

* Mon Apr 26 2021 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.7.0-1
- update bootstrap
- fix ArchiveCommand plugin
- add metric and trigger to count non-active replication slots
- add metric to count children of PostgreSQL parent pid

* Tue Nov 24 2020 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.6.2-1
- update bootstrap for 9.5, 9.6 versions
- update packaging for Windows

* Fri Nov 20 2020 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.6.1-1
- update bootstrap option input parameters

* Tue Nov 17 2020 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.6.0-1
- update xlog plugin
- add support for PostgreSQL 13
- add plugin memory_leak_diagnostic
- add plugin relations_size

* Mon Aug 17 2020 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.5.1-1
- update pg8000 driver
- drop relations_size plugin
- redirect log messages for mamonsu agent to log fle
- fix pg_probackup trigger

* Fri Jul 31 2020 Alexander Popov <a.popov@postgrespro.ru>  - 2.5.0-1
- drop python2 support
- add old templates for mamonsu and zabbix-agent
- add new plugin: pg_probackup
- add new plugin: relations_size
- add new plugin: prepared_transaction

* Tue May 26 2020 Alexander Popov <a.popov@postgrespro.ru>  - 2.4.5-1
- added checksum_failures metric in Instance plugin for Postgresql 12
- changed PG version support in commands:
	mamonsu export zabbix-parameters
	mamonsu export zabbix-template
	mamonsu export template <file>
	mamonsu export zabbix-template
- update help message for 'mamonsu export'

* Thu Feb 20 2020 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.4.4-1
- change command name for uploading metrics from file (written by mamonsu /var/log/mamonsu/localhost.log, [metric_log] parameter in agent.conf file) to Zabbix Server
- update help message for 'upload' function

* Fri Feb 14 2020 Daria Vilkova <d.vilkova@postgrespro.ru>  - 2.4.3-1
- display postgres connections parameters in log
- add support for Zabbix 4.4 Server
- new feature: export metrics from file (written by mamonsu /var/log/mamonsu/localhost.log, [metric_log] to parameter in agent.conf file) to Zabbix Server

* Mon Jan 20 2020 Grigory Smolkin <g.smolkin@postgrespro.ru> - 2.4.2-1
- fix longest running xact metric
- fixes for python 3

* Tue Sep 3 2019 Daria Vilkova <d.vilkova@postgrespro.ru> - 2.4.1-1
-  add trigger for pgsql.ping

* Thu Aug 22 2019 Daria Vilkova <d.vilkova@postgrespro.ru> - 2.4.0-1
- add zabbix-agent template and configuration file export,
- add new types of connections in "connections" plugin,
- add modification of interval for metric gather,
- add new plugin: archive_command,
- fix oldest transaction time instead of oldest query time and exclude excess processes from a query in "oldest" plugin

* Thu Feb 15 2018 Grigory Smolkin <g.smolkin@postgrespro.ru> - 2.3.4-1
- Connections states fix, cfs compression ratio fix

* Tue Dec 12 2017 Grigory Smolkin <g.smolkin@postgrespro.ru> - 2.3.3-1
- PostgreSQL 10 support

* Tue Dec 12 2017 Grigory Smolkin <g.smolkin@postgrespro.ru> - 2.3.2-1
- bootstrap fixes

* Fri Aug 18 2017 Grigory Smolkin <g.smolkin@postgrespro.ru> - 2.3.1-1
- update trigger fork-rate

* Sat Mar 11 2017 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.3.0-1
- linux: fix vfs discovery, change defaults

* Wed Nov 30 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.9-1
- fix password auth

* Mon Nov 28 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.8-1
- fix double connection

* Thu Nov 24 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.7-1
- add new metrics

* Mon Nov 21 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.6-1
- bug fixes: memory and autovacuum plugin

* Fri Nov 18 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.5-1
- memory and cfs plugin fixes

* Thu Nov 17 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.4-1
- add cfs compression plugin

* Tue Nov 15 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.1-1
- improve report tool

* Thu Nov 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.2.0-1
- change default item type to 'Zabbix trapper'

* Mon Oct 31 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.8-1
- improve report

* Thu Oct 27 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.7-1
- disable color for report tool if not have tty

* Thu Oct 27 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.6-1
- improve report tool

* Mon Oct 24 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.5-1
- pg_locks fixes

* Mon Oct 24 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.3-1
- add pg_locks plugin

* Mon Oct 24 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.2-1
- fix checkpointer metrics

* Mon Oct 24 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.1-1
- fix log messages, postinstal

* Sun Oct 23 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.1.0-1
- fix recovery detection

* Sun Oct 23 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.9-1
- improve checkpointer plugin

* Sun Oct 23 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.8-1
- new plugin: agent memory monitoring

* Sun Oct 23 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.7-1
- close unused connection

* Sat Oct 22 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.6-1
- add new plugin

* Thu Oct 20 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.5-1
- report encoding fixes

* Thu Oct 20 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.4-1
- more log in test select

* Thu Oct 20 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.3-1
- fix pg_buffercache plugin

* Wed Oct 19 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.2-1
- fix security issue for pg_buffercache plugin: add to bootstrap

* Wed Oct 19 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.1-1
- add pg_buffercahe plugin

* Mon Oct 17 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 2.0.0-1
- fix mamonsu tune

* Mon Oct 17 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.9-1
- improve mamonsu tune

* Sun Oct 16 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.8-1
- improve mamonsu bootstrap

* Fri Oct 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.7-1
- update template

* Fri Oct 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.6-1
- delay renamed to bootstrap, fix bootstrap detection

* Fri Oct 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.5-1
- fix pgsql plugin replication lag

* Fri Oct 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.4-1
- add metric: count of xlog files

* Fri Oct 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.3-1
- mamonsu deploy

* Thu Oct 13 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.2-1
- improve tune

* Thu Oct 13 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.1-1
- improve report

* Thu Oct 13 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.9.0-1
- improve report

* Wed Oct 12 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.9-1
- improve report, fix disable plugin in config

* Fri Oct 7 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.8-1
- improve external plugins

* Fri Oct 7 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.7-1
- improve external plugins

* Thu Oct 6 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.6-1
- fix config in external plugins

* Thu Oct 6 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.5-1
- every plugin can enabled/disabled via config

* Thu Oct 6 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.4-1
- simply plugin config

* Tue Oct 4 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.3.1
- simple daemonize

* Tue Oct 4 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.2-1
- improve tune tool

* Mon Oct 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.1-1
- improve pg_wait_samping

* Mon Oct 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.8.0-1
- add pg_wait_samping

* Mon Oct 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.7.5-1
- improve template

* Mon Oct 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.7.5-1
- fix tune

* Mon Oct 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.7.4-1
- improve zabbix template

* Mon Oct 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.7.3-1
- improve pg_stat_statement plugin

* Fri Sep 30 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.7.2-1
- add pg_stat_statement plugin

* Fri Sep 30 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.7.1-1
- disk-stat plugin problem with sizes > 1Tb

* Fri Sep 30 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.7.0-1
- windows fixes

* Thu Sep 29 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.9-1
- template fixes

* Thu Sep 29 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.8-1
- improve mamonsu tune

* Thu Sep 29 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.7-1
- postgresql pool tune

* Wed Sep 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.6-1
- improve mamonsu tune

* Wed Sep 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.4-1
- improve mamonsu report

* Fri Sep 2 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.3-1
- improve mamonsu report

* Fri Sep 2 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.2-1
- mamonsu zabbix fixes for python3

* Tue Aug 30 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.1-1
- mamonsu agent fixes for python3

* Mon Aug 29 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.6.0-1
- Analog of zabbix_get

* Sat Aug 27 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.5.1-1
- Runner fixes

* Fri Aug 26 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.5.0-1
- Zabbix tool feature

* Thu Aug 25 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.4.4-1
- Uptime plugin fixes

* Thu Aug 25 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.4.2-1
- Net plugin fixes

* Mon Aug 22 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.4.1-1
- Report fixes

* Mon Aug 22 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.3.4-1
- New system plugins

* Sun Aug 21 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.3.3-1
- New system plugins

* Sun Aug 21 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.3.2-1
- AutoTune and FirstLook improvements

* Fri Aug 19 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.3.1-1
- import template fix

* Fri Aug 19 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.3.0-1
- enable pgsql plugins by default

* Thu Aug 18 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.2.1-1
- report fixes

* Thu Aug 18 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.2.0-1
- metric fixes

* Thu Aug 11 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.1.0-1
- log rotation by size

* Thu Aug 11 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.0.1-1
- metric corrections

* Wed Aug 10 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 1.0.0-1
- metric log

* Thu Jul 21 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.7.0-1
- metric log

* Sun Jul 17 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.6.5-2
- fix logrotate

* Tue Jul 12 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.6.5-1
- fix replica metrics

* Tue Jul 12 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.6.4-1
- fixes

* Tue Jul 12 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.6.3-1
- fix replica metrics

* Fri Jul 8 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.6.2-1
- mamonsu report improve

* Wed Jul 6 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.6.1-1
- Autotune PostgreSQL config

* Mon Jul 4 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.6.0-1
- Autotune PostgreSQL config

* Tue Jun 28 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.5.1-1
- First look fixes

* Mon Jun 27 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.5.0-1
- Add first look tools

* Tue Jun 21 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.4.1-1
- Fix plugins

* Tue Jun 21 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.4.0-1
- Auto host fea

* Tue Jun 21 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.3.2-1
- Fix metric name

* Mon Jun 6 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.3.1-1
- fixes

* Mon Jun 6 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.3.0-1
- additional cpu plugins
- additional vfs plugins

* Fri Jun 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.2.1-1
- fixes for binary log

* Fri Jun 3 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.2.0-1
- Zabbix binary log

* Thu Jun 2 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.1.1-1
- Update messages

* Thu Jun 2 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.1.0-1
- Plugins: nodata, plugin errors

* Mon May 23 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.11-1
- Add replication lag.
- Fixes in frozen.

* Sat May 14 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.10-1
- User plugins fixes.

* Fri Apr 8 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.9-1
- User plugins support.

* Fri Mar 18 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.8-1
- Zabbix 3.0 support.

* Thu Mar 17 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.7-1
- Bug fixes.

* Tue Feb 9 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.6-1
- Fix init scripts.

* Tue Feb 2 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.5-1
- Fixes.

* Mon Feb 1 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.4-1
- Fixes.

* Mon Feb 1 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.3-1
- Keep alive log, socket connection.

* Sat Jan 30 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.2-1
- Changes in init.

* Fri Jan 29 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.1-1
- Initial release.
