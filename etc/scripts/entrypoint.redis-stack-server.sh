#!/usr/bin/dumb-init /bin/sh

### docker entrypoint script, for starting redis stack
BASEDIR=/opt/redis-stack
cd ${BASEDIR}

CMD=${BASEDIR}/bin/redis-server
if [ -f /redis-stack.conf ]; then
    CONFFILE=/redis-stack.conf
fi

if [ -z ${REDIS_DATA_DIR} ]; then
    REDIS_DATA_DIR=/data
fi

if [ -z ${REDISEARCH_ARGS} ]; then
REDISEARCH_ARGS="MAXSEARCHRESULTS 10000 MAXAGGREGATERESULTS 10000"
fi

if [ -z ${REDISGRAPH_ARGS} ]; then
REDISGRAPH_ARGS="MAX_QUEUED_QUERIES 25 TIMEOUT 1000 RESULTSET_SIZE 10000"
fi

${CMD} \
${CONFFILE} -- \
--dir ${REDIS_DATA_DIR} \
--protected-mode no \
--loadmodule /opt/redis-stack/lib/redisearch.so \
MAXSEARCHRESULTS 10000 MAXAGGREGATERESULTS 10000 ${REDISEARCH_ARGS} \
--loadmodule /opt/redis-stack/lib/redisgraph.so \
MAX_QUEUED_QUERIES 25 TIMEOUT 1000 RESULTSET_SIZE 10000 ${REDISGRAPH_ARGS} \
--loadmodule /opt/redis-stack/lib/redistimeseries.so ${REDISTIMESERIES_ARGS} \
--loadmodule /opt/redis-stack/lib/rejson.so ${REDISJSON_ARGS} \
--loadmodule /opt/redis-stack/lib/redisbloom.so ${REDISBLOOM_ARGS} \
${REDIS_ARGS}
