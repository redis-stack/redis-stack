#!/bin/bash

### docker entrypoint script, for starting redis stack
BASEDIR=/opt/redis-stack
cd ${BASEDIR}

${BASEDIR}/bin/redis-server ${BASEDIR}/etc/redis-stack.conf