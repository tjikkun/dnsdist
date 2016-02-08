%global _hardened_build 1
%global prever alpha2
%if 0%{?fedora}
%global uglify 1
%global luajit 1
%endif
%ifnarch %{power64} || 0%{?rhel} > 7
%global uglify 1
%endif
%ifnarch %{power64}
%if 0%{?rhel} > 6
%global luajit 1
%endif
%endif

Name: dnsdist
Version: 1.0.0
Release: 0.8.%{?prever}%{?dist}
Summary: Highly DNS-, DoS- and abuse-aware loadbalancer
Group: System Environment/Daemons
License: GPLv2
URL: http://dnsdist.org
Source0: http://downloads.powerdns.com/releases/%{name}-%{version}-%{?prever}.tar.bz2

BuildRequires: boost-devel
BuildRequires: libedit-devel
BuildRequires: lua-devel
%if 0%{?luajit}
BuildRequires: luajit-devel
%endif
BuildRequires: readline-devel
%if 0%{?el6} == 0
BuildRequires: libsodium-devel
BuildRequires: systemd-units
%else
BuildRequires: devtoolset-3-gcc-c++
BuildRequires: http-parser
BuildRequires: libuv
%endif
%if 0%{?uglify}
BuildRequires: uglify-js
%endif
%if 0%{?el6}
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
%else
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description
dnsdist is a highly DNS-, DoS- and abuse-aware loadbalancer. Its goal in life
is to route traffic to the best server, delivering top performance to
legitimate users while shunting or blocking abusive traffic.


%prep
%setup -q -n %{name}-%{version}-%{?prever}

%build
%if 0%{?el6}
CC=/opt/rh/devtoolset-3/root/usr/bin/cc
export CC
CXX=/opt/rh/devtoolset-3/root/usr/bin/c++
export CXX
%endif
%configure \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--disable-static \
	--disable-dependency-tracking \
	--disable-silent-rules \
%if 0%{?el6} == 0
	--enable-dnscrypt \
	--enable-libsodium \
%endif
	--with-lua \
%if 0%{?luajit}
	--with-luajit \
%endif
	--enable-unit-tests
rm html/js/*
%if 0%{?uglify}
make min_js
%else
cp src_js/*.js html/js
%endif

make %{?_smp_mflags}
mv dnsdistconf.lua dnsdist.conf.sample

%install
make install DESTDIR=%{buildroot}

%if 0%{?el6}
%{__install} -D -p -m 644 contrib/%{name}.init.centos6 %{buildroot}%{_initrddir}/%{name}
%{__install} -D -p -m 644 contrib/%{name}.default %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%else
# install systemd unit file
%{__install} -D -p -m 644 contrib/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%endif
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}/

%check
make %{?_smp_mflags} check
rm %{buildroot}%{_bindir}/testrunner

%post
%if 0%{?el6}
/sbin/chkconfig --add %{name}
%else
%systemd_post %{name}.service
%endif

%preun
%if 0%{?el6}
if [ "$1" -eq "0" ]; then
  # Package removal, not upgrade
  /sbin/service %{name} stop > /dev/null 2>&1 || :
  /sbin/chkconfig --del %{name}
fi
%else
%systemd_preun %{name}.service
%endif

%postun
%if 0%{?el6}
if [ "$1" -ge "1" ] ; then
  /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi
%else
%systemd_postun_with_restart %{name}.service
%endif

%files
%doc dnsdist.conf.sample
%doc README.md
%license COPYING
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%if 0%{?el6}
%{_initrddir}/%{name}
%{_sysconfdir}/sysconfig/%{name}
%else
%{_unitdir}/%{name}.service
%endif
%dir %{_sysconfdir}/%{name}/


%changelog
* Mon Feb 08 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.8.alpha2
- Add SysV init support for EPEL6

* Mon Feb 08 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.7.alpha2
- Only copy .js files when minify-js is not available

* Mon Feb 08 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.6.alpha2
- PPC on EPEL does not have uglify-js

* Mon Feb 08 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.5.alpha2
- Don't build against luijit on ppc, it is not available there

* Mon Feb 08 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.4.alpha2
- Add sample config file

* Sat Feb 06 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.3.alpha2
- Update to new upstream

* Sun Jan 10 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.2.alpha1
- SPEC fixes for review

* Sun Jan 10 2016 Sander Hoentjen <sander@hoentjen.eu> - 1.0.0-0.1.alpha1
- Initial package
