Summary:	OpenVZ containers control utility
Summary(pl.UTF-8):	Narzędzie do zarządzania środowiskiem wirtualnym OpenVZ
Name:		vzctl
Version:	3.0.29.3
Release:	1
License:	GPL
Group:		Base/Kernel
Source0:	http://download.openvz.org/utils/vzctl/%{version}/src/%{name}-%{version}.tar.bz2
# Source0-md5:	e265b60c589a3d3b665608598b43e930
Source1:	pld.conf
Source2:	pld-add_ip.sh
Source3:	pld-del_ip.sh
Source4:	pld-set_hostname.sh
Source5:	vz-pld.in
Source6:	vzeventd-pld.in
Patch0:		%{name}-pld.patch
URL:		http://openvz.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
Requires:	%{name}-lib = %{version}-%{release}
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
# these reqs are for vz helper scripts
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

%define _configdir	%{_sysconfdir}/vz
%define _distconfdir	%{_configdir}/dists
%define _distscriptdir	%{_distconfdir}/scripts

%description
This utility allows system administator to control OpenVZ containers,
i.e. create, start, shutdown, set various options and limits etc.

%description -l pl.UTF-8
Narzędzia vztcl pozwalają kontrolować środowisko wirtualne (kontener)
OpenVZ, jak na przykład: utworzenie, zatrzymanie, wyłączenie kontenera
oraz umożliwia ustawienie opcji i limitów dotyczących kontenera.

%package lib
Summary:	OpenVZ containers control API library
Group:		Libraries

%description lib
OpenVZ containers control API library.

%prep
%setup -q
%patch0 -p1
install %{SOURCE1} etc/dists
install %{SOURCE2} %{SOURCE3} %{SOURCE4} etc/dists/scripts
install %{SOURCE5} %{SOURCE6} etc/init.d

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--enable-bashcomp \
	--enable-logrotate \
	--disable-static

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{cron.d,rc.d/init.d,sysconfig/interfaces}

%{__make} install install-pld \
	vpsconfdir=/etc/sysconfig/vz-scripts \
	DESTDIR=$RPM_BUILD_ROOT

%{__mv} $RPM_BUILD_ROOT/etc/init.d/vz* $RPM_BUILD_ROOT/etc/rc.d/init.d
%{__mv} $RPM_BUILD_ROOT/etc/sysconfig/{network-scripts,interfaces}/ifcfg-venet0

ln -s ../sysconfig/vz-scripts $RPM_BUILD_ROOT%{_configdir}/conf
ln -s ../vz/vz.conf $RPM_BUILD_ROOT/etc/sysconfig/vz

:> $RPM_BUILD_ROOT/etc/cron.d/vz

# .so could go to vzctl-lib-devel, but since we don't have it...
rm -f $RPM_BUILD_ROOT%{_libdir}/libvzctl.{la,so}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/bin/rm -rf /dev/vzctl
/bin/mknod -m 600 /dev/vzctl c 126 0
if [ -f %{_configdir}/vz.conf ]; then
	if ! grep -q "IPTABLES=" %{_configdir}/vz.conf 2>/dev/null; then
		echo 'IPTABLES="ipt_REJECT ipt_tos ipt_limit ipt_multiport iptable_filter iptable_mangle ipt_TCPMSS ipt_tcpmss ipt_ttl ipt_length"' >> %{_configdir}/vz.conf
	fi
fi
/sbin/chkconfig --add vz
/sbin/chkconfig --add vzeventd
%service vzeventd restart "vzeventd service"

%preun
if [ $1 = 0 ]; then
	/sbin/chkconfig --del vz
	/sbin/chkconfig --del vzeventd
fi

%post	lib -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ChangeLog
%config(noreplace) /etc/bash_completion.d/%{name}.sh
%attr(640,root,root) %ghost /etc/cron.d/vz
%attr(754,root,root) /etc/rc.d/init.d/vz*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%attr(755,root,root) /etc/sysconfig/network-scripts/if*-venet
%attr(640,root,root) %config(noreplace,missingok) %verify(not md5 mtime size) /etc/sysconfig/interfaces/ifcfg-venet0
%dir /etc/sysconfig/vz-scripts
%config(missingok) /etc/sysconfig/vz-scripts/ve-*.conf-sample
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/vz-scripts/0.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/vz
%config(noreplace) /etc/udev/rules.d/*-%{name}.rules
%dir %{_configdir}
%dir %{_distconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_distconfdir}/default
%config(noreplace) %{_distconfdir}/distribution.conf-template
%config(noreplace) %{_distconfdir}/*.conf
%dir %{_distscriptdir}
%attr(755,root,root) %config(noreplace) %{_distscriptdir}/*.sh
%config(noreplace) %{_distscriptdir}/functions
%{_configdir}/names
%config(noreplace) %verify(not md5 mtime size) %{_configdir}/*conf
%attr(755,root,root) /sbin/ifup-local
%attr(755,root,root) %{_sbindir}/*send
%attr(755,root,root) %{_sbindir}/vz*
%dir /vz
/vz/[dlt]*
%attr(700,root,root) %dir /vz/[pr]*
/var/lib/vzctl
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*

%files lib
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvzctl-*.so
%attr(755,root,root) %{_libdir}/vzctl
