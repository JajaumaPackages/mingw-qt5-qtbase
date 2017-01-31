%?mingw_package_header

# Override the __debug_install_post argument as this package
# contains both native as well as cross compiled binaries
%global __debug_install_post %%{mingw_debug_install_post}; %{_rpmconfigdir}/find-debuginfo.sh %{?_missing_build_ids_terminate_build:--strict-build-id} %{?_find_debuginfo_opts} "%{_builddir}/%%{?buildsubdir}" %{nil}

#%%global pre rc1

#%%global snapshot_date 20121110
#%%global snapshot_rev d725239c

%if 0%{?snapshot_date}
%global source_folder qt-qtbase
%else
%global source_folder qtbase-opensource-src-%{version}%{?pre:-%{pre}}
%endif

# first two digits of version
%global release_version %(echo %{version} | awk -F. '{print $1"."$2}')

Name:           mingw-qt5-qtbase
Version:        5.6.0
Release:        6%{?pre:.%{pre}}%{?snapshot_date:.git%{snapshot_date}.%{snapshot_rev}}%{?dist}
Summary:        Qt5 for Windows - QtBase component

License:        GPLv3 with exceptions or LGPLv2 with exceptions
Group:          Development/Libraries
URL:            http://qt.io/

%if 0%{?snapshot_date}
# To regenerate:
# wget http://qt.gitorious.org/qt/qtbase/archive-tarball/%{snapshot_rev} -O qt5-qtbase-%{snapshot_rev}.tar.gz
Source0:        qt5-qtbase-%{snapshot_rev}.tar.gz
%else
%if "%{?pre}" != ""
Source0:        http://download.qt-project.org/development_releases/qt/%{release_version}/%{version}-%{pre}/submodules/qtbase-opensource-src-%{version}-%{pre}.tar.xz
%else
Source0:        http://download.qt-project.org/official_releases/qt/%{release_version}/%{version}/submodules/qtbase-opensource-src-%{version}.tar.xz
%endif
%endif

######################################
# Patches which should be upstreamed #
######################################

# Make sure the .pc files of the Qt5 modules are installed correctly
# This should prevent (silent) failures like:
# sed -e "s,/usr/i686-w64-mingw32/sys-root/mingw/include,/usr/i686-w64-mingw32/sys-root/mingw/include/qt5,g" -e "s,/usr/i686-w64-mingw32/sys-root/mingw/lib,/usr/i686-w64-mingw32/sys-root/mingw/lib,g" "../../../build_win32/lib/pkgconfig/Qt5AxContainer.pc" >"/home/erik/rpmbuild/BUILDROOT/mingw-qt5-qtactiveqt-5.0.1-1.fc18.x86_64/usr/i686-w64-mingw32/sys-root/mingw/lib/pkgconfig/Qt5AxContainer.pc"
# sed: can't read ../../../build_win32/lib/pkgconfig/Qt5AxContainer.pc: No such file or directory
# make[5]: [install_target] Error 2 (ignored)
#
# This issue was discovered during the review of mingw-qt5-qttools:
# https://bugzilla.redhat.com/show_bug.cgi?id=858080
Patch1:         qt5-workaround-pkgconfig-install-issue.patch

# Prevents resource files from being added to the LIBS parameter
# This solves an issue where the generated pkg-config files contained
# invalid Libs.private references like .obj/debug/Qt5Cored_resource_res.o
Patch2:         qt5-dont-add-resource-files-to-qmake-libs.patch

# qmake generates the pkgconfig .pc files two times, once for the
# release build and once for the debug build (which we're not actually
# building in this package). For both generations the exact same
# pkgconfig file name is used. This causes references to the debug
# build ending up in the .pc files which are unwanted
# Prevent this from happening by giving the pkgconfig .pc
# files for the debug build an unique file name
Patch3:         qt5-prevent-debug-library-names-in-pkgconfig-files.patch

# Fix qmake to create implibs with .dll.a extension for MinGW
Patch4:         qt5-qmake-implib-dll-a.patch

# As of Qt 5.4.1 the detection of the static DBus and Harfbuzz libraries got broken
Patch5:         qt5-fix-static-dbus-detection.patch
Patch6:         qt5-fix-static-harfbuzz-detection.patch

# When using pkg-config to detect static libraries, the --static flag should also be used
Patch7:         qt5-use-correct-pkg-config-static-flags.patch

# Enable QSharedMemory when targeting windows
# This is required to get the qtsystems module built again, RHBZ #1288928)
Patch8:         dfb9b9e1f7ff723bbb082875962ddcf0d69d1db2.diff

###########################
# Fedora specific patches #
###########################

# Patch the win32-g++ mkspecs profile to match our environment
Patch100:       qt5-use-win32-g++-mkspecs-profile.patch

# When building Qt as static library some files have a different content
# when compared to the static library. Merge those changes manually.
# This patch also applies some additional changes which are required to make
# linking against the static version of Qt work without any manual fiddling
Patch101:       qt5-merge-static-and-shared-library-trees.patch

# Add support for Angle
# It makes no sense to upstream this yet as upstream
# Angle only supports using static libraries
Patch102:       qt5-add-angle-support.patch

# Make sure our external Angle package is used instead of the bundled one
Patch103:       qt5-use-external-angle-library.patch

# The bundled pcre is built as static library by default
# As we're not using the bundled copy but our own copy
# we need to do some fiddling to fix compilation issues
# when trying to build static qmake projects
Patch104:       qt5-qtbase-fix-linking-against-static-pcre.patch

# Upstream always wants the host libraries to be static instead of
# shared libraries. This causes issues and is against the Fedora
# packaging guidelines so disable this 'feature'
Patch105:       qt5-dont-build-host-libs-static.patch

# Build host tools with rpath enabled
# We have to use rpath here as the library which the
# various tools depend on (libQt5Bootstrap.so) resides
# in the folder /usr/{i686,x86_64}-w64-mingw32/lib
# We can't use the regular %%_libdir for this as we
# want to avoid conflicts with the native qt5 packages
Patch106:       qt5-enable-rpath-for-host-tools.patch

# Build host libs with system zlib. This patch cannot be upstreamed as-is
# due to the other host-libs patches.
Patch107:       qt5-use-system-zlib-in-host-libs.patch

# Make sure the qtmain (static) library doesn't conflict with the one
# provided by the mingw-qt (qt4) package. The mkspecs profile is already
# updated by patch100 to reflect this change
# https://bugzilla.redhat.com/show_bug.cgi?id=1092465
Patch108:       qt5-rename-qtmain-to-qt5main.patch

# Ugly workaround for a build failure which only happens on arm (Fedora 20)
# g++ -c -pipe -O2 -g -std=c++0x -fno-exceptions -Wall -W -D_REENTRANT -fPIE -DQT_NO_MTDEV -DQT_NO_LIBUDEV -DQT_NO_EVDEV -DQT_QMLDEVTOOLS_LIB -DQDOC2_COMPAT -DQT_NO_EXCEPTIONS -DQT_NO_DEBUG -DQT_BOOTSTRAP_LIB -DQT_BOOTSTRAPPED -DQT_LITE_UNICODE -DQT_NO_CAST_TO_ASCII -DQT_NO_CODECS -DQT_NO_DATASTREAM -DQT_NO_LIBRARY -DQT_NO_QOBJECT -DQT_NO_SYSTEMLOCALE -DQT_NO_THREAD -DQT_NO_UNICODETABLES -DQT_NO_USING_NAMESPACE -DQT_NO_DEPRECATED -DQT_NO_TRANSLATION -DQT_QMAKE_LOCATION="/builddir/build/BUILD/build_release_static_win32/bin/qmake" -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/mkspecs/linux-g++ -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/src/tools/qdoc -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/src/tools/qdoc -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/src/tools/qdoc/qmlparser -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/include -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/include/QtCore -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/include/QtXml -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/include/QtCore/5.3.1 -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/include/QtCore/5.3.1/QtCore -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/include/QtXml/5.3.1 -I/builddir/build/BUILD/qtbase-opensource-src-5.3.1/include/QtXml/5.3.1/QtXml -I../../../include -I../../../include/QtCore -I/builddir/build/BUILD/build_release_static_win32/include/QtXml -I. -o .obj/quoter.o /builddir/build/BUILD/qtbase-opensource-src-5.3.1/src/tools/qdoc/quoter.cpp
# /builddir/build/BUILD/qtbase-opensource-src-5.3.1/src/tools/qdoc/quoter.cpp: In constructor 'Quoter::Quoter()':
# /builddir/build/BUILD/qtbase-opensource-src-5.3.1/src/tools/qdoc/quoter.cpp:139:1: internal compiler error: in add_stores, at var-tracking.c:5918
# }
# ^
Patch109:       qt5-workaround-gcc48-arm-build-failure.patch

# Workaround a compatibility issue because we are using an older version of ANGLE in Fedora
# Upgrading the mingw-angleproject package isn't possible for now because mingw-qt5-qtwebkit doesn't support the latest ANGLE yet..
#
# /home/erik/fedora/mingw-qt5-qtbase/qtbase-opensource-src-5.5.0/src/plugins/platforms/windows/qwindowseglcontext.cpp:376:15: error: 'EGL_PLATFORM_ANGLE_DEVICE_TYPE_ANGLE' was not declared in this scope
#                EGL_PLATFORM_ANGLE_DEVICE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_DEVICE_TYPE_WARP_ANGLE, EGL_NONE }
#                ^
# /home/erik/fedora/mingw-qt5-qtbase/qtbase-opensource-src-5.5.0/src/plugins/platforms/windows/qwindowseglcontext.cpp:376:53: error: 'EGL_PLATFORM_ANGLE_DEVICE_TYPE_WARP_ANGLE' was not declared in this scope
#                EGL_PLATFORM_ANGLE_DEVICE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_DEVICE_TYPE_WARP_ANGLE, EGL_NONE }
Patch110:       qt5-disable-angle-opengl-testcode.patch

# Prevent the pkgconfig files from containing references to /libQt5Core.dll.a for Libs.private
Patch111:       qt5-pkgconfig-static-library-name-workaround.patch

BuildRequires:  mingw32-filesystem >= 95
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-openssl
BuildRequires:  mingw32-zlib
BuildRequires:  mingw32-win-iconv
BuildRequires:  mingw32-libjpeg-turbo
BuildRequires:  mingw32-libpng
BuildRequires:  mingw32-sqlite
BuildRequires:  mingw32-dbus
BuildRequires:  mingw32-pkg-config
BuildRequires:  mingw32-angleproject >= 0-0.11.git.30d6c2.20141113
BuildRequires:  mingw32-pcre
BuildRequires:  mingw32-postgresql
BuildRequires:  mingw32-harfbuzz
BuildRequires:  mingw32-dbus-static
BuildRequires:  mingw32-harfbuzz-static
BuildRequires:  mingw32-pcre-static
BuildRequires:  mingw32-sqlite-static
BuildRequires:  mingw32-gstreamer1
BuildRequires:  mingw32-winpthreads-static

BuildRequires:  mingw64-filesystem >= 95
BuildRequires:  mingw64-gcc
BuildRequires:  mingw64-gcc-c++
BuildRequires:  mingw64-binutils
BuildRequires:  mingw64-openssl
BuildRequires:  mingw64-zlib
BuildRequires:  mingw64-win-iconv
BuildRequires:  mingw64-libjpeg-turbo
BuildRequires:  mingw64-libpng
BuildRequires:  mingw64-sqlite
BuildRequires:  mingw64-dbus
BuildRequires:  mingw64-pkg-config
BuildRequires:  mingw64-angleproject >= 0-0.11.git.30d6c2.20141113
BuildRequires:  mingw64-pcre
BuildRequires:  mingw64-postgresql
BuildRequires:  mingw64-harfbuzz
BuildRequires:  mingw64-dbus-static
BuildRequires:  mingw64-harfbuzz-static
BuildRequires:  mingw64-pcre-static
BuildRequires:  mingw64-sqlite-static
BuildRequires:  mingw64-gstreamer1
BuildRequires:  mingw64-winpthreads-static

BuildRequires:  zip
BuildRequires:  dos2unix

# Needed for Angle support
BuildRequires:  flex
BuildRequires:  bison

# For Qt5Bootstrap
BuildRequires:  pkgconfig(zlib)


%description
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.


# Win32
%package -n mingw32-qt5-qtbase
Summary:        Qt5 for Windows - QtBase component
# This package contains the cross-compiler setup for qmake
Requires:       mingw32-qt5-qmake = %{version}-%{release}
BuildArch:      noarch

%description -n mingw32-qt5-qtbase
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.

%package -n mingw32-qt5-qmake
Summary:       Qt5 for Windows build environment
Requires:      mingw32-qt5-qttools-tools

%description -n mingw32-qt5-qmake
This package contains the build environment for cross compiling
applications with the Fedora Windows Qt Library and cross-compiler.

%package -n mingw32-qt5-qtbase-devel
Summary:       Qt5 for Windows build environment
Requires:      mingw32-qt5-qtbase = %{version}-%{release}

%description -n mingw32-qt5-qtbase-devel
Contains the files required to get various Qt tools built
which are part of the mingw-qt5-qttools package

%package -n mingw32-qt5-qtbase-static
Summary:       Static version of the mingw32-qt5-qtbase library
Requires:      mingw32-qt5-qtbase = %{version}-%{release}
Requires:      mingw32-angleproject-static
Requires:      mingw32-libjpeg-turbo-static
Requires:      mingw32-libpng-static
Requires:      mingw32-harfbuzz-static
Requires:      mingw32-pcre-static
Requires:      mingw32-winpthreads-static
Requires:      mingw32-zlib-static
BuildArch:     noarch

%description -n mingw32-qt5-qtbase-static
Static version of the mingw32-qt5 library.

# Win64
%package -n mingw64-qt5-qtbase
Summary:        Qt5 for Windows - QtBase component
# This package contains the cross-compiler setup for qmake
Requires:       mingw64-qt5-qmake = %{version}-%{release}
BuildArch:      noarch

%description -n mingw64-qt5-qtbase
This package contains the Qt software toolkit for developing
cross-platform applications.

This is the Windows version of Qt, for use in conjunction with the
Fedora Windows cross-compiler.

%package -n mingw64-qt5-qmake
Summary:       Qt for Windows build environment
Requires:      mingw64-qt5-qttools-tools

