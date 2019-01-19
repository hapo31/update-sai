# update_sai

Update your twitter screen name when tweeted keyword.

## Initialize

```
$ mv config.py.template ./src/config.py
```

Edit src/config.py in consumer_key, consumer_secret, access_token and access_secret.

```
$ vi ./src/config.py
```

After

```
$ python3 ./src/db_up.py
$ ./build.sh
```

## Build Docker image

```
$ ./build.sh
```

## Run

```
$ ./run.sh
```
