%define _vzdir /vz
%define _lockdir %{_vzdir}/lock
%define _dumpdir %{_vzdir}/dump
%define _privdir %{_vzdir}/private
%define _rootdir %{_vzdir}/root
%define _cachedir %{_vzdir}/template/cache
%define _veipdir /var/lib/vzctl/veip
%define _pkglibdir %{_libdir}/vzctl
%define _configdir %{_sysconfdir}/vz
%define _scriptdir /usr/share/vzctl/scripts
%define _vpsconfdir /etc/sysconfig/vz-scripts
%define _netdir	/etc/sysconfig/network-scripts
%define _logrdir /etc/logrotate.d
%define _crondir /etc/cron.d
%define _distconfdir %{_configdir}/dists
%define _namesdir %{_configdir}/names
%define _distscriptdir %{_distconfdir}/scripts
%define _udevrulesdir /etc/udev/rules.d
%define _bashcdir /etc/bash_completion.d

Summary:	OpenVZ containers control utility
Summary(pl.UTF-8):	Narzędzie do zarządzania środowiskiem wirtualnym OpenVZ
Name:		vzctl
Version:	3.0.25.1
Release:	0.1
License:	GPL
Group:		Base/Kernel
Source0:	http://download.openvz.org/utils/vzctl/%{version}/src/%{name}-%{version}.tar.bz2
# Source0-md5:	5798ea88d06afff1d6d1bbbfc45899f1
URL:		http://openvz.org/
Requires:	%{name}-lib = %{version}-%{release}
# these reqs are for vz helper scripts
Requires:	/sbin/chkconfig
Requires:	bash
Requires:	ed
Requires:	fileutils
Requires:	gawk
Requires:	grep
Requires:	sed
Requires:	tar
Requires:	vzquota >= 2.7.0-4
# requires for vzmigrate purposes
Suggests:	gawk
Suggests:	openssh
Suggests:	rsync
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This utility allows system administator to control OpenVZ containers,
i.e. create, start, shutdown, set various options and limits etc.

%description -l pl.UTF-8
Narzędzia vztcl pozwalają kontrolować środowisko wirtualne (kontener)
OpenVZ, jak na przykład: utworzenie, zatrzymanie, wyłączenie kontenera
oraz umożliwia ustawienie opcji i limitów dotyczących kontenera.

%package lib
Summary:	OpenVZ containers control API library
Group:		Base/Kernel

%description lib
OpenVZ containers control API library.

%prep
%setup -q

%build
%configure \
	--enable-bashcomp \
	--enable-logrotate \
	--disable-static

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install install-redhat \
	vpsconfdir=%{_vpsconfdir} \
	DESTDIR=$RPM_BUILD_ROOT

ln -s ../sysconfig/vz-scripts $RPM_BUILD_ROOT%{_configdir}/conf
ln -s ../vz/vz.conf $RPM_BUILD_ROOT/etc/sysconfig/vz
# Needed for ghost in files section below
mkdir $RPM_BUILD_ROOT/etc/cron.d/
touch $RPM_BUILD_ROOT/etc/cron.d/vz

# .so could go to vzctl-lib-devel, but since we don't have it...
rm -f $RPM_BUILD_ROOT%{_libdir}/libvzctl.{la,so}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/bin/rm -rf /dev/vzctl
/bin/mknod -m 600 /dev/vzctl c 126 0
if [ -f %{_configdir}/vz.conf ]; then
	if ! grep "IPTABLES=" %{_configdir}/vz.conf >/dev/null 2>&1; then
		echo 'IPTABLES="ipt_REJECT ipt_tos ipt_limit ipt_multiport iptable_filter iptable_mangle ipt_TCPMSS ipt_tcpmss ipt_ttl ipt_length"' >> %{_configdir}/vz.conf
	fi
fi
/sbin/chkconfig --add vz

%preun
if [ $1 = 0 ]; then
	/sbin/chkconfig --del vz
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog
%attr(755,root,root) /etc/rc.d/init.d/vz
%ghost /etc/cron.d/vz
%dir %{_lockdir}
%dir %{_dumpdir}
%dir %attr(700,root,root) %{_privdir}
%dir %attr(700,root,root) %{_rootdir}
%dir %{_cachedir}
%dir %{_veipdir}
%dir %{_configdir}
%dir %{_namesdir}
%dir %{_vpsconfdir}
%dir %{_distconfdir}
%dir %{_distscriptdir}
%dir %{_vzdir}
%attr(755,root,root) %{_sbindir}/*send
%attr(755,root,root) %{_sbindir}/vz*
%attr(755,root,root) %{_scriptdir}/vps*
%{_logrdir}/vzctl
%{_distconfdir}/distribution.conf-template
%{_distconfdir}/default
%attr(755,root,root) %{_distscriptdir}/*.sh
%{_distscriptdir}/functions
%attr(755,root,root) %{_netdir}/if*-venet
%{_netdir}/ifcfg-venet0
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*
%{_udevrulesdir}/*
%{_bashcdir}/*

%config(noreplace) %{_configdir}/vz.conf
%config(noreplace) %{_distconfdir}/*.conf
%config(noreplace) %{_crondir}/vz
%config %{_vpsconfdir}/ve-*.conf-sample
%config %{_vpsconfdir}/0.conf

%attr(777, root, root) %{_sysconfdir}/vz/conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/vz

%files lib
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvzctl-*.so
%dir %{_pkglibdir}
%dir %{_pkglibdir}/scripts
%attr(755,root,root) %{_pkglibdir}/scripts/vps-*
%attr(755,root,root) %{_pkglibdir}/scripts/vzevent-*
%attr(755,root,root) %{_pkglibdir}/scripts/initd-functions
