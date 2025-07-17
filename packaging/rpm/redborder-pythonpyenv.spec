%define debug_package %{nil}

%global pyenv_root %{__pyenv_root}
%global python_version %{__python_version}

%undefine __brp_mangle_shebangs

Name: redborder-pythonpyenv
Version: %{__version}
Release: %{__release}%{?dist}
Summary: Python 3.10 with pyenv in /opt/redborder/pyenv
License: MIT
ExclusiveArch: x86_64
Summary: This package installs pyenv and Python through pyenv.

BuildRequires:  gcc, make, zlib-devel, bzip2-devel, readline-devel, sqlite-devel, openssl-devel, xz-devel, libffi-devel, git, curl

Requires:       bash

%description
This package installs pyenv into %{pyenv_root} and installs Python %{python_version} through pyenv.

%prep
# No unpacking needed if you use install-python.sh

%build
mkdir -p %{pyenv_root}
export PYENV_ROOT=%{pyenv_root}
export PATH="$PYENV_ROOT/bin:$PATH"

# Clonar pyenv en buildroot
git clone https://github.com/pyenv/pyenv.git %{pyenv_root}

# Instalar Python con pyenv
eval "$(%{pyenv_root}/bin/pyenv init -)"
%{pyenv_root}/bin/pyenv install %{python_version}
%{pyenv_root}/bin/pyenv global %{python_version}

# Verifica instalación
%{pyenv_root}/versions/%{python_version}/bin/python3 --version

%install
mkdir -p %{buildroot}%{pyenv_root}
cp -a %{pyenv_root}/* %{buildroot}%{pyenv_root}/

%files
%{pyenv_root}

%changelog
* Thu Jul 17 2025 Miguel N. <manegron@email> - 0.0.1
- Instala pyenv y Python 3.10.14 en /opt/redborder/pyenv
