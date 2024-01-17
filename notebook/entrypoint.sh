#!/bin/bash

PYTHON_VENV_PATH="./venv"
PYTHON_REQUIREMENTS="./requirements.txt"

echo "Running entrypoint script..."

if [ -z "${1}" ] && [ -z "${CONTAINER_PORT+x}" ];
then 
	export CONTAINER_PORT=8888
elif [ ! -z "${1}" ];
then
	export CONTAINER_PORT="${1}"
fi

# Check if python virtual env and use it
# or create it and install stuff otherwise
if test -f "${PYTHON_VENV_PATH}/bin/activate"; then
  echo "VENV exists"
  . ${PYTHON_VENV_PATH}/bin/activate
else
  echo "VENV is created"
  python -m venv venv
  . ${PYTHON_VENV_PATH}/bin/activate
  # fix for
  # error: invalid command 'bdist_wheel'
  pip install wheel
  python -m pip install -r ${PYTHON_REQUIREMENTS}
fi

. ${PYTHON_VENV_PATH}/bin/activate 
#jupyter notebook --ip "0.0.0.0" --port ${CONTAINER_PORT}
exec jupyter-lab --ip "0.0.0.0" --port ${CONTAINER_PORT}