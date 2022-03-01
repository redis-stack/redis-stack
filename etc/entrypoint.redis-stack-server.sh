#!/bin/bash

### docker entrypoint script, for starting redis stack
BASEDIR=/opt/redis-stack
cd ${BASEDIR}

if [ -f /redis-stack.conf ]; then
CMD=${BASEDIR}/bin/redis-server
    CONFFILE=/redis-stack.conf
fi

${CMD} \
${CONFFILE} -- \
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
${REDISBLOOM_ARGS}