#!/bin/bash

docker exec -u 1000 -it $(docker ps | grep notebookcnt | cut -d" " -f1) '/bin/bash'
