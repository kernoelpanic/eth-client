#!/bin/bash

echo "Running entrypoint script..."
pwd
# test run geth
#geth --version

if [ -e ./datadir/bob/initialized ] && [ ! -e ./datadir/bob/initlock ]; then
    echo "Running geth ..."
    exec geth --verbosity 5 --networkid '20251201' --config ${WORKDIR_CONTAINER}/config.toml
else
    # This finishes fasts and terminates
    # container will be restarted by docker compose after termination
    echo "Initializing geth ..."
    touch ${WORKDIR_CONTAINER}/datadir/bob/initlock
    geth \
    --identity 'bob' \
    --networkid '20251201' \
    --datadir ${WORKDIR_CONTAINER}/datadir/bob \
    --verbosity 5 \
    init ${WORKDIR_CONTAINER}/genesis.json

    echo "Initialization complete, cleaning up ..."
    touch ${WORKDIR_CONTAINER}/datadir/bob/initialized
    rm ${WORKDIR_CONTAINER}/datadir/bob/initlock
    exit
fi
