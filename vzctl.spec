%define _initddir %_sysconfdir/init.d
%define _vzdir /vz
%define _lockdir %{_vzdir}/lock
%define _dumpdir %{_vzdir}/dump
%define _privdir %{_vzdir}/private
%define _rootdir %{_vzdir}/root
%define _cachedir %{_vzdir}/template/cache
%define _veipdir /var/lib/vzctl/veip
%define _pkglibdir %_libdir/vzctl
%define _configdir %_sysconfdir/vz
%define _scriptdir /usr/share/vzctl/scripts
%define _vpsconfdir %_sysconfdir/sysconfig/vz-scripts
%define _netdir	%_sysconfdir/sysconfig/network-scripts
%define _logrdir %_sysconfdir/logrotate.d
%define _crondir %{_configdir}/cron
%define _distconfdir %{_configdir}/dists
%define _namesdir %{_configdir}/names
%define _distscriptdir %{_distconfdir}/scripts
%define _udevrulesdir %_sysconfdir/udev/rules.d
%define _bashcdir %_sysconfdir/bash_completion.d


Summary:	Virtual Environments control utility
Name:		vzctl
Version:	3.0.22
Release:	0.1
License:	GPL
Group:		Base/Kernel
Source0:	http://download.openvz.org/utils/vzctl/%{version}/src/%{name}-%{version}.tar.bz2
# Source0-md5:	d02fdecaeaa1327c08ba5d980383cafa
ExclusiveOS:	Linux
URL:		http://openvz.org/
Requires:	vzkernel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
# these reqs are for vz helper scripts
Requires:	/sbin/chkconfig
Requires:	bash
Requires:	ed
Requires:	fileutils
Requires:	gawk
Requires:	grep
Requires:	sed
Requires:	tar
Requires:	vzctl-lib = %{version}-%{release}
Requires:	vzquota >= 2.7.0-4

# requires for vzmigrate purposes
Requires:	gawk
Requires:	openssh
Requires:	rsync

%description
This utility allows system administator to control Virtual
Environments, i.e. create, start, shutdown, set various options and
limits etc.

%prep
%setup -q

