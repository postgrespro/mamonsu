Name:           mamonsu
Version:        2.2.4
Release:        1%{?dist}
Summary:        Monitoring agent for PostgreSQL
Group:          Applications/Internet
License:        BSD
Source0:        http://pypi.python.org/packages/source/m/mamonsu/mamonsu-%{version}.tar.gz
Source1:        mamonsu.init
Source2:        mamonsu-logrotate.in
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildArch:      noarch
Requires:       python-setuptools

%description
Monitoring agent for PostgreSQL.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root %{buildroot}
export PYTHONPATH=%{buildroot}%{python_sitelib}

%{__mkdir} -p %{buildroot}/%{_sysconfdir}/%{name}
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/init.d
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/logrotate.d
%{__mkdir} -p %{buildroot}/%{_datarootdir}/%{name}

%{__install} -m 0644 -p packaging/conf/example.conf %{buildroot}/%{_sysconfdir}/%{name}/agent.conf
%{__install} -m 0644 -p packaging/conf/template.xml %{buildroot}/%{_datarootdir}/%{name}/template.xml
%{__install} -m 0644 -p examples/*.py %{buildroot}/%{_datarootdir}/%{name}/
%{__install} -m 0755 -p %{SOURCE1} %{buildroot}/%{_sysconfdir}/init.d/%{name}
%{__install} -m 0644 -p %{SOURCE2} %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}

%files
%doc README.rst
%config(noreplace) %{_sysconfdir}/%{name}/agent.conf
%{python_sitelib}/%{name}/
%{python_sitelib}/%{name}-%{version}*
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
chown mamonsu.mamonsu /var/run/mamonsu

mkdir -p /etc/mamonsu/plugins
touch /etc/mamonsu/plugins/__init__.py

mkdir -p /var/log/mamonsu
chown mamonsu.mamonsu /var/log/mamonsu

%preun
/sbin/service mamonsu stop >/dev/null 2>&1
/sbin/chkconfig --del mamonsu

%changelog
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
