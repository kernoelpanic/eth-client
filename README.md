# Smart contract test environment

This ethereum smart contract test environment is used in the lecture [Security and Privacy Engineering](https://ufind.univie.ac.at/en/course.html?lv=052011&semester=2023W) at the university of Vienna.

## For students

Make sure to have the following folders created
relative to the repository folder for the docker volumes:

- `../keystore/`
- `geth/datadir/bob/keystore/`
- `notebook/geth/`

The directories should exist for `docker-compose up` to work without errors.

You could add them like this:

```
$ mkdir ../keystore
$ mkdir -p geth/datadir/bob/keystore
$ mkdir notebook/geth
```

Place your private key file (in json format) in a folder called `../keystore`  outside this repository.
Then run the following commands (the first build might take a while because it fetches and builds geth from source).
```bash
$ docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
# the run the containers
$ docker compose up -d
```
You can access the log output of all running containers `docker compose logs --follow`.

If `geth-client-cnt` experience issues arise, try restarting the
containers (`docker-compose down` followed by `up -d`)
or try to fix the permissions on the `geth/datadir`
directory:
```bash
$ chown -R o+x,o+r,o+w geth/datadir
```

In some cases, deleting the `geth/datadir/bob/geth` folder and
`geth/datadir/bob/initialized` to start the sync anew could also help.

If your `notebook-cnt` experiences issues such as:
```bash
...
notebookcnt      | /smartenv/entrypoint.sh: line 33: exec: jupyter-lab: not found
...
```
Try to remove the python virtual env directory which is used in the volume inside the container:
```bash
$ rm -r notebook/venv
```

Connect to your local jupyter notebook, the url will be in the logs of the `notebook` container (`docker compose logs notebookcnt`).
Then check the connection to our geth PoA node by going over the connection test notebook
[connection_test.ipynb](./notebook/connection_test.ipynb).

The source code of the challenges, as well as their ABI can be found in the folder [challenges](./notebook/challenges).

To familiarize yourself with ethereum and smart contracts we recommend that you look into the jupyter notebook which uses a local test network (created by `anvil`). The notebook [sccc-anvil.ipynb](./notebook/sccc-anvil.ipynb) illustrates some basic interaction concepts required to solve the challenges.

Good luck and happy hacking!
