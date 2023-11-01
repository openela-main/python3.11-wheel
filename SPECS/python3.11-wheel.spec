%global __python3 /usr/bin/python3.11
%global python3_pkgversion 3.11

# The function of bootstrap is that it disables the wheel subpackage
%bcond_with bootstrap

# Default: when bootstrapping -> disable tests
%if %{with bootstrap}
%bcond_with tests
%else
%bcond_without tests
%endif

# Similar to what we have in pythonX.Y.spec files.
# If enabled, provides unversioned executables and other stuff.
# Disable it if you build this package in an alternative stack.
%bcond_with main_python

%global pypi_name wheel
%global python_wheel_name %{pypi_name}-%{version}-py3-none-any.whl

Name:           python%{python3_pkgversion}-%{pypi_name}
Version:        0.38.4
Release:        3%{?dist}
Summary:        Built-package format for Python

# packaging is ASL 2.0 or BSD
License:        MIT and (ASL 2.0 or BSD)
URL:            https://github.com/pypa/wheel
Source0:        %{url}/archive/%{version}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-rpm-macros
BuildRequires:  python%{python3_pkgversion}-setuptools

# python3 bootstrap: this is rebuilt before the final build of python3, which
# adds the dependency on python3-rpm-generators, so we require it manually
BuildRequires:  python3-rpm-generators

%if %{with tests}
BuildRequires:  python%{python3_pkgversion}-pytest
# several tests compile extensions
# those tests are skipped if gcc is not found
BuildRequires:  gcc
%endif

# Virtual provides for the packages bundled by wheel.
# Actual version can be found in git history:
# https://github.com/pypa/wheel/commits/master/src/wheel/vendored/packaging/tags.py
%global bundled %{expand:
Provides:       bundled(python%{python3_version}dist(packaging)) = 21.3
}

%{bundled}


# Require alternatives version that implements the --keep-foreign flag
Requires(postun): alternatives >= 1.19.1-1

# python3.11 installs the alternatives master symlink to which we attach a slave
Requires:       python%{python3_pkgversion}
Requires(post): python%{python3_pkgversion}
Requires(postun): python%{python3_pkgversion}

%global _description %{expand:
Wheel is the reference implementation of the Python wheel packaging standard,
as defined in PEP 427.

It has two different roles:

 1. A setuptools extension for building wheels that provides the bdist_wheel
    setuptools command.
 2. A command line tool for working with wheel files.}

%description %{_description}

%if %{without bootstrap}
%package -n     %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
Summary:        The Python wheel module packaged as a wheel
%{bundled}

%description -n %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
A Python wheel of wheel to use with virtualenv.
%endif


%prep
%autosetup -n %{pypi_name}-%{version} -p1


%build
%py3_build


%install
%py3_install
mv %{buildroot}%{_bindir}/%{pypi_name}{,-%{python3_version}}
%if %{with main_python}
ln -s %{pypi_name}-%{python3_version} %{buildroot}%{_bindir}/%{pypi_name}-3
ln -s %{pypi_name}-3 %{buildroot}%{_bindir}/%{pypi_name}
%endif
# Create an empty file to be used by `alternatives`
touch %{buildroot}%{_bindir}/%{pypi_name}-3

%if %{without bootstrap}
# We can only use bdist_wheel when wheel is installed, hence we don't build the wheel in %%build
export PYTHONPATH=%{buildroot}%{python3_sitelib}
%py3_build_wheel
mkdir -p %{buildroot}%{python_wheel_dir}
install -p dist/%{python_wheel_name} -t %{buildroot}%{python_wheel_dir}
%endif


%if %{with tests}
%check
rm setup.cfg  # to drop pytest coverage options configured there
%pytest -v --ignore build
%endif

%post -n python%{python3_pkgversion}-%{pypi_name}
alternatives --keep-foreign --add-slave python3 %{_bindir}/python%{python3_version} \
    %{_bindir}/%{pypi_name}-3 \
    %{pypi_name}-3 \
    %{_bindir}/%{pypi_name}-%{python3_version}

%postun -n python%{python3_pkgversion}-%{pypi_name}
# Do this only during uninstall process (not during update)
if [ $1 -eq 0 ]; then
   alternatives --remove-slave python3 %{_bindir}/python%{python3_version} \
       %{pypi_name}-3
fi


%files -n python%{python3_pkgversion}-%{pypi_name}
%license LICENSE.txt
%doc README.rst
%{_bindir}/%{pypi_name}-%{python3_version}
%if %{with main_python}
%{_bindir}/%{pypi_name}
%{_bindir}/%{pypi_name}-3
%endif
%ghost %{_bindir}/%{pypi_name}-3
%{python3_sitelib}/%{pypi_name}*/

%if %{without bootstrap}
%files -n %{python_wheel_pkg_prefix}-%{pypi_name}-wheel
%license LICENSE.txt
# we own the dir for simplicity
%dir %{python_wheel_dir}/
%{python_wheel_dir}/%{python_wheel_name}
%endif

%changelog
* Wed Feb 01 2023 Charalampos Stratakis <cstratak@redhat.com> - 0.38.4-3
- Explicitly require the python3.11-rpm-macros

* Wed Feb 01 2023 Charalampos Stratakis <cstratak@redhat.com> - 0.38.4-2
- Disable bootstrap

* Tue Dec 13 2022 Charalampos Stratakis <cstratak@redhat.com> - 0.38.4-1
- Initial package
- Fedora contributions by:
      Charalampos Stratakis <cstratak@redhat.com>
      Dennis Gilmore <dennis@ausil.us>
      Haikel Guemar <hguemar@fedoraproject.org>
      Igor Gnatenko <ignatenkobrain@fedoraproject.org>
      Karolina Surma <ksurma@redhat.com>
      Lumir Balhar <lbalhar@redhat.com>
      Matej Stuchlik <mstuchli@redhat.com>
      Miro Hrončok <miro@hroncok.cz>
      Robert Kuska <rkuska@redhat.com>
      Slavek Kabrda <bkabrda@redhat.com>
      Tomas Hrnciar <thrnciar@redhat.com>
      Tomas Orsava <torsava@redhat.com>
