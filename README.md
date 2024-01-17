# Smart contract test environment

This ethereum smart contract test environment is used in the lecture [Security and Privacy Engineering](https://ufind.univie.ac.at/en/course.html?lv=052011&semester=2023W) at the university of Vienna. 

## For students

Place your private key file (in json format) in a folder called `../keystore`  outside this repository. 
Then run
```bash
$ docker compose up -d
```
If you want to rebuild the containers run `docker compose up --build`.
You can access all containers log output via `docker compose logs --follow`.



