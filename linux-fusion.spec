#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)
#
%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		_rel	1
Summary:	Fusion Linux kernel module
Summary(pl):	Modu³ Fusion dla j±dra Linuksa
Name:		linux-fusion
Version:	3.0
Release:	%{_rel}
License:	GPL v2+
Group:		Base/Kernel
Source0:	http://www.directfb.org/downloads/Core/%{name}-%{version}.tar.gz
# Source0-md5:	8f666bab9a9c18f0c9e966e95dbe887d
URL:		http://www.directfb.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.217
%endif
BuildRequires:	sed >= 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Fusion Linux kernel module.

%description -l pl
Modu³ Fusion dla j±dra Linuksa.

%package devel
Summary:	Header file for Fusion device
Summary(pl):	Plik nag³ówkowy dla urz±dzenia Fusion
Group:		Development/Libraries
Requires:	linux-libc-headers

%description devel
Header file for Fusion device.

%description devel -l pl
Plik nag³ówkowy dla urz±dzenia Fusion.

%package -n kernel-char-fusion
Summary:	Fusion module for Linux kernel
Summary(pl):	Modu³ Fusion dla j±dra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-char-fusion
Fusion module for Linux kernel.

%description -n kernel-char-fusion -l pl
Modu³ Fusion dla j±dra Linuksa.

%package -n kernel-smp-char-fusion
Summary:	Fusion module for Linux SMP kernel
Summary(pl):	Modu³ Fusion dla j±dra Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-char-fusion
Fusion module for Linux SMP kernel.

%description -n kernel-smp-char-fusion -l pl
Modu³ Fusion dla j±dra Linuksa SMP.

%prep
%setup -q

sed -i -e 's/^obj-[^ ]*/obj-m/' linux/drivers/char/fusion/Makefile-2.6
echo "EXTRA_CFLAGS = -I`pwd`/linux/include" >> linux/drivers/char/fusion/Makefile-2.6

%build
%if %{with kernel}
cd linux/drivers/char/fusion
ln -sf Makefile-2.6 Makefile
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv fusion{,-$cfg}.ko
done
cd ../../../..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_includedir}/linux
install linux/include/linux/fusion.h $RPM_BUILD_ROOT%{_includedir}/linux
%endif

%if %{with kernel}
cd linux/drivers/char/fusion
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/char
install fusion-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/char/fusion.ko
%if %{with smp} && %{with dist_kernel}
install fusion-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/char/fusion.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-char-fusion
%depmod %{_kernel_ver}

%postun	-n kernel-char-fusion
%depmod %{_kernel_ver}

%post	-n kernel-smp-char-fusion
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-char-fusion
%depmod %{_kernel_ver}smp

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

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-char-fusion
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/char/fusion.ko*
%endif
%endif
