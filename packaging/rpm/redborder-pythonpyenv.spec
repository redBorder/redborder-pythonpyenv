%define debug_package %{nil}

%global pyenv_root %{__pyenv_root}
%global python_version %{__python_version}
%global redborder_agents_dir /opt/redborder-agents
%global redborder_agents_venv_path %{redborder_agents_dir}/venv

%global __provides_exclude ^python3$
%global __provides_exclude_from ^%{pyenv_root}/.*
%global __requires_exclude ^python3$
%global __requires_exclude_from ^%{pyenv_root}/.*

%global __provides_exclude_from ^%{redborder_agents_dir}/.*
%global __requires_exclude_from ^%{redborder_agents_dir}/.*

%global __requires_exclude ^/usr/local/bin/python$

%global __provides_exclude_from libpython3.*
%global __provides_exclude_from libsqlite3.*


%undefine __brp_mangle_shebangs

Name: redborder-pythonpyenv
Version: %{__version}
Release: %{__release}%{?dist}
Summary: Python 3.11.13 with pyenv in /opt/redborder/pyenv
License: MIT
ExclusiveArch: x86_64

Source0: redborder-agents_requirements.txt
Source1: mcp-server-webui_requirements.txt

BuildRequires: gcc, gcc-c++, make, zlib-devel, bzip2-devel, readline-devel, sqlite-devel, openssl-devel, xz-devel, libffi-devel, git, curl, autoconf, automake, libtool, gcc-gfortran, autoconf, openblas-devel

Requires: bash, openblas-devel

%description
This package installs pyenv into %{pyenv_root}, Python %{python_version}, and a virtualenv with crewai and dependencies.

%prep
# No source to unpack

%build
mkdir -p %{pyenv_root}
export PYENV_ROOT=%{pyenv_root}
export PATH="$PYENV_ROOT/bin:$PATH"

# Clonar pyenv
git clone https://github.com/pyenv/pyenv.git %{pyenv_root}

# Instalar SQLite 3.45.3
SQLITE_VERSION=3.45.3
SQLITE_PREFIX=$PYENV_ROOT/.deps/sqlite

mkdir -p $SQLITE_PREFIX
curl -LO https://www.sqlite.org/2024/sqlite-autoconf-3450300.tar.gz
tar xzf sqlite-autoconf-3450300.tar.gz
cd sqlite-autoconf-3450300
./configure --prefix=$SQLITE_PREFIX
make -j$(nproc)
make install
cd ..

# Exportar variables de compilación
export CPPFLAGS="-I$SQLITE_PREFIX/include"
export LDFLAGS="-L$SQLITE_PREFIX/lib"
export LD_RUN_PATH="$SQLITE_PREFIX/lib"
export PKG_CONFIG_PATH="$SQLITE_PREFIX/lib/pkgconfig"
export MAKE_OPTS="-j$(nproc)"

# Forzar rpath para encontrar libsqlite en tiempo de ejecución
export CONFIGURE_OPTS="--with-ensurepip=install --enable-loadable-sqlite-extensions"

# Inicializar pyenv y compilar Python
eval "$(%{pyenv_root}/bin/pyenv init -)"
env \
  CPPFLAGS="$CPPFLAGS" \
  LDFLAGS="$LDFLAGS -Wl,-rpath,$SQLITE_PREFIX/lib" \
  PKG_CONFIG_PATH="$PKG_CONFIG_PATH" \
  CONFIGURE_OPTS="$CONFIGURE_OPTS" \
  MAKE_OPTS="$MAKE_OPTS" \
  %{pyenv_root}/bin/pyenv install %{python_version}

# Usar la versión compilada
%{pyenv_root}/bin/pyenv global %{python_version}

PYTHON_BIN=%{pyenv_root}/versions/%{python_version}/bin/python3

# Preparar entorno virtual
$PYTHON_BIN -m ensurepip
$PYTHON_BIN -m pip install --upgrade pip setuptools virtualenv

# Create redborder-agents venv and install dependencies
mkdir -p %{redborder_agents_dir}

# Create reborder-agents venv
$PYTHON_BIN -m virtualenv %{redborder_agents_venv_path}

# Activate venv and install packages
. %{redborder_agents_venv_path}/bin/activate

%{redborder_agents_venv_path}/bin/pip install --upgrade pip setuptools

# Install from source to avoid problems
%{redborder_agents_venv_path}/bin/pip install --no-binary=:all: numpy scipy

# Install redborder-agents dependencies
%{redborder_agents_venv_path}/bin/pip install -r $RPM_SOURCE_DIR/redborder-agents_requirements.txt

# Install webui mcp server dependencies
%{redborder_agents_venv_path}/bin/pip install -r $RPM_SOURCE_DIR/mcp-server-webui_requirements.txt

# Verificar SQLite y crewai
%{redborder_agents_venv_path}/bin/python -c "import sqlite3; print(sqlite3.sqlite_version)"
%{redborder_agents_venv_path}/bin/python -c "import crewai; print('CrewAI version:', crewai.__version__)"

deactivate

%install
mkdir -p %{buildroot}%{pyenv_root}
cp -a %{pyenv_root}/. %{buildroot}%{pyenv_root}/
mkdir -p %{buildroot}%{redborder_agents_dir}
cp -a %{redborder_agents_dir}/. %{buildroot}%{redborder_agents_dir}/

%files
%{pyenv_root}
%{redborder_agents_venv_path}

%changelog
* Thu Jul 17 2025 manegron <manegron@email>
- Instala redborder-agents y dependencias en virtualenv aislada, y python 3.11

* Thu Jul 17 2025 manegron <manegron@email>
- Instala pyenv y Python 3.10.14 en /opt/redborder/pyenv
