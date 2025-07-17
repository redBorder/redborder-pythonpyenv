# redborder-pythonpyenv

This project install pyenv with python 3.11.13 and virtual environment
for dependencies of redborder_agents service and redborder webui mcp
server.

## Build
```
make rpm
```
Note: 
Remember to keep up to date redborder-agents_requirements.txt
and mcp-server-webui_requeriments.txt before build.

## Installation
```
dnf install redborder-pythonpyenv
```

## Testing redborder-agents virtual environment
```
source /opt/redborder-agents/venv/bin/activate
python -c 'import crewai; print('\''CrewAI version:'\'', crewai.__version__)'
```
