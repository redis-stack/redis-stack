# Some pointers to run the docker

There are two dockers that we build:

* redis-stack - redis, the modules, and redisinsight
* redis-stack-server - redis and the modules

Examples below highlight redis-stack, but the only actual difference is a lack of port *8001*


Environment variables that can be set on the docker image:

**All optional arguments**

* REDISBLOOM_ARGS - arguments to pass when loading the bloom module
* REDISEARCH_ARGS - arguments to pass when loading the search module
* REJSON_ARGS - arguments to pass when loading the json module
* REDISTIMESERIES_ARGS - arguments to pass when loading the timeseries module
* REDISGRAPH_ARGS - arguments to pass when loading the graph module
* REDIS_ARGS - extra arguments to pass to redis

Ports that need plumbing
- 6379 - the redis instance
- 8001 - the redisinsight instance

---------------

To persist data outside of the docker you're going to *need* to include the following options prior to the image (redislabs/redis-stack:edge).

-v /path/to/redisinsight/data:/redisinsight
-v /path/to/your/redis-data:/data/

Example, with the current directory containing something called data which hosts our data.

```
docker run -v `pwd`/data/redisinsight:/redisinsight -v `pwd`/redis:/data -p 6379:6379 -p 8001:8001 redislabs/redis-stack:edge
```

```

### Run redis stack with ports 6379 (redis) and 8001 (redisinsight) tunneled back to your machine
```
docker run -p 6379:6379 -p 8001:8001 redislabs/redis-stack:edge
```

### Same as the prior item, but running in the background (i.e disconnected)
```
docker run -d -p 6379:6379 -p 8001:8001 redislabs/redis-stack:edge
```
### Run redis stack on another port: 5555 (redis) and 9999 (redisinsight) tunneled back to your machine
```
docker run -p 5555:6379 -p 9999:8001 redislabs/redis-stack:edge
```


### Start, while loading extra options for the redis-server in a configuration file named *redis-stack.conf* stored outside the docker

```
docker run -v `pwd`/redis-stack.conf:/redis-stack.conf -p 6379:6379 -p 8001:8001 redislabs/redis-stack:edge
```

### Start redis stack, passing in additional arguments to the REDISTIMESERIES module (such as retention time)

```
docker run -e REDISTIMESERIES_ARGS="RETENTION_POLICY=20" -p 6379:6379 -p 8001:8001 redislabs/redis-stack:edge
```

### Start redis stack, setting the password *redis-stack*

```
docker run -e REDIS_ARGS="--requirepass redis-stack" -p 6379:6379 -p 8001:8001 redislabs/redis-stack:edge
```
