#
# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

# The goal here is to have main, userspace, package built once with
# simple release number, and only rebuild kernel packages with kernel
# version as part of release number, without the need to bump release
# with every kernel change.
%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	4
%define		pname	linux-fusion
Summary:	Fusion and One Linux kernel modules
Summary(pl.UTF-8):	Moduły Fusion i One dla jądra Linuksa
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	9.0.3
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	GPL v2+
Group:		Base/Kernel
Source0:	http://www.directfb.org/downloads/Core/linux-fusion/%{pname}-%{version}.tar.xz
# Source0-md5:	5799f52ec656cdd3da592c94a6262199
Patch0:		linux-3.19.patch
URL:		http://www.directfb.org/
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}}
BuildRequires:	rpmbuild(macros) >= 1.701
BuildRequires:	sed >= 4.0
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Fusion and One Linux kernel modules.

%description -l pl.UTF-8
Moduły Fusion i One dla jądra Linuksa.

%package devel
Summary:	Header file for Fusion device
Summary(pl.UTF-8):	Plik nagłówkowy dla urządzenia Fusion
Group:		Development/Libraries
Requires:	linux-libc-headers

%description devel
Header file for Fusion device.

%description devel -l pl.UTF-8
Plik nagłówkowy dla urządzenia Fusion.

%package -n linux-one-devel
Summary:	Header file for One IPC device
Summary(pl.UTF-8):	Plik nagłówkowy dla urządzenia IPC One
Group:		Development/Libraries
Requires:	linux-libc-headers

%description -n linux-one-devel
Header file for One IPC device.

Linux One is the new IPC API used by Coma.

%description -n linux-one-devel -l pl.UTF-8
Plik nagłówkowy dla urządzenia IPC One.

Linux One to nowe API IPC wykorzystywane przez Comę.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-char-fusion\
Summary:	Fusion module for Linux kernel\
Summary(pl.UTF-8):	Moduł Fusion dla jądra Linuksa\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-char-fusion\
Fusion module for Linux kernel.\
\
%description -n kernel%{_alt_kernel}-char-fusion -l pl.UTF-8\
Moduł Fusion dla jądra Linuksa.\
\
%post	-n kernel%{_alt_kernel}-char-fusion\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-char-fusion\
%depmod %{_kernel_ver}\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-char-fusion\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/kernel/drivers/char/fusion.ko*\
%endif\
\
%package -n kernel%{_alt_kernel}-misc-one\
Summary:	One IPC module for Linux kernel\
Summary(pl.UTF-8):	Moduł IPC One dla jądra Linuksa\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-misc-one\
One IPC module for Linux kernel.\
\
Linux One is the new IPC API used by Coma.\
\
%description -n kernel%{_alt_kernel}-misc-one -l pl.UTF-8\
Moduł IPC One dla jądra Linuksa.\
\
Linux One to nowe API IPC wykorzystywane przez Comę.\
\
%post	-n kernel%{_alt_kernel}-misc-one\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-misc-one\
%depmod %{_kernel_ver}\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-misc-one\
%defattr(644,root,root,755)\
/lib/modules/%{_kernel_ver}/misc/linux-one.ko*\
%endif\
%{nil}

%define build_kernel_pkg()\
# NOTE: build_kernel_modules (as of rpm macros 1.649) doesn't allow line breaking\
%build_kernel_modules -C linux/drivers/char/fusion -m fusion FUSIONCORE=single\
%build_kernel_modules -C one -m linux-one ONECORE=single\
%install_kernel_modules -D installed -m linux/drivers/char/fusion/fusion -d kernel/drivers/char\
%install_kernel_modules -D installed -m  one/linux-one -d misc\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}
%patch0 -p1

%{__sed} -i -e 's/^obj-[^ ]*/obj-m/' linux/drivers/char/fusion/Makefile-2.6
%{__sed} -i -e 's/^obj-[^ ]*/obj-m/' one/Makefile-2.6
echo "EXTRA_CFLAGS = -I`pwd`/linux/include -I`pwd`/linux/drivers/char/fusion -I`pwd`/linux/drivers/char/fusion/single" >> linux/drivers/char/fusion/Makefile-2.6
echo "EXTRA_CFLAGS = -I`pwd`/include -I`pwd`/one/single" >> one/Makefile-2.6

ln -sf Makefile-2.6 linux/drivers/char/fusion/Makefile
ln -sf Makefile-2.6 one/Makefile

%build
%{?with_kernel:%{expand:%build_kernel_packages}}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_includedir}/linux
install linux/include/linux/fusion.h $RPM_BUILD_ROOT%{_includedir}/linux
install include/linux/one.h $RPM_BUILD_ROOT%{_includedir}/linux
%endif

%if %{with kernel}
cp -a installed/* $RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%files devel
%defattr(644,root,root,755)
%doc ChangeLog README TODO
%{_includedir}/linux/fusion.h

%files -n linux-one-devel
%defattr(644,root,root,755)
%doc README.linux-one TODO.linux-one
%{_includedir}/linux/one.h
%endif
