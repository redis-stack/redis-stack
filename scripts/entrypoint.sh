#!/bin/bash

### docker entrypoint script, for starting redis stack
BASEDIR=/opt/redis-stack
cd ${BASEDIR}

${BASEDIR}/bin/redis-server ${BASEDIR}/etc/redis-stack.conf
SERVER_STATIC_CONTENT=1 API_PORT=8081 ${BASEDIR}/nodejs/bin/node share/redisinsight/server/src/main.js
