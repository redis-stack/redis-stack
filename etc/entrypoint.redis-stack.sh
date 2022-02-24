#!/bin/bash

### docker entrypoint script, for starting redis stack
BASEDIR=/opt/redis-stack
cd ${BASEDIR}

${BASEDIR}/bin/redis-server ${BASEDIR}/etc/redis-stack.conf
${BASEDIR}/nodejs/bin/node -r ${BASEDIR}/share/redisinsight/api/node_modules/dotenv/config share/redisinsight/api/dist/src/main.js dotenv_config_path=${BASEDIR}/share/redisinsight/.env
