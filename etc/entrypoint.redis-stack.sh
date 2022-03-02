#!/bin/bash

### docker entrypoint script, for starting redis stack
BASEDIR=/opt/redis-stack
cd ${BASEDIR}

CMD=${BASEDIR}/bin/redis-server
if [ -f /redis-stack.conf ]; then
    CONFFILE=/redis-stack.conf
fi

${CMD} \
${CONFFILE} -- \
--protected-mode no \
--daemonize yes \
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

${BASEDIR}/nodejs/bin/node -r ${BASEDIR}/share/redisinsight/api/node_modules/dotenv/config share/redisinsight/api/dist/src/main.js dotenv_config_path=${BASEDIR}/share/redisinsight/.env
