%define		php_name	php%{?php_suffix}
%define		modname		xhprof
Summary:	PHP extension for XHProf, a Hierarchical Profiler
Name:		%{php_name}-pecl-xhprof
Version:	0.9.4
Release:	1
License:	Apache v2.0
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	ab4062a7337e3bdaa2fd7065a7942b8d
Source1:	%{modname}.ini
Source2:	apache.conf
URL:		http://pecl.php.net/package/xhprof
BuildRequires:	%{php_name}-devel >= 4:5.2.0
BuildRequires:	rpmbuild(macros) >= 1.666
%{?requires_php_extension}
Provides:	php(xhprof) = %{version}
# https://bugs.php.net/61262
ExclusiveArch:	%{ix86} %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{modname}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}

%description
XHProf is a function-level hierarchical profiler for PHP.

This package provides the raw data collection component, implemented
in C (as a PHP extension).

The HTML based navigational interface is provided in the "xhprof"
package.

%package -n xhprof
Summary:	A Hierarchical Profiler for PHP - Web interface
Group:		Development/Tools
Requires:	%{_bindir}/dot
Requires:	%{name} = %{version}-%{release}
Requires:	php(core) >= 5.2.0
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n xhprof
XHProf is a function-level hierarchical profiler for PHP and has a
simple HTML based navigational interface.

The raw data collection component, implemented in C (as a PHP
extension, provided by the "php-pecl-xhprof" package).

The reporting/UI layer is all in PHP. It is capable of reporting
function-level inclusive and exclusive wall times, memory usage, CPU
times and number of calls for each function.

Additionally, it supports ability to compare two runs (hierarchical
DIFF reports), or aggregate results from multiple runs.

Documentation: %{_docdir}/%{name}-%{version}/docs/index.html

%prep
%setup -qc
mv %{modname}-%{version}/* .

# not to be installed
mv xhprof_html/docs docs

%build
cd extension
phpize
%configure
%{__make}
cd -

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=extension/modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install -C extension \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -a examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

# Install the web interface
install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

install -d $RPM_BUILD_ROOT%{_datadir}/xhprof
cp -a xhprof_html $RPM_BUILD_ROOT%{_datadir}/xhprof/xhprof_html
cp -a xhprof_lib  $RPM_BUILD_ROOT%{_datadir}/xhprof/xhprof_lib

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%triggerin -n xhprof -- apache-base
%webapp_register httpd %{_webapp}

%triggerun -n xhprof -- apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc CHANGELOG CREDITS README LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
%{_examplesdir}/%{name}-%{version}

%files -n xhprof
%defattr(644,root,root,755)
%doc docs/*
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%{_datadir}/xhprof
