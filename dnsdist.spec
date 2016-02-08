%global _hardened_build 1
%global prever alpha2

Name: dnsdist
Version: 1.0.0
Release: 0.5.%{?prever}%{?dist}
Summary: Highly DNS-, DoS- and abuse-aware loadbalancer
Group: System Environment/Daemons
License: GPLv2
URL: http://dnsdist.org
Source0: http://downloads.powerdns.com/releases/%{name}-%{version}-%{?prever}.tar.bz2

BuildRequires: boost-devel
BuildRequires: libedit-devel
BuildRequires: libsodium-devel
BuildRequires: lua-devel
%ifnarch %{power64}
BuildRequires: luajit-devel
%endif
BuildRequires: readline-devel
BuildRequires: systemd-units
BuildRequires: uglify-js
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
dnsdist is a highly DNS-, DoS- and abuse-aware loadbalancer. Its goal in life
is to route traffic to the best server, delivering top performance to
legitimate users while shunting or blocking abusive traffic.


%prep
%setup -q -n %{name}-%{version}-%{?prever}

%build
%configure \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--disable-static \
	--disable-dependency-tracking \
	--disable-silent-rules \
	--enable-dnscrypt \
	--enable-libsodium \
	--with-lua \
	--with-luajit \
	--enable-unit-tests
rm html/js/*
make min_js
make %{?_smp_mflags}
mv dnsdistconf.lua dnsdist.conf.sample

%install
make install DESTDIR=%{buildroot}

# install systemd unit file
%{__install} -D -p -m 644 contrib/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%{__install} -d %{buildroot}%{_sysconfdir}/%{name}/

%check
make %{?_smp_mflags} check
rm %{buildroot}%{_bindir}/testrunner

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%doc dnsdist.conf.sample
%doc README.md
%license COPYING
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_unitdir}/%{name}.service
%dir %{_sysconfdir}/%{name}/


%changelog
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
