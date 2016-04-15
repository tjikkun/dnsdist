%global _hardened_build 1
%global prever beta1
%ifarch %{nodejs_arches}
%global uglify 1
%endif


Name: dnsdist
Version: 1.0.0
Release: 0.10.%{?prever}%{?dist}
Summary: Highly DNS-, DoS- and abuse-aware loadbalancer
Group: System Environment/Daemons
License: GPLv2
URL: http://dnsdist.org
Source0: http://downloads.powerdns.com/releases/%{name}-%{version}-%{?prever}.tar.bz2

BuildRequires: boost-devel
BuildRequires: libedit-devel
BuildRequires: libsodium-devel
BuildRequires: lua-devel
%ifnarch %{power64} aarch64 s390 s390x
BuildRequires: luajit-devel
%else
BuildRequires: lua-devel
%endif
BuildRequires: protobuf-devel
BuildRequires: re2-devel
BuildRequires: readline-devel
BuildRequires: systemd-devel
BuildRequires: systemd-units
%if 0%{?uglify}
BuildRequires: uglify-js
%endif
Requires(post): systemd
Requires(preun): shadow-utils
Requires(preun): systemd
Requires(postun): systemd

%description
dnsdist is a highly DNS-, DoS- and abuse-aware loadbalancer. Its goal in life
is to route traffic to the best server, delivering top performance to
legitimate users while shunting or blocking abusive traffic.


%prep
%setup -q -n %{name}-%{version}-%{?prever}

# run as dnsdist user
sed -i '/^ExecStart/ s/dnsdist/dnsdist -u dnsdist -g dnsdist/' dnsdist.service.in

%build
%configure \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--disable-static \
	--disable-dependency-tracking \
	--disable-silent-rules \
	--enable-dnscrypt \
	--enable-libsodium \
%ifnarch %{power64} aarch64 s390 s390x
	--with-luajit \
%else
	--with-lua \
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

# install systemd unit file
install -D -p -m 644 contrib/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -d %{buildroot}%{_sysconfdir}/%{name}/

%pre
getent group dnsdist >/dev/null || groupadd -r dnsdist
getent passwd dnsdist >/dev/null || \
    useradd -r -g dnsdist -d / -s /sbin/nologin \
    -c "dnsdist user" dnsdist
exit 0

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
* Fri Apr 15 2016 Ruben Kerkhof <ruben@rubenkerkhof.com> - 1.9.9-0.10.beta1
- Upstream released new version
- Run as dnsdist user / group (#1326623)
- Enable support for libre2 and protobufs
- Fix systemd detection
- Only build with lua if luajit is not available

* Tue Mar 08 2016 Ruben Kerkhof <ruben@rubenkerkhof.com> 1.0.0-0.9.alpha2
- Rebuild for libsodium soname bump

* Tue Feb 23 2016 Peter Robinson <pbrobinson@fedoraproject.org> 1.0.0-0.8.alpha2
- Add aarch64/s390(x) to luajit excludes
- uglify-js available on nodejs arches so use that define

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