%description -n mingw64-qt5-qmake
This package contains the build environment for cross compiling
applications with the Fedora Windows Qt Library and cross-compiler.

%package -n mingw64-qt5-qtbase-devel
Summary:       Qt5 for Windows build environment
Requires:      mingw64-qt5-qtbase = %{version}-%{release}

%description -n mingw64-qt5-qtbase-devel
Contains the files required to get various Qt tools built
which are part of the mingw-qt5-qttools package

%package -n mingw64-qt5-qtbase-static
Summary:       Static version of the mingw64-qt5-qtbase library
Requires:      mingw64-qt5-qtbase = %{version}-%{release}
Requires:      mingw64-angleproject-static
Requires:      mingw64-libjpeg-turbo-static
Requires:      mingw64-libpng-static
Requires:      mingw64-harfbuzz-static
Requires:      mingw64-pcre-static
Requires:      mingw64-winpthreads-static
Requires:      mingw64-zlib-static
BuildArch:     noarch

%description -n mingw64-qt5-qtbase-static
Static version of the mingw64-qt5-qtbase library.


%?mingw_debug_package


%prep
%setup -q -n %{source_folder}

# Note: some patches don't have a -b argument here
# This was done on purpose as the Qt build infrastructure
# automatically copies the entire mkspecs folder to
# the RPM_BUILD_ROOT. To prevent patch backups from
# appearing in the resulting RPMs we have to avoid
# using the -b argument here while applying patches
%patch1 -p0 -b .pkgconfig
%patch2 -p1 -b .res
%patch3 -p1 -b .pkgconfig_debug
%patch4 -p1 -b .qmake_implib
%patch5 -p1 -b .dbus_static
%patch6 -p1 -b .harfbuzz_static
%patch7 -p1 -b .pkgconfig_static
%patch8 -p1 -b .qshared_memory

%patch100 -p1
%patch101 -p0
%patch102 -p0 -b .angle
%patch103 -p0 -b .external_angle
%patch104 -p1 -b .pcre
%patch105 -p0
%patch106 -p1
%patch107 -p1 -b .host_system_zlib
%patch108 -p1 -b .qtmain
%patch110 -p1 -b .no_angle_opengl_tester
%patch111 -p1 -b .pkgconfig_static

%if 0%{?fedora} == 20
%ifarch %{arm}
%patch109 -p0 -b .arm
%endif
%endif

# Make sure the Qt5 build system uses our external ANGLE library
rm -rf src/3rdparty/angle include/QtANGLE/{EGL,GLES2,KHR}

# As well as our external PCRE library and zlib
rm -rf src/3rdparty/{pcre,zlib}


%build
# Generic configure arguments
qt_configure_args_generic="\
    -xplatform win32-g++ \
    -c++std c++11 \
    -optimized-qmake \
    -verbose \
    -opensource \
    -confirm-license \
    -force-pkg-config \
    -force-debug-info \
    -audio-backend \
    -system-zlib \
    -system-harfbuzz \
    -system-libpng \
    -system-libjpeg \
    -system-sqlite \
    -no-fontconfig \
    -iconv \
    -openssl \
    -dbus-linked \
    -no-glib \
    -no-gtkstyle \
    -no-icu \
    -release \
    -nomake examples \
    -make tools"

# The odd paths for the -hostbindir argument are on purpose
# The qtchooser tool assumes that the tools 'qmake', 'moc' and others
# are all available in the same folder with these exact file names
# To prevent conflicts with the mingw-qt (Qt4) package we have
# to put these tools in a dedicated folder
qt_configure_args_win32="\
    -hostprefix %{_prefix}/%{mingw32_target} \
    -hostbindir %{_prefix}/%{mingw32_target}/bin/qt5 \
    -hostdatadir %{mingw32_datadir}/qt5 \
    -prefix %{mingw32_prefix} \
    -bindir %{mingw32_bindir} \
    -archdatadir %{mingw32_datadir}/qt5 \
    -datadir %{mingw32_datadir}/qt5 \
    -docdir %{mingw32_docdir}/qt5 \
    -examplesdir %{mingw32_datadir}/qt5/examples \
    -headerdir %{mingw32_includedir}/qt5 \
    -libdir %{mingw32_libdir} \
    -plugindir %{mingw32_libdir}/qt5/plugins \
    -sysconfdir %{mingw32_sysconfdir} \
    -translationdir %{mingw32_datadir}/qt5/translations \
    -device-option CROSS_COMPILE=%{mingw32_target}-"

qt_configure_args_win64="\
    -hostprefix %{_prefix}/%{mingw64_target} \
    -hostbindir %{_prefix}/%{mingw64_target}/bin/qt5 \
    -hostdatadir %{mingw64_datadir}/qt5 \
    -prefix %{mingw64_prefix} \
    -bindir %{mingw64_bindir} \
    -archdatadir %{mingw64_datadir}/qt5 \
    -datadir %{mingw64_datadir}/qt5 \
    -docdir %{mingw64_docdir}/qt5 \
    -examplesdir %{mingw64_datadir}/qt5/examples \
    -headerdir %{mingw64_includedir}/qt5 \
    -libdir %{mingw64_libdir} \
    -plugindir %{mingw64_libdir}/qt5/plugins \
    -sysconfdir %{mingw64_sysconfdir} \
    -translationdir %{mingw64_datadir}/qt5/translations \
    -device-option CROSS_COMPILE=%{mingw64_target}-"

# RPM automatically sets the environment variable PKG_CONFIG_PATH
# to point to the native pkg-config files, but while cross compiling
# we don't want to have this environment variable set
unset PKG_CONFIG_PATH

###############################################################################
# Win32
#
# We have to build Qt two times, once for the static release build and
# once for the shared release build
#
# Unfortunately Qt only supports out-of-source builds which are in ../some_folder
rm -rf ../build_release_static_win32
mkdir ../build_release_static_win32
pushd ../build_release_static_win32
../%{source_folder}/configure \
    -static \
    $qt_configure_args_win32 $qt_configure_args_generic
make %{?_smp_mflags}
popd

# The LD_LIBRARY_PATH override is needed because libQt5Bootstrap* are shared
# libraries which various compiled tools (like moc) use. As the libQt5Bootstrap*
# libraries aren't installed at this point yet, we have to workaround this
rm -rf ../build_release_shared_win32
mkdir ../build_release_shared_win32
pushd ../build_release_shared_win32
../%{source_folder}/configure \
    -shared \
    $qt_configure_args_win32 $qt_configure_args_generic
LD_LIBRARY_PATH=`pwd`/lib make %{?_smp_mflags}
popd

###############################################################################
# Win64
#
# We have to build Qt two times, once for the static release build and
# once for the shared release build
#
# Unfortunately Qt only supports out-of-source builds which are in ../some_folder
rm -rf ../build_release_static_win64
mkdir ../build_release_static_win64
pushd ../build_release_static_win64
../%{source_folder}/configure \
    -static \
    $qt_configure_args_win64 $qt_configure_args_generic
make %{?_smp_mflags}
popd

rm -rf ../build_release_shared_win64
mkdir ../build_release_shared_win64
pushd ../build_release_shared_win64
../%{source_folder}/configure \
    -shared \
    $qt_configure_args_win64 $qt_configure_args_generic
LD_LIBRARY_PATH=`pwd`/lib make %{?_smp_mflags}
popd


%install
make install -C ../build_release_shared_win32$BUILDDIR INSTALL_ROOT=$RPM_BUILD_ROOT
make install -C ../build_release_shared_win64$BUILDDIR INSTALL_ROOT=$RPM_BUILD_ROOT

# Install the static libraries in a temporary prefix so we can merge everything together properly
mkdir $RPM_BUILD_ROOT/static
make install -C ../build_release_static_win32$BUILDDIR INSTALL_ROOT=$RPM_BUILD_ROOT/static
make install -C ../build_release_static_win64$BUILDDIR INSTALL_ROOT=$RPM_BUILD_ROOT/static

# The mingw gcc compiler assumes that %%{_prefix}/%%{mingw32_target}/lib and
# %%{prefix}/%%{mingw64_target}/lib are paths which need to be searched
# during linking for cross-compiled libraries. As this isn't intended and
# introduces unwanted side effects (related to building mingw-qt5-qttools)
# remove the reference to it
sed -i s@'"%{_prefix}/%{mingw32_target}/lib" '@@g $RPM_BUILD_ROOT%{mingw32_datadir}/qt5/mkspecs/qconfig.pri
sed -i s@'"%{_prefix}/%{mingw64_target}/lib" '@@g $RPM_BUILD_ROOT%{mingw64_datadir}/qt5/mkspecs/qconfig.pri

# Drop the qt5main and libQt5Bootstrap static libraries from the static
# tree as they're already part of the main tree
rm -f $RPM_BUILD_ROOT/static/%{mingw32_libdir}/libqt5main*
rm -f $RPM_BUILD_ROOT/static/%{mingw64_libdir}/libqt5main*
rm -f $RPM_BUILD_ROOT/static/%{mingw32_libdir}/libQt5Bootstrap*
rm -f $RPM_BUILD_ROOT/static/%{mingw64_libdir}/libQt5Bootstrap*

