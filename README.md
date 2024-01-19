# Smart contract test environment

This ethereum smart contract test environment is used in the lecture [Security and Privacy Engineering](https://ufind.univie.ac.at/en/course.html?lv=052011&semester=2023W) at the university of Vienna. 

## For students

Place your private key file (in json format) in a folder called `../keystore`  outside this repository. 
Then run
```bash
$ UID=$(id -u) GID=$(id -g) docker compose up -d  
# or
$ UID=${UID} GID=${GID} docker compose up -d  
```
If you want to rebuild the containers run `docker compose up --build`.
You can access all containers log output via `docker compose logs --follow`.

Connect to your local jupyter notebook, the url will be in the logs of the `notebook` container (`notebookcnt`).
Then check the connection to our geth PoA node by going over the connection test notebook
[connection_test.ipynb](./notebook/connection_test.ipynb).

The source code of the challenges, as well as their ABI can be found in the folder [challenges](./notebook/challenges).

To familiarize yourself with ethereum and smart contracts we recommend that you look into the jupyter notebook which uses a local test network (created by `anvil`). The notebook [sccc-anvil.ipynb](./notebook/sccc-anvil.ipynb) illustrates some basic interaction concepts required to solve the challenges. 

Good luck and happy hacking!