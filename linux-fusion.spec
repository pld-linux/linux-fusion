#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)
#
%if %{without kernel}
%undefine	with_dist_kernel
%endif

Summary:	Fusion and One Linux kernel modules
Summary(pl.UTF-8):	Moduły Fusion i One dla jądra Linuksa
Name:		linux-fusion
Version:	9.0.0
%define		rel	1
Release:	%{rel}
License:	GPL v2+
Group:		Base/Kernel
Source0:	http://www.directfb.org/downloads/Core/linux-fusion/%{name}-%{version}.tar.gz
# Source0-md5:	4199617ed8ba205da52fedfb862e4507
URL:		http://www.directfb.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRequires:	sed >= 4.0
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

%package -n kernel-char-fusion
Summary:	Fusion module for Linux kernel
Summary(pl.UTF-8):	Moduł Fusion dla jądra Linuksa
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-char-fusion
Fusion module for Linux kernel.

%description -n kernel-char-fusion -l pl.UTF-8
Moduł Fusion dla jądra Linuksa.

%package -n kernel-one
Summary:	One IPC module for Linux kernel
Summary(pl.UTF-8):	Moduł IPC One dla jądra Linuksa
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-one
One IPC module for Linux kernel.

Linux One is the new IPC API used by Coma.

%description -n kernel-one -l pl.UTF-8
Moduł IPC One dla jądra Linuksa.

Linux One to nowe API IPC wykorzystywane przez Comę.

%prep
%setup -q

%{__sed} -i -e 's/^obj-[^ ]*/obj-m/' linux/drivers/char/fusion/Makefile-2.6
%{__sed} -i -e 's/^obj-[^ ]*/obj-m/' one/Makefile-2.6
echo "EXTRA_CFLAGS = -I`pwd`/linux/include -I`pwd`/linux/drivers/char/fusion -I`pwd`/linux/drivers/char/fusion/single" >> linux/drivers/char/fusion/Makefile-2.6
echo "EXTRA_CFLAGS = -I`pwd`/include -I`pwd`/one/single" >> one/Makefile-2.6

%build
%if %{with kernel}
cd linux/drivers/char/fusion
ln -sf Makefile-2.6 Makefile
# NOTE: build_kernel_modules (as of rpm macros 1.649) doesn't allow line breaking
%build_kernel_modules -m fusion FUSIONCORE=single
cd ../../../../one
ln -sf Makefile-2.6 Makefile
%build_kernel_modules -m linux-one ONECORE=single
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_includedir}/linux
install linux/include/linux/fusion.h $RPM_BUILD_ROOT%{_includedir}/linux
install include/linux/one.h $RPM_BUILD_ROOT%{_includedir}/linux
%endif

%if %{with kernel}
cd linux/drivers/char/fusion
%install_kernel_modules -m fusion -d kernel/drivers/char
cd ../../../../one
%install_kernel_modules -m linux-one -d kernel
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-char-fusion
%depmod %{_kernel_ver}

%postun	-n kernel-char-fusion
%depmod %{_kernel_ver}

%post	-n kernel-one
%depmod %{_kernel_ver}

%postun	-n kernel-one
%depmod %{_kernel_ver}

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

%if %{with kernel}
%files -n kernel-char-fusion
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/char/fusion.ko*

%files -n kernel-one
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/linux-one.ko*
%endif
