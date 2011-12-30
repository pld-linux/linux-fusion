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

Summary:	Fusion Linux kernel module
Summary(pl.UTF-8):	Moduł Fusion dla jądra Linuksa
Name:		linux-fusion
Version:	8.7.0
%define		rel	1
Release:	%{rel}
License:	GPL v2+
Group:		Base/Kernel
Source0:	http://www.directfb.org/downloads/Core/linux-fusion/%{name}-%{version}.tar.gz
# Source0-md5:	b93b39711474dd353f93ef08cabdfb8b
URL:		http://www.directfb.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
BuildRequires:	sed >= 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Fusion Linux kernel module.

%description -l pl.UTF-8
Moduł Fusion dla jądra Linuksa.

%package devel
Summary:	Header file for Fusion device
Summary(pl.UTF-8):	Plik nagłówkowy dla urządzenia Fusion
Group:		Development/Libraries
Requires:	linux-libc-headers

%description devel
Header file for Fusion device.

%description devel -l pl.UTF-8
Plik nagłówkowy dla urządzenia Fusion.

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

%prep
%setup -q

sed -i -e 's/^obj-[^ ]*/obj-m/' linux/drivers/char/fusion/Makefile-2.6
echo "EXTRA_CFLAGS = -I`pwd`/linux/include -I`pwd`/linux/drivers/char/fusion -I`pwd`/linux/drivers/char/fusion/single" >> linux/drivers/char/fusion/Makefile-2.6

%build
%if %{with kernel}
cd linux/drivers/char/fusion
ln -sf Makefile-2.6 Makefile
%build_kernel_modules -m fusion \
	FUSIONCORE=single
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_includedir}/linux
install linux/include/linux/fusion.h $RPM_BUILD_ROOT%{_includedir}/linux
%endif

%if %{with kernel}
cd linux/drivers/char/fusion
%install_kernel_modules -m fusion -d kernel/drivers/char
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-char-fusion
%depmod %{_kernel_ver}

%postun	-n kernel-char-fusion
%depmod %{_kernel_ver}

%if %{with userspace}
%files devel
%defattr(644,root,root,755)
%doc ChangeLog TODO
%{_includedir}/linux/fusion.h
%endif

%if %{with kernel}
%files -n kernel-char-fusion
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/char/fusion.ko*
%endif
