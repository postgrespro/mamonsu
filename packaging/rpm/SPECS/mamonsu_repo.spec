Summary:	Mamonsu rpm packages
Name:		mamonsu-repo
Version:	1.0.0
Release:	1
Summary:	Repository package for Mamonsu
Group:		Applications/Internet
License:	BSD
Url:		http://postgrespro.ru/

Source0:    http://repo.postgrespro.ru/mamonsu/keys/GPG-KEY-MAMONSU
Source1:    mamonsu.repo

BuildArch:	noarch

%description
This package contains repository configuration and the GPG key for mamonsu rpm packages.

%prep
%setup -q  -c -T
install -pm 644 %{SOURCE0} .
install -pm 644 %{SOURCE1} .

%build

%install
rm -rf $RPM_BUILD_ROOT

#GPG Key
install -Dpm 644 %{SOURCE0} \
    $RPM_BUILD_ROOT%{_sysconfdir}/pki/rpm-gpg/GPG-KEY-MAMONSU

# yum
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d
install -pm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%config(noreplace) /etc/yum.repos.d/*
/etc/pki/rpm-gpg/*

%changelog
* Wed Nov 27 2019 Grigory Smolkin <g.smolkin@postgrespro.ru>
- Initial Package