# Move the static libraries from the static tree to the main tree
mv $RPM_BUILD_ROOT/static%{mingw32_libdir}/*.a $RPM_BUILD_ROOT%{mingw32_libdir}
mv $RPM_BUILD_ROOT/static%{mingw64_libdir}/*.a $RPM_BUILD_ROOT%{mingw64_libdir}

# Also keep various Qt5 plugins to be used in static builds
# https://bugzilla.redhat.com/show_bug.cgi?id=1257630
mv $RPM_BUILD_ROOT/static%{mingw32_libdir}/qt5/plugins/*/*.a $RPM_BUILD_ROOT%{mingw32_libdir}
mv $RPM_BUILD_ROOT/static%{mingw64_libdir}/qt5/plugins/*/*.a $RPM_BUILD_ROOT%{mingw64_libdir}

# Clean up the static trees as we've now merged all interesting pieces
rm -rf $RPM_BUILD_ROOT/static

# The .dll's are installed in both %%{mingw32_bindir} and %%{mingw32_libdir}
# One copy of the .dll's is sufficient
rm -f $RPM_BUILD_ROOT%{mingw32_libdir}/*.dll
rm -f $RPM_BUILD_ROOT%{mingw64_libdir}/*.dll

# Drop all the files which we don't need
rm -f  $RPM_BUILD_ROOT%{mingw32_libdir}/*.prl
rm -f  $RPM_BUILD_ROOT%{mingw64_libdir}/*.prl

# Remove various unneeded files belonging to the Qt5Bootstrap library
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libQt5Bootstrap.la
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libQt5Bootstrap.prl
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libQt5BootstrapDBus.la
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libQt5BootstrapDBus.prl
rm -rf $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/pkgconfig

rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw64_target}/lib/libQt5Bootstrap.la
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw64_target}/lib/libQt5Bootstrap.prl
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw64_target}/lib/libQt5BootstrapDBus.la
rm -f  $RPM_BUILD_ROOT%{_prefix}/%{mingw64_target}/lib/libQt5BootstrapDBus.prl
rm -rf $RPM_BUILD_ROOT%{_prefix}/%{mingw64_target}/lib/pkgconfig

# Add qtchooser support
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/xdg/qtchooser
echo "%{_prefix}/%{mingw32_target}/bin/qt5" >  $RPM_BUILD_ROOT%{_sysconfdir}/xdg/qtchooser/mingw32-qt5.conf
echo "%{mingw32_prefix}" >> $RPM_BUILD_ROOT%{_sysconfdir}/xdg/qtchooser/mingw32-qt5.conf
echo "%{_prefix}/%{mingw64_target}/bin/qt5" >  $RPM_BUILD_ROOT%{_sysconfdir}/xdg/qtchooser/mingw64-qt5.conf
echo "%{mingw64_prefix}" >> $RPM_BUILD_ROOT%{_sysconfdir}/xdg/qtchooser/mingw64-qt5.conf

# Manually install qmake and other native tools so we don't depend anymore on
# the version of the native Fedora Qt and also fix issues as illustrated at
# http://stackoverflow.com/questions/6592931/building-for-windows-under-linux-using-qt-creator
#
# Also make sure the tools can be found by CMake
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/bin
mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{mingw64_target}/bin

for tool in qmake moc rcc uic qdbuscpp2xml qdbusxml2cpp qdoc syncqt.pl; do
    ln -s ../%{mingw32_target}/bin/qt5/$tool $RPM_BUILD_ROOT%{_bindir}/%{mingw32_target}-$tool-qt5
    ln -s ../%{mingw64_target}/bin/qt5/$tool $RPM_BUILD_ROOT%{_bindir}/%{mingw64_target}-$tool-qt5
done

ln -s %{mingw32_target}-qmake-qt5 $RPM_BUILD_ROOT%{_bindir}/mingw32-qmake-qt5
ln -s %{mingw64_target}-qmake-qt5 $RPM_BUILD_ROOT%{_bindir}/mingw64-qmake-qt5


# Win32
%files -n mingw32-qt5-qtbase
%{mingw32_bindir}/Qt5Concurrent.dll
%{mingw32_bindir}/Qt5Core.dll
%{mingw32_bindir}/Qt5DBus.dll
%{mingw32_bindir}/Qt5Gui.dll
%{mingw32_bindir}/Qt5Network.dll
%{mingw32_bindir}/Qt5OpenGL.dll
%{mingw32_bindir}/Qt5PrintSupport.dll
%{mingw32_bindir}/Qt5Sql.dll
%{mingw32_bindir}/Qt5Test.dll
%{mingw32_bindir}/Qt5Widgets.dll
%{mingw32_bindir}/Qt5Xml.dll
%{mingw32_libdir}/libQt5Concurrent.dll.a
%{mingw32_libdir}/libQt5Core.dll.a
%{mingw32_libdir}/libQt5DBus.dll.a
%{mingw32_libdir}/libQt5Gui.dll.a
%{mingw32_libdir}/libQt5Network.dll.a
%{mingw32_libdir}/libQt5OpenGL.dll.a
%{mingw32_libdir}/libQt5PrintSupport.dll.a
%{mingw32_libdir}/libQt5Sql.dll.a
%{mingw32_libdir}/libQt5Test.dll.a
%{mingw32_libdir}/libQt5Widgets.dll.a
%{mingw32_libdir}/libQt5Xml.dll.a
%{mingw32_libdir}/libqt5main.a
%{mingw32_libdir}/pkgconfig/Qt5Concurrent.pc
%{mingw32_libdir}/pkgconfig/Qt5Core.pc
%{mingw32_libdir}/pkgconfig/Qt5DBus.pc
%{mingw32_libdir}/pkgconfig/Qt5Gui.pc
%{mingw32_libdir}/pkgconfig/Qt5Network.pc
%{mingw32_libdir}/pkgconfig/Qt5OpenGL.pc
%{mingw32_libdir}/pkgconfig/Qt5OpenGLExtensions.pc
%{mingw32_libdir}/pkgconfig/Qt5PrintSupport.pc
%{mingw32_libdir}/pkgconfig/Qt5Sql.pc
%{mingw32_libdir}/pkgconfig/Qt5Test.pc
%{mingw32_libdir}/pkgconfig/Qt5Widgets.pc
%{mingw32_libdir}/pkgconfig/Qt5Xml.pc
%dir %{mingw32_libdir}/qt5/
%dir %{mingw32_libdir}/qt5/plugins
%dir %{mingw32_libdir}/qt5/plugins/bearer
%{mingw32_libdir}/qt5/plugins/bearer/qgenericbearer.dll
%{mingw32_libdir}/qt5/plugins/bearer/qnativewifibearer.dll
%dir %{mingw32_libdir}/qt5/plugins/generic
%{mingw32_libdir}/qt5/plugins/generic/qtuiotouchplugin.dll
%dir %{mingw32_libdir}/qt5/plugins/imageformats
%{mingw32_libdir}/qt5/plugins/imageformats/qgif.dll
%{mingw32_libdir}/qt5/plugins/imageformats/qico.dll
%{mingw32_libdir}/qt5/plugins/imageformats/qjpeg.dll
%dir %{mingw32_libdir}/qt5/plugins/platforms
%{mingw32_libdir}/qt5/plugins/platforms/qminimal.dll
%{mingw32_libdir}/qt5/plugins/platforms/qwindows.dll
%dir %{mingw32_libdir}/qt5/plugins/printsupport
%{mingw32_libdir}/qt5/plugins/printsupport/windowsprintersupport.dll
%dir %{mingw32_libdir}/qt5/plugins/sqldrivers
%{mingw32_libdir}/qt5/plugins/sqldrivers/qsqlite.dll
%{mingw32_libdir}/qt5/plugins/sqldrivers/qsqlodbc.dll
%{mingw32_libdir}/qt5/plugins/sqldrivers/qsqlpsql.dll
%{mingw32_libdir}/cmake/Qt5/
%{mingw32_libdir}/cmake/Qt5Core/
%{mingw32_libdir}/cmake/Qt5Concurrent/
%{mingw32_libdir}/cmake/Qt5DBus/
%{mingw32_libdir}/cmake/Qt5Gui/
%{mingw32_libdir}/cmake/Qt5Network/
%{mingw32_libdir}/cmake/Qt5OpenGL/
%{mingw32_libdir}/cmake/Qt5OpenGLExtensions/
%{mingw32_libdir}/cmake/Qt5PrintSupport/
%{mingw32_libdir}/cmake/Qt5Sql/
%{mingw32_libdir}/cmake/Qt5Test/
%{mingw32_libdir}/cmake/Qt5Widgets/
%{mingw32_libdir}/cmake/Qt5Xml/
%dir %{mingw32_includedir}/qt5/
%{mingw32_includedir}/qt5/QtConcurrent/
%{mingw32_includedir}/qt5/QtCore/
%{mingw32_includedir}/qt5/QtDBus/
%{mingw32_includedir}/qt5/QtGui/
%{mingw32_includedir}/qt5/QtNetwork/
%{mingw32_includedir}/qt5/QtOpenGL/
%{mingw32_includedir}/qt5/QtOpenGLExtensions/
%{mingw32_includedir}/qt5/QtPlatformHeaders/
%{mingw32_includedir}/qt5/QtPlatformSupport/
%{mingw32_includedir}/qt5/QtPrintSupport/
%{mingw32_includedir}/qt5/QtSql/
%{mingw32_includedir}/qt5/QtTest/
%{mingw32_includedir}/qt5/QtWidgets/
%{mingw32_includedir}/qt5/QtXml/
%{mingw32_docdir}/qt5/

%files -n mingw32-qt5-qmake
%doc LGPL_EXCEPTION.txt LICENSE.FDL LICENSE.LGPLv21 LICENSE.LGPLv3 LICENSE.PREVIEW.COMMERCIAL
%{_bindir}/%{mingw32_target}-moc-qt5
%{_bindir}/%{mingw32_target}-qdbuscpp2xml-qt5
%{_bindir}/%{mingw32_target}-qdbusxml2cpp-qt5
%{_bindir}/%{mingw32_target}-qdoc-qt5
%{_bindir}/%{mingw32_target}-qmake-qt5
%{_bindir}/%{mingw32_target}-rcc-qt5
%{_bindir}/%{mingw32_target}-syncqt.pl-qt5
%{_bindir}/%{mingw32_target}-uic-qt5
%{_bindir}/mingw32-qmake-qt5
%dir %{_prefix}/%{mingw32_target}/bin/qt5/
%{_prefix}/%{mingw32_target}/bin/qt5/fixqt4headers.pl
%{_prefix}/%{mingw32_target}/bin/qt5/moc
%{_prefix}/%{mingw32_target}/bin/qt5/qdbuscpp2xml
%{_prefix}/%{mingw32_target}/bin/qt5/qdbusxml2cpp
%{_prefix}/%{mingw32_target}/bin/qt5/qlalr
%{_prefix}/%{mingw32_target}/bin/qt5/qmake
%{_prefix}/%{mingw32_target}/bin/qt5/rcc
%{_prefix}/%{mingw32_target}/bin/qt5/syncqt.pl
%{_prefix}/%{mingw32_target}/bin/qt5/uic
%{_prefix}/%{mingw32_target}/lib/libQt5Bootstrap.so.5*
%{_prefix}/%{mingw32_target}/lib/libQt5BootstrapDBus.so.5*
%{mingw32_datadir}/qt5/

# qtchooser
%dir %{_sysconfdir}/xdg/qtchooser/
# not editable config files, so not using %%config here
%{_sysconfdir}/xdg/qtchooser/mingw32-qt5.conf

%files -n mingw32-qt5-qtbase-devel
%{_prefix}/%{mingw32_target}/lib/libQt5Bootstrap.so
%{_prefix}/%{mingw32_target}/lib/libQt5BootstrapDBus.so

%files -n mingw32-qt5-qtbase-static
%{mingw32_libdir}/libQt5Concurrent.a
%{mingw32_libdir}/libQt5Core.a
%{mingw32_libdir}/libQt5DBus.a
%{mingw32_libdir}/libQt5Gui.a
%{mingw32_libdir}/libQt5Network.a
%{mingw32_libdir}/libQt5OpenGL.a
%{mingw32_libdir}/libQt5OpenGLExtensions.a
%{mingw32_libdir}/libQt5PlatformSupport.a
%{mingw32_libdir}/libQt5PrintSupport.a
%{mingw32_libdir}/libQt5Sql.a
%{mingw32_libdir}/libQt5Test.a
%{mingw32_libdir}/libQt5Widgets.a
%{mingw32_libdir}/libQt5Xml.a
%{mingw32_libdir}/libqgenericbearer.a
%{mingw32_libdir}/libqico.a
%{mingw32_libdir}/libqminimal.a
%{mingw32_libdir}/libqnativewifibearer.a
%{mingw32_libdir}/libqsqlite.a
%{mingw32_libdir}/libqsqlodbc.a
%{mingw32_libdir}/libqtuiotouchplugin.a
%{mingw32_libdir}/libqwindows.a
%{mingw32_libdir}/libwindowsprintersupport.a

# Win64
%files -n mingw64-qt5-qtbase
%{mingw64_bindir}/Qt5Concurrent.dll
%{mingw64_bindir}/Qt5Core.dll
%{mingw64_bindir}/Qt5DBus.dll
%{mingw64_bindir}/Qt5Gui.dll
%{mingw64_bindir}/Qt5Network.dll
%{mingw64_bindir}/Qt5OpenGL.dll
%{mingw64_bindir}/Qt5PrintSupport.dll
%{mingw64_bindir}/Qt5Sql.dll
%{mingw64_bindir}/Qt5Test.dll
%{mingw64_bindir}/Qt5Widgets.dll
%{mingw64_bindir}/Qt5Xml.dll
%{mingw64_libdir}/libQt5Concurrent.dll.a
%{mingw64_libdir}/libQt5Core.dll.a
%{mingw64_libdir}/libQt5DBus.dll.a
%{mingw64_libdir}/libQt5Gui.dll.a
%{mingw64_libdir}/libQt5Network.dll.a
%{mingw64_libdir}/libQt5OpenGL.dll.a
%{mingw64_libdir}/libQt5PrintSupport.dll.a
%{mingw64_libdir}/libQt5Sql.dll.a
%{mingw64_libdir}/libQt5Test.dll.a
%{mingw64_libdir}/libQt5Widgets.dll.a
%{mingw64_libdir}/libQt5Xml.dll.a
%{mingw64_libdir}/libqt5main.a
%{mingw64_libdir}/pkgconfig/Qt5Concurrent.pc
%{mingw64_libdir}/pkgconfig/Qt5Core.pc
%{mingw64_libdir}/pkgconfig/Qt5DBus.pc
%{mingw64_libdir}/pkgconfig/Qt5Gui.pc
%{mingw64_libdir}/pkgconfig/Qt5Network.pc
%{mingw64_libdir}/pkgconfig/Qt5OpenGL.pc
%{mingw64_libdir}/pkgconfig/Qt5OpenGLExtensions.pc
%{mingw64_libdir}/pkgconfig/Qt5PrintSupport.pc
%{mingw64_libdir}/pkgconfig/Qt5Sql.pc
%{mingw64_libdir}/pkgconfig/Qt5Test.pc
%{mingw64_libdir}/pkgconfig/Qt5Widgets.pc
%{mingw64_libdir}/pkgconfig/Qt5Xml.pc
%dir %{mingw64_libdir}/qt5/
%dir %{mingw64_libdir}/qt5/plugins
%dir %{mingw64_libdir}/qt5/plugins/bearer
%{mingw64_libdir}/qt5/plugins/bearer/qgenericbearer.dll
%{mingw64_libdir}/qt5/plugins/bearer/qnativewifibearer.dll
%dir %{mingw64_libdir}/qt5/plugins/generic
%{mingw64_libdir}/qt5/plugins/generic/qtuiotouchplugin.dll
%dir %{mingw64_libdir}/qt5/plugins/imageformats
%{mingw64_libdir}/qt5/plugins/imageformats/qgif.dll
%{mingw64_libdir}/qt5/plugins/imageformats/qico.dll
%{mingw64_libdir}/qt5/plugins/imageformats/qjpeg.dll
%dir %{mingw64_libdir}/qt5/plugins/platforms
%{mingw64_libdir}/qt5/plugins/platforms/qminimal.dll
%{mingw64_libdir}/qt5/plugins/platforms/qwindows.dll
%dir %{mingw64_libdir}/qt5/plugins/printsupport
%{mingw64_libdir}/qt5/plugins/printsupport/windowsprintersupport.dll
%dir %{mingw64_libdir}/qt5/plugins/sqldrivers
%{mingw64_libdir}/qt5/plugins/sqldrivers/qsqlite.dll
%{mingw64_libdir}/qt5/plugins/sqldrivers/qsqlodbc.dll
%{mingw64_libdir}/qt5/plugins/sqldrivers/qsqlpsql.dll
%{mingw64_libdir}/cmake/Qt5/
%{mingw64_libdir}/cmake/Qt5Core/
%{mingw64_libdir}/cmake/Qt5Concurrent/
%{mingw64_libdir}/cmake/Qt5DBus/
%{mingw64_libdir}/cmake/Qt5Gui/
%{mingw64_libdir}/cmake/Qt5Network/
%{mingw64_libdir}/cmake/Qt5OpenGL/
%{mingw64_libdir}/cmake/Qt5OpenGLExtensions/
%{mingw64_libdir}/cmake/Qt5PrintSupport/
%{mingw64_libdir}/cmake/Qt5Sql/
%{mingw64_libdir}/cmake/Qt5Test/
%{mingw64_libdir}/cmake/Qt5Widgets/
%{mingw64_libdir}/cmake/Qt5Xml/
%dir %{mingw64_includedir}/qt5/
%{mingw64_includedir}/qt5/QtConcurrent/
%{mingw64_includedir}/qt5/QtCore/
%{mingw64_includedir}/qt5/QtDBus/
%{mingw64_includedir}/qt5/QtGui/
%{mingw64_includedir}/qt5/QtNetwork/
%{mingw64_includedir}/qt5/QtOpenGL/
%{mingw64_includedir}/qt5/QtOpenGLExtensions/
%{mingw64_includedir}/qt5/QtPlatformHeaders/
%{mingw64_includedir}/qt5/QtPlatformSupport/
%{mingw64_includedir}/qt5/QtPrintSupport/
%{mingw64_includedir}/qt5/QtSql/
%{mingw64_includedir}/qt5/QtTest/
%{mingw64_includedir}/qt5/QtWidgets/
%{mingw64_includedir}/qt5/QtXml/
%{mingw64_docdir}/qt5/

%files -n mingw64-qt5-qmake
%doc LGPL_EXCEPTION.txt LICENSE.FDL LICENSE.LGPLv21 LICENSE.LGPLv3 LICENSE.PREVIEW.COMMERCIAL
%{_bindir}/%{mingw64_target}-moc-qt5
%{_bindir}/%{mingw64_target}-qdbuscpp2xml-qt5
%{_bindir}/%{mingw64_target}-qdbusxml2cpp-qt5
%{_bindir}/%{mingw64_target}-qdoc-qt5
%{_bindir}/%{mingw64_target}-qmake-qt5
%{_bindir}/%{mingw64_target}-rcc-qt5
%{_bindir}/%{mingw64_target}-syncqt.pl-qt5
%{_bindir}/%{mingw64_target}-uic-qt5
%{_bindir}/mingw64-qmake-qt5
%dir %{_prefix}/%{mingw64_target}/bin/qt5/
%{_prefix}/%{mingw64_target}/bin/qt5/fixqt4headers.pl
%{_prefix}/%{mingw64_target}/bin/qt5/moc
%{_prefix}/%{mingw64_target}/bin/qt5/qdbuscpp2xml
%{_prefix}/%{mingw64_target}/bin/qt5/qdbusxml2cpp
%{_prefix}/%{mingw64_target}/bin/qt5/qlalr
%{_prefix}/%{mingw64_target}/bin/qt5/qmake
%{_prefix}/%{mingw64_target}/bin/qt5/rcc
%{_prefix}/%{mingw64_target}/bin/qt5/syncqt.pl
%{_prefix}/%{mingw64_target}/bin/qt5/uic
%{_prefix}/%{mingw64_target}/lib/libQt5Bootstrap.so.5*
%{_prefix}/%{mingw64_target}/lib/libQt5BootstrapDBus.so.5*
%{mingw64_datadir}/qt5/

# qtchooser
%dir %{_sysconfdir}/xdg/qtchooser/
# not editable config files, so not using %%config here
%{_sysconfdir}/xdg/qtchooser/mingw64-qt5.conf

%files -n mingw64-qt5-qtbase-devel
%{_prefix}/%{mingw64_target}/lib/libQt5Bootstrap.so
%{_prefix}/%{mingw64_target}/lib/libQt5BootstrapDBus.so

%files -n mingw64-qt5-qtbase-static
%{mingw64_libdir}/libQt5Concurrent.a
%{mingw64_libdir}/libQt5Core.a
%{mingw64_libdir}/libQt5DBus.a
%{mingw64_libdir}/libQt5Gui.a
%{mingw64_libdir}/libQt5Network.a
%{mingw64_libdir}/libQt5OpenGL.a
%{mingw64_libdir}/libQt5OpenGLExtensions.a
%{mingw64_libdir}/libQt5PlatformSupport.a
%{mingw64_libdir}/libQt5PrintSupport.a
%{mingw64_libdir}/libQt5Sql.a
%{mingw64_libdir}/libQt5Test.a
%{mingw64_libdir}/libQt5Widgets.a
%{mingw64_libdir}/libQt5Xml.a
%{mingw64_libdir}/libqgenericbearer.a
%{mingw64_libdir}/libqico.a
%{mingw64_libdir}/libqminimal.a
%{mingw64_libdir}/libqnativewifibearer.a
%{mingw64_libdir}/libqsqlite.a
%{mingw64_libdir}/libqsqlodbc.a
%{mingw64_libdir}/libqtuiotouchplugin.a
%{mingw64_libdir}/libqwindows.a
%{mingw64_libdir}/libwindowsprintersupport.a


%changelog
* Wed Feb 01 2017 Jajauma's Packages <jajauma@yandex.ru> - 5.6.0-6
- De-bootstrap build

* Tue Jan 31 2017 Jajauma's Packages <jajauma@yandex.ru> - 5.6.0-5
- Bootstrap build
- Fix building on el7 by forcing c++11 mode

* Sat May 07 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.6.0-4
- Rebuild against mingw-gcc 6.1

* Wed Apr 13 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.6.0-3
- Re-enable QSharedMemory (got broken between Qt 5.3 and Qt 5.4)
- Fixes FTBFS of mingw-qt5-qsystems package (RHBZ #1288928)

* Sat Apr  9 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.6.0-2
- Add BR: mingw{32,64}-gstreamer1

* Sun Mar 27 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.6.0-1
- Update to 5.6.0
- Build with -optimized-qmake again

* Sun Feb  7 2016 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.1-4
- Temporary build without -optimized-qmake on Fedora24+ to prevent
  a build failure with GCC6 on i686 environments

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.5.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Dec 31 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.1-2
- Prevent warning output when QWebView loads QNetworkRequest (QTBUG-49174)
- Re-add QMAKE_LRELEASE qmake parameter which accidently got lost some time ago

* Thu Dec 24 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.1-1
- Update to 5.5.1
- Fixes RHBZ #1293056

* Thu Aug 27 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.0-2
- Add static versions of various plugin libraries like qwindows to the -static subpackages (RHBZ #1257630)

* Wed Aug  5 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.5.0-1
- Update to 5.5.0

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Apr 24 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.1-2
- Fix CVE-2015-0295, CVE-2015-1858, CVE-2015-1859 and CVE-2015-1860

* Sun Mar  8 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.1-1
- Update to 5.4.1
- Added some more BuildRequires for mingw*-static libraries as the ./configure
  script now needs them to be available in the buildroot
- Fix detection of the static dbus and harfbuzz libraries

* Mon Jan 26 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.0-4
- Rebuild against mingw-w64 v4.0rc1

* Wed Dec 31 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.0-3
- Added some more Requires tags to the -static subpackages

* Wed Dec 31 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.0-2
- Added various Requires tags to the -static subpackages

* Mon Dec 29 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.4.0-1
- Update to 5.4.0
- Thanks to Philip A Reimer (ArchLinux MinGW maintainer)
  for rebasing the ANGLE patches
- Use external harfbuzz library (unfortunately this also introduces
  additional runtime dependencies on mingw-freetype, mingw-bzip2,
  mingw-glib2 and mingw-gettext)

* Thu Dec  4 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.2-2
- Rebuild against gcc 4.9.2 (to fix paths mentioned in mkspecs/qconfig.pri)

* Fri Sep 19 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.2-1
- Update to 5.3.2

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Jul 23 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.1-3
- Rebuild against gcc 4.9.1 (to fix paths mentioned in mkspecs/qconfig.pri)

* Sun Jul  6 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.1-2
- Remove references to obsolete packages

* Sat Jul  5 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.1-1
- Update to 5.3.1

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 24 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.3.0-1
- Update to 5.3.0

* Sat May  3 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.1-3
- Fix invalid reference to qtmain when using CMake (RHBZ #1092465)
- Fix DoS vulnerability in the GIF image handler (QTBUG-38367, RHBZ #1092837)

* Sun Apr 13 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.1-2
- Rebuild against gcc 4.9 (to fix paths mentioned in mkspecs/qconfig.pri)

* Sat Feb  8 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.1-1
- Update to 5.2.1

* Sat Jan 11 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-4
- Remove hard dependency on qtchooser and co-own the /etc/xdg/qtchooser folder

* Mon Jan  6 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-3
- Split the cmake patch and moved half of its contents to the 'implib dll'
  patch and the other to the 'use external angle' patch as those are more
  proper locations

* Sun Jan  5 2014 Yaakov Selkowitz <yselkowitz@users.sourceforge.net> - 5.2.0-2
- Fix qmake to use .dll.a extension for implibs (avoids renaming hacks in
  all mingw-qt5-* packages)
- Force usage of system zlib in Qt5Bootstrap
- Install shared libQt5BootstrapDBus for qdbuscpp2xml and qdbusxml2cpp
- Fix QMAKE_LIBS_NETWORK for static linkage
- Closes RHBZ #1048677

* Sun Jan  5 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-1
- Update to 5.2.0
- Use the generic win32-g++ mkspecs profile instead of win32-g++-cross
  and win32-g++-cross-x64 (as is preferred by upstream)
- Add support for qtchooser
- Moved the native tools to /usr/$target/bin/qt5 (qtchooser requires the
  tools to be in an unique folder with their original file names)
  All symlinks in %%{_bindir} are updated to reflect this as well
- Prevent invalid Libs.private references in generated pkg-config files
- Prevent patch backups from ending up in the mkspecs folders
- Reorganized and cleaned up the patches

* Fri Nov 29 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-0.4.rc1
- Update to 5.2.0 RC 1

* Wed Nov 27 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-0.3.beta1
- Try harder to fix detection of the uic tool when using CMake

* Tue Nov 26 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-0.2.beta1
- Fix detection of the uic tool when using CMake (RHBZ #1019952)

* Tue Oct 22 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.2.0-0.1.beta1
- Update to 5.2.0 beta 1
- Fix CMake support (RHBZ #1019952, RHBZ #1019947)

* Thu Sep 12 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.1-2
- Removed DBus 'interface' workaround patch as the issue is resolved in DBus upstream

* Thu Aug 29 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.1-1
- Update to 5.1.1
- Fix FTBFS against latest mingw-w64

* Fri Aug  2 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-5
- Re-enable R: mingw{32,64}-qt5-qttools-lrelease now that
  bootstrapping Qt5 on ARM has completed

* Wed Jul 31 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-4
- Make sure the native Qt5Bootstrap library is a shared library
- Enabled PostgreSQL support
- Removed the reference to the 'demos' folder as demos are
  bundled as separate tarballs

* Tue Jul 30 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-3
- Temporary build without R: mingw{32,64}-qt5-qttools-lrelease
  to allow mingw-qt5-qttools to be built on arm

* Sat Jul 13 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-2
- Rebuild against libpng 1.6

* Wed Jul 10 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.1.0-1
- Update to 5.1.0
- Fix detection of external pcre library
- Added BR: mingw32-pcre mingw64-pcre

* Wed Jul 10 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.2-3
- Display message box if platform plugin cannot be found (QTBUG-31765, QTBUG-31760)

* Fri May 10 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.2-2
- Fix references to the tools qdoc and qhelpgenerator (needed to build qtdoc)

* Sat Apr 13 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.2-1
- Update to 5.0.2
- Remove DirectWrite support for now as the necessary API
  isn't available on Windows XP (as mentioned in RHBZ #917323)

* Thu Mar 28 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.1-4
- Have the -qmake packages require mingw{32,64}-qt5-qttools-lrelease
  and update the reference to it in the mkspecs profiles

* Tue Mar 26 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.1-3
- Make sure the .pc files of the Qt5 modules are installed correctly

* Thu Feb  7 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.1-2
- Replaced the OpenSSL patch with a more proper one
- Improve detection of the Qt5Bootstrap library (needed by mingw-qt5-qttools)
- Workaround cross-compilation issue when using a non-x86 host (RHBZ #905863, QTBUG #29426)
- Resolve build failure caused by QtDBus headers which use the reserved keyword 'interface'

* Thu Jan 31 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.1-1
- Update to 5.0.1
- Removed the -fast configure argument (upstream dropped support for it)

* Fri Jan 11 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-4
- Moved the libQt5Bootstrap.a library (required to build tools like lrelease
  and lupdate which are part of mingw-qt5-qttools) to separate -devel subpackages
  as it is a native library instead of a cross-compiled one
- Removed the pkg-config file for Qt5Bootstrap as it doesn't work as expected
  when Qt5 is cross-compiled

* Sat Dec 29 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-3
- The define QT_NEEDS_QMAIN also needs to be set for our mkspecs profiles
- To make linking against qt5main.a (which contains a Qt specific WinMain) work
  binaries need to be linked with -lmingw32 -lqt5main
- Resolves some initialisation issues
- Don't enable ICU support as it introduces over 20MB of dependency bloat

* Sat Dec 29 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-2
- Don't segfault when no suitable platform dll could be located

* Mon Dec 24 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-1
- Update to Qt 5.0.0 Final
- Use the qplatformdefs.h header which is included in the
  win32-g++ mkspecs profile instead of providing our own
- Replaced the bundled copy of the ANGLE libraries with
  a seperate mingw-angleproject package

* Thu Dec 13 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.15.rc2
- Update to Qt 5.0.0 RC2
- Dropped upstreamed DirectWrite patch

* Fri Dec  7 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.14.rc1
- Update to Qt 5.0.0 RC1
- Replaced various hack with proper patches
- Use the configure argument -archdatadir as it is used to decide
  where the mkspecs profiles should be installed

* Sat Nov 10 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.13.beta1.git20121110.d725239c
- Update to 20121110 snapshot (rev d725239c)
- Dropped the configure argument -qtlibinfix 5 as upstream
  has resolved the file conflicts with Qt4 properly now
- Added several missing flags to the mkspecs profiles
- Dropped the pkg-config file renames as they're not needed any more
- Dropped two obsolete patches

* Sat Nov 10 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.12.beta1.git20121103.ccc4fbdf
- Update to 20121103 snapshot (rev ccc4fbdf)
- Use -std=c++11 instead of -std=c++0x as the latter is deprecated in gcc 4.7
- Added DirectWrite support
- Added Angle support

* Sun Oct  7 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.11.beta1
- Fix compilation failure of the win64 build when using c++11 mode

* Sat Sep 15 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.10.beta1
- Re-added some configure arguments as they're apparently still needed to build
  the individual Qt components
- Removed -ltiff from the mkspecs profiles
- Added BR: mingw32-icu mingw64-icu
- Fix directory ownership of %%{mingw32_datadir}/qt5/ and %%{mingw64_datadir}/qt5/

* Thu Sep 13 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.9.beta1
- Add QT_TOOL.lrelease.command to the mkspecs profiles
- Fixed detection of mingw-icu
- Removed some obsolete configure arguments

* Wed Sep 12 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.8.beta1
- Make sure that Qt components which are built as static library also
  contain the version number (TARGET_VERSION_EXT) when it is set

* Mon Sep 10 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.7.beta1
- Added syncqt to the mkspecs profiles
- Set the qtlibinfix parameter correctly to avoid needing to use other hacks

* Sun Sep  9 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.6.beta1
- Make sure that Qt is built with debugging symbols and that these
  debugging symbols are placed in the -debuginfo subpackage

* Sat Sep  8 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.5.beta1
- Removed -javascript-jit from the configure arguments as it's only needed
  for QtWebKit (which is provided in a seperate package)
- Added QMAKE_DLLTOOL to the mkspecs profiles

* Sat Sep  8 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.4.beta1
- Use the lrelease tool from mingw-qt4 for now until mingw-qt5-qttools is packaged

* Fri Sep  7 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.3.beta1
- Added win32 static release and win64 static release builds

* Tue Sep  4 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.2.beta1
- Moved headers to %%{mingw32_includedir}/qt5 and %%{mingw64_includedir}/qt5
- Renamed the pkgconfig files to avoid conflict with qt4

* Tue Sep  4 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 5.0.0-0.1.beta1
- Initial package (based on mingw-qt spec file)

