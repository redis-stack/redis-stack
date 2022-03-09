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

${CMD} \
${CONFFILE} -- \
--dir ${REDIS_DATA_DIR} \
--protected-mode no \
--loadmodule /opt/redis-stack/lib/redisearch.so \
${REDISEARCH_ARGS} \
--loadmodule /opt/redis-stack/lib/redisgraph.so \
${REDISGRAPH_ARGS} \
--loadmodule /opt/redis-stack/lib/redistimeseries.so \
${REDISTIMESERIES_ARGS} \
--loadmodule /opt/redis-stack/lib/rejson.so \
${REJSON_ARGS} \
--loadmodule /opt/redis-stack/lib/redisbloom.so \
${REDISBLOOM_ARGS} \
${REDIS_ARGS}
