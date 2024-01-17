#!/bin/bash

echo "Running entrypoint script..."
pwd
# test run geth 
#geth --version

if [ -e ./datadir/bob/initialized ] && [ ! -e ./datadir/bob/initlock ];
    then 
        echo "Running geth ..."
        exec geth \
        --identity 'bob' \
        --networkid '20240101' \
        --datadir ${WORKDIR_CONTAINER}/datadir/bob \
        --http \
        --http.port 8545 \
        --http.addr 0.0.0.0 \
        --http.api 'eth,net,web3,personal,debug,admin,miner,txpool,clique' \
        --http.corsdomain '*' \
        --http.vhosts '*' \
        --allow-insecure-unlock \
        --ipcdisable \
        --nodiscover \
        --metrics \
        --verbosity 6 \
        #console # does not work if no console is given with -it in docker
        #   --bootnodes "$(cat ${WORKDIR_CONTAINER}/enodes)" \
    else
        # This finishes fasts and terminates 
        # container will be restarted by docker compose after termination
        echo "Initializing geth ..."
        touch ./datadir/bob/initlock
        geth \
        --identity 'bob' \
        --networkid '20240101' \
        --datadir ${WORKDIR_CONTAINER}/datadir/bob \
        --verbosity 6 \
        init ${WORKDIR_CONTAINER}/genesis.json 
        
        echo "Initialization compleate, cleaning up ..."
        touch ./datadir/bob/initialized
        rm ./datadir/bob/initlock
        exit 
fi





