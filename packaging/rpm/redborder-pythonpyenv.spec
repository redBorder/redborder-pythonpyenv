%define debug_package %{nil}
%global __brp_strip %{nil}

%global pyenv_root %{__pyenv_root}
%global python_version %{__python_version}

# =====================
# redborder-agents
# =====================
%global redborder_agents_dir /opt/redborder-agents
%global redborder_agents_venv_path %{redborder_agents_dir}/venv
%global redborder_agents_webui_venv_path %{redborder_agents_dir}/src/redborder_agents/servers/webui/.venv

# =====================
# airflow
# =====================
%global airflow_dir /opt/airflow
%global airflow_venv_path %{airflow_dir}/venv

%global __provides_exclude ^python3$|libpython3\.11\.so\.1\.0.*|libpython3\.so.*|libsqlite3.*

# =====================
# redborder-agents
# =====================
%global __provides_exclude_from %{pyenv_root}/.*|%{redborder_agents_dir}/.*
%global __requires_exclude ^python3$
%global __requires_exclude_from %{pyenv_root}/.*|%{redborder_agents_dir}/.*

# =====================
# airflow
# =====================
%global __provides_exclude_from %{pyenv_root}/.*|%{airflow_dir}/.*
%global __requires_exclude_from %{pyenv_root}/.*|%{airflow_dir}/.*

%undefine __brp_mangle_shebangs

Name: redborder-pythonpyenv
Version: %{__version}
Release: %{__release}%{?dist}
Summary: Python 3.11.13 with pyenv in /opt/redborder/pyenv
License: MIT
ExclusiveArch: x86_64

Source0: redborder-agents_requirements.txt
Source1: mcp-server-webui_requirements.txt
Source2: airflow_requirements.txt

BuildRequires: gcc, gcc-c++, make, zlib-devel, bzip2-devel, readline-devel, sqlite-devel, openssl-devel, xz-devel, libffi-devel, git, curl, autoconf, automake, libtool, gcc-gfortran, autoconf, openblas-devel, wget, unzip, findutils, libvirt-devel, pkgconfig, krb5-devel, mariadb-devel, graphviz-devel, openldap-devel

Requires: bash, openblas-devel

%description
This package installs pyenv into %{pyenv_root}, Python %{python_version}, and two virtualenvs: one for redborder-agents and another for the webui MCP server.

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
export LDFLAGS="-L$SQLITE_PREFIX/lib -Wl,-rpath,$SQLITE_PREFIX/lib"
export LD_RUN_PATH="$SQLITE_PREFIX/lib"
export PKG_CONFIG_PATH="$SQLITE_PREFIX/lib/pkgconfig"
export CONFIGURE_OPTS="--with-ensurepip=install --enable-loadable-sqlite-extensions"
export MAKE_OPTS="-j$(nproc)"

# Compilar Python con pyenv
eval "$(%{pyenv_root}/bin/pyenv init -)"
%{pyenv_root}/bin/pyenv install %{python_version}
%{pyenv_root}/bin/pyenv global %{python_version}
PYTHON_BIN=%{pyenv_root}/versions/%{python_version}/bin/python3

# Preparar entorno virtual
$PYTHON_BIN -m pip install --upgrade pip setuptools virtualenv

# =====================
# VENV redborder-agents
# =====================
mkdir -p %{redborder_agents_dir}
$PYTHON_BIN -m venv %{redborder_agents_venv_path}
%{redborder_agents_venv_path}/bin/pip install --upgrade pip setuptools
%{redborder_agents_venv_path}/bin/pip install --no-deps -r $RPM_SOURCE_DIR/redborder-agents_requirements.txt

# Verificar SQLite y crewai
%{redborder_agents_venv_path}/bin/python -c "import sqlite3; print('SQLite:', sqlite3.sqlite_version)"
%{redborder_agents_venv_path}/bin/python -c "import crewai; print('CrewAI:', crewai.__version__)"

# =====================
# VENV webui MCP server
# =====================
mkdir -p $(dirname %{redborder_agents_webui_venv_path})
$PYTHON_BIN -m venv %{redborder_agents_webui_venv_path}
%{redborder_agents_webui_venv_path}/bin/pip install --upgrade pip setuptools
%{redborder_agents_webui_venv_path}/bin/pip install --no-deps -r $RPM_SOURCE_DIR/mcp-server-webui_requirements.txt

# Verificar MCP
%{redborder_agents_webui_venv_path}/bin/python -c "import importlib.metadata; print('MCP:', importlib.metadata.version('mcp'))"

# =====================
# VENV airflow
# =====================
mkdir -p %{airflow_dir}
$PYTHON_BIN -m virtualenv %{airflow_venv_path}
%{airflow_venv_path}/bin/pip install -r $RPM_SOURCE_DIR/airflow_requirements.txt

%install
mkdir -p %{buildroot}%{pyenv_root}
cp -a %{pyenv_root}/. %{buildroot}%{pyenv_root}/
mkdir -p %{buildroot}%{redborder_agents_dir}
cp -a %{redborder_agents_dir}/. %{buildroot}%{redborder_agents_dir}/
mkdir -p %{buildroot}%{airflow_dir}
cp -a %{airflow_dir}/. %{buildroot}%{airflow_dir}/

%files
%{pyenv_root}
%{redborder_agents_venv_path}
%{redborder_agents_webui_venv_path}
%{airflow_venv_path}

%changelog
* Tue Sep 09 2025 Vicente Mesa <vimesa@redborder.com>
- Add airflow venv

* Wed Sep 10 2025 Rafael Gómez <rgomez@redborder.com>
- Improve performance of RPM builiding and split up redborder-agents venv

* Sat Aug 9 2025 manegron <manegron@redborder.com>
- Excluir algunas librerias internas como provides 

* Thu Jul 17 2025 manegron <manegron@redborder.com>
- Instala redborder-agents y dependencias en virtualenv aislada, y python 3.11

* Thu Jul 17 2025 manegron <manegron@redborder.com>
- Instala pyenv y Python 3.10.14 en /opt/redborder/pyenv
