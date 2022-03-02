# Some pointers to run the docker

There are two dockers that we build:


Environment variables that can be set on the docker image:

**All optional arguments**

REDISBLOOM_ARGS - arguments to pass when loading the bloom module
REDISEARCH_ARGS - arguments to pass when loading the search module
REJSON_ARGS - arguments to pass when loading the json module
REDISTIMESERIES_ARGS - arguments to pass when loading the timeseries module
REDISGRAPH_ARGS - arguments to pass when loading the graph module
REDIS_ARGS - extra arguments to pass to redis

Ports that need plumbing
- 6379 - the redis instance
- 8001 - the redisinsight instance

---------------

### Run redis stack with ports 6379 (redis) and 8001 (redisinsight) tunneled back to your machine
```
docker run -p 6379:6379 -p 8001:8001 redislabs/redis-stack:latest
```


### Run redis stack on another port: 5555 (redis) and 9999 (redisinsight) tunneled back to your machine
```
docker run -p 5555:6379 -p 9999:8001 redislabs/redis-stack:latest
```


### Start, while loading extra options for the redis-server in a configuration file named *redis-stack.conf* stored outside the docker

```
docker run -v `pwd`/redis-stack.conf:/redis-stack.conf -p 6379:6379 -p 8001:8001 redislabs/redis-stack:latest
```

### Start redis stack, passing in additional arguments to the REDISTIMESERIES module (such as retention time)

```
docker run -e REDISTIMESERIES_ARGS="RETENTION_POLICY=20" -p 6379:6379 -p 8001:8001 redislabs/redis-stack:latest
```

### Start redis stack, setting the password *redis-stack*

```
docker run -e REDIS_ARGS="--requirepass redis-stack" -p 6379:6379 -p 8001:8001 redislabs/redis-stack:latest
```