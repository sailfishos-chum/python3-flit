# Modified for SailfishOS
# + Disable tests by default
# + Remove redundant python-flit package


# circular build dependency on requests-download and testpath
%bcond_with tests

%define srcname flit

Name:		python3-%{srcname}
Version:	3.5.1
Release:	1
Summary:	Simplified packaging of Python modules

# ./flit/log.py under ASL 2.0 license
# ./flit/upload.py under PSF license
License:	BSD and ASL 2.0 and Python

URL:		https://flit.readthedocs.io/en/latest/
Source0:	%{name}-%{version}.tar.gz

# For the tests
# https://pypi.org/pypi?%3Aaction=list_classifiers#/classifiers.lst
Source1:	classifiers.lst

BuildArch:	noarch
BuildRequires:	python3-devel
BuildRequires:	pyproject-rpm-macros >= 0-40
BuildRequires:	python3-pip

# Runtime deps needed to build self
BuildRequires:	python3-tomli

%if %{with tests}
# Runtime deps, others
BuildRequires:	python3-requests
BuildRequires:	python3-docutils
BuildRequires:	python3-pygments
BuildRequires:	python3-tomli-w

# Test deps
BuildRequires:	/usr/bin/python
BuildRequires:	python3-pytest
BuildRequires:	python3-responses

# Test deps that require flit to build:
BuildRequires:	python3-testpath
BuildRequires:	python3-requests-download
%endif

%{?python_provide:%python_provide python3-%{srcname}}
Requires:	python3-%{srcname}-core = %{version}-%{release}
# https://pypi.python.org/pypi/tornado
# ./flit/log.py unknown version
Provides:	bundled(python3dist(tornado))

# soft dependency: (WARNING) Cannot analyze code. Pygments package not found.
Recommends:	python3-pygments



%description
Flit is a simple way to put Python packages and modules on PyPI.

Flit only creates packages in the new 'wheel' format. People using older
versions of pip (<1.5) or easy_install will not be able to install them.

Flit packages a single importable module or package at a time, using the import
name as the name on PyPI. All sub-packages and data files within a package are
included automatically.

Flit requires Python 3, but you can use it to distribute modules for Python 2,
so long as they can be imported on Python 3.

%package -n python3-%{srcname}-core
Summary:	PEP 517 build backend for packages using Flit
%{?python_provide:%python_provide python3-%{srcname}-core}
Conflicts:	python3-%{srcname} < 2.1.0-2

%description -n python3-%{srcname}-core
This provides a PEP 517 build backend for packages using Flit.
The only public interface is the API specified by PEP 517,
at flit_core.buildapi.


%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
export FLIT_NO_NETWORK=1
export PYTHONPATH=$PWD:$PWD/flit_core

# first, build flit_core with self

cd flit_core
%pyproject_wheel
cd -

# build of the main flit (needs flit_core)
%pyproject_wheel

%install
%pyproject_install

# don't ship tests in flit_core package
# if upstream decides to change the installation, it can be removed:
# https://github.com/takluyver/flit/issues/403
rm -r %{buildroot}%{python3_sitelib}/flit_core/tests/

%if %{with tests}
%check
# flit attempts to download list of classifiers from PyPI, but not if it's cached
# test_invalid_classifier fails without the list
mkdir -p fake_cache/flit
cp %{SOURCE1} fake_cache/flit
export XDG_CACHE_HOME=$PWD/fake_cache

%pytest
%endif


%files -n python3-%{srcname}
%license LICENSE
%doc README.rst
%{python3_sitelib}/flit-*.dist-info/
%{python3_sitelib}/flit/
%{_bindir}/flit


%files -n python3-%{srcname}-core
%license LICENSE
%doc flit_core/README.rst
%{python3_sitelib}/flit_core-*.dist-info/
%{python3_sitelib}/flit_core/
