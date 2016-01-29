Name:           mamonsu
Version:        0.0.1
Release:        1%{?dist}
Summary:        Active zabbix agent
Group:          Applications/Internet
License:        BSD
Source0:        http://pypi.python.org/packages/source/m/mamonsu/mamonsu-%{version}.tar.gz
Source1:        mamonsu.init
Source2:        mamonsu-logrotate.in
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildArch:      noarch

%description
Zabbix active agent for monitoring PostgreSQL.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root %{buildroot}
export PYTHONPATH=%{buildroot}%{python_sitelib}

mkdir -p %{buildroot}/%{_sysconfdir}/mamonsu
mkdir -p %{buildroot}/%{_sysconfdir}/init.d
mkdir -p %{buildroot}/%{_sysconfdir}/logrotate.d

install -m 0644 -p conf/example.conf %{buildroot}/%{_sysconfdir}/mamonsu/agent.conf
install -m 0755 -p %{SOURCE1} %{buildroot}/%{_sysconfdir}/init.d/mamonsu
install -m 0644 -p %{SOURCE2} %{buildroot}/%{_sysconfdir}/logrotate.d/mamonsu

%files
%doc README.rst
%{python_sitelib}/%{name}/
%{python_sitelib}/%{name}-%{version}*
%{_sysconfdir}/mamonsu
%{_sysconfdir}/init.d/mamonsu
%{_sysconfdir}/logrotate.d/mamonsu
%{_bindir}/mamonsu

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group mamonsu > /dev/null || groupadd -r mamonsu
getent passwd mamonsu > /dev/null || \
    useradd -r -g mamonsu -d /var/run/mamonsu -s /sbin/nologin \
    -c "mamonsu monitoring user" mamonsu

mkdir -p /var/run/mamonsu
chown mamonsu.mamonsu /var/run/mamonsu

mkdir -p /var/log/mamonsu
chown mamonsu.mamonsu /var/log/mamonsu

%post
/sbin/chkconfig --add mamonsu || :

%preun
/sbin/service mamonsu stop >/dev/null 2>&1
/sbin/chkconfig --del mamonsu

%changelog
* Fri Jan 29 2016 Dmitry Vasilyev <d.vasilyev@postgrespro.ru> - 0.0.1-1
- Initial release.