%build
CFLAGS="%{rpmcflags}" %configure \
	--enable-bashcomp \
	--enable-logrotate \
	--disable-static
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT vpsconfdir=%{_vpsconfdir} install install-redhat
ln -s ../sysconfig/vz-scripts $RPM_BUILD_ROOT%{_configdir}/conf
ln -s ../vz/vz.conf $RPM_BUILD_ROOT/etc/sysconfig/vz
# This could go to vzctl-lib-devel, but since we don't have it...
rm -f  $RPM_BUILD_ROOT%_libdir/libvzctl.{la,so}
# Needed for ghost in files section below
mkdir $RPM_BUILD_ROOT/etc/cron.d/
touch $RPM_BUILD_ROOT/etc/cron.d/vz

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_initddir}/vz
%ghost /etc/cron.d/vz
%dir %{_lockdir}
%dir %{_dumpdir}
%dir %attr(700,root,root) %{_privdir}
%dir %attr(700,root,root) %{_rootdir}
%dir %{_cachedir}
%dir %{_veipdir}
%dir %{_configdir}
%dir %{_crondir}
%dir %{_namesdir}
%dir %{_vpsconfdir}
%dir %{_distconfdir}
%dir %{_distscriptdir}
%dir %{_vzdir}
%attr(755,root,root) %{_sbindir}/vzctl
%attr(755,root,root) %{_sbindir}/arpsend
%attr(755,root,root) %{_sbindir}/ndsend
%attr(755,root,root) %{_sbindir}/vzsplit
%attr(755,root,root) %{_sbindir}/vzlist
%attr(755,root,root) %{_sbindir}/vzmemcheck
%attr(755,root,root) %{_sbindir}/vzcpucheck
%attr(755,root,root) %{_sbindir}/vznetcfg
%attr(755,root,root) %{_sbindir}/vzcalc
%attr(755,root,root) %{_sbindir}/vzpid
%attr(755,root,root) %{_sbindir}/vzcfgvalidate
%attr(755,root,root) %{_sbindir}/vzmigrate
%attr(755,root,root) %{_scriptdir}/vpsreboot
%attr(755,root,root) %{_scriptdir}/vpsnetclean
%{_logrdir}/vzctl
%{_distconfdir}/distribution.conf-template
%{_distconfdir}/default
%attr(755,root,root) %{_distscriptdir}/*.sh
%{_distscriptdir}/functions
%attr(755,root,root) %{_netdir}/ifup-venet
%attr(755,root,root) %{_netdir}/ifdown-venet
%{_netdir}/ifcfg-venet0
%attr(644, root, root) %{_mandir}/man8/vzctl.8.*
%attr(644, root, root) %{_mandir}/man8/vzmigrate.8.*
%attr(644, root, root) %{_mandir}/man8/arpsend.8.*
%attr(644, root, root) %{_mandir}/man8/vzsplit.8.*
%attr(644, root, root) %{_mandir}/man8/vzcfgvalidate.8.*
%attr(644, root, root) %{_mandir}/man8/vzmemcheck.8.*
%attr(644, root, root) %{_mandir}/man8/vzcalc.8.*
%attr(644, root, root) %{_mandir}/man8/vzpid.8.*
%attr(644, root, root) %{_mandir}/man8/vzcpucheck.8.*
#%attr(644, root, root) %{_mandir}/man8/vzcheckovr.8.*
%attr(644, root, root) %{_mandir}/man8/vzlist.8.*
%attr(644, root, root) %{_mandir}/man5/vps.conf.5.*
%attr(644, root, root) %{_mandir}/man5/vz.conf.5.*
%attr(644, root, root) %{_udevrulesdir}/*
%attr(644, root, root) %{_bashcdir}/*

%config(noreplace) %{_configdir}/vz.conf
%config(noreplace) %{_distconfdir}/*.conf
%config(noreplace) %{_crondir}/vz
%config %{_vpsconfdir}/ve-vps.basic.conf-sample
%config %{_vpsconfdir}/ve-light.conf-sample
%config %{_vpsconfdir}/0.conf

%attr(777, root, root) %{_sysconfdir}/vz/conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/vz

%post
/bin/rm -rf /dev/vzctl
/bin/mknod -m 600 /dev/vzctl c 126 0
if [ -f %{_configdir}/vz.conf ]; then
	if ! grep "IPTABLES=" %{_configdir}/vz.conf >/dev/null 2>&1; then
		echo 'IPTABLES="ipt_REJECT ipt_tos ipt_limit ipt_multiport iptable_filter iptable_mangle ipt_TCPMSS ipt_tcpmss ipt_ttl ipt_length"' >> %{_configdir}/vz.conf
	fi
fi
/sbin/chkconfig --add vz > /dev/null 2>&1

if [ -f %{_sysconfdir}/SuSE-release ]; then
	NET_CFG='ifdown-venet ifup-venet'
	if ! grep -q -E "^alias venet0" /etc/modprobe.conf; then
		echo "alias venet0 vznet" >> /etc/modprobe.conf
	fi
	ln -f /etc/sysconfig/network-scripts/ifcfg-venet0 /etc/sysconfig/network/ifcfg-venet0
	for file in ${NET_CFG}; do
		ln -sf /etc/sysconfig/network-scripts/${file} /etc/sysconfig/network/scripts/${file}
	done
fi

%preun
if [ $1 = 0 ]; then
	/sbin/chkconfig --del vz >/dev/null 2>&1
fi

%package lib
Summary:	Virtual Environments control API library
Group:		Base/Kernel

%description lib
Virtual Environments control API library

%files lib
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvzctl-*.so
%dir %{_pkglibdir}
%dir %{_pkglibdir}/scripts
%attr(755,root,root) %{_pkglibdir}/scripts/vps-stop
%attr(755,root,root) %{_pkglibdir}/scripts/vps-functions
%attr(755,root,root) %{_pkglibdir}/scripts/vps-net_add
%attr(755,root,root) %{_pkglibdir}/scripts/vps-net_del
%attr(755,root,root) %{_pkglibdir}/scripts/vps-create
