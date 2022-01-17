#!/bin/bash

if [[ -z ${OS} || -z ${OSNICK} || -z ${ARCH} || -z ${REDIS_BINARIES} ]]; then
    echo "All of OS, OSNICK, ARCH, and REDIS_BINARIES must all be defined."
    exit 3
fi

if [ -z ${VARIANT} ]; then
VARIANT=${OSNICK}-${ARCH}
fi

if [ -z ${1} ]; then
    echo "Usage: ${0} {deb|rpm}"
    exit 3
fi

PRODUCT=redis-stack
BASE_DIR=deps
BINARY_DEPS=${BASE_DIR}/external/${VARIANT}
BASE_PRODUCT_PATH=${BASE_DIR}/${VARIANT}/opt/${PRODUCT}
BINDIR=${BASE_PRODUCT_PATH}/bin
LIBDIR=${BASE_PRODUCT_PATH}/lib

mkdir -p ${BASE_PRODUCT_PATH}/{bin,lib,conf,share}

if [ -z ${REDISJSON_VERSION} ]; then
    REDISJSON_VERSION=2.0.6
fi
if [ -z ${REDISGRAPH_VERSION} ]; then
    REDISGRAPH_VERSION=2.8.7
fi

if [ -z ${REDISTIMESERIES_VERSION} ]; then
    REDISTIMESERIES_VERSION=1.6.5
fi

if [ -z ${REDISEARCH_VERSION} ]; then
    REDISEARCH_VERSION=2.2.6
fi

if [ -z ${REDISGEARS_VERSION} ]; then
    REDISGEARS_VERSION=1.2.1
fi


if [ -z ${REDISBLOOM_VERSION} ]; then
    REDISBLOOM_VERISION=1.1.1
fi

AWS_S3_BUCKET=redismodules.s3.amazonaws.com
MODULE_LIST="redistimeseries/redistimeseries.${OS}-${OSNICK}-${ARCH}.${REDISTIMESERIES_VERSION}.zip
redisgraph/redisgraph.${OS}-${OSNICK}-${ARCH}.${REDISGRAPH_VERSION}.zip
rejson/rejson.${OS}-${OSNICK}-${ARCH}.${REDISJSON_VERSION}.zip
"
#redisearch/redisearch.${OS}-${OSNICK}-${ARCH}.${REDISJSON_VERSION}.zip
#redisgears/redisgears.${OS}-${OSNICK}-${ARCH}.${REDISJSON_VERSION}.zip

set -e
for m in ${MODULE_LIST}; do
    module=`echo $m|cut -d '/' -f 1-1`
    mkdir -p ${BINARY_DEPS}
    destzip=${BINARY_DEPS}/${module}.zip
    if [ ! -f ${destzip} ]; then
        wget https://${AWS_S3_BUCKET}/${m} -O ${destzip}
        unzip -p ${destzip} ${module}.so > ${BASE_PRODUCT_PATH}/lib/${module}.so || unzip -p ${destzip} ${module}-enterprise.so > ${BASE_PRODUCT_PATH}/lib/${module}.so
        if [ $? -ne 0 ]; then
            echo "Failed to get ${module}.so from ${destzip}. Exiting."
            exit 3
        fi
    fi
done

cp ${REDIS_BINARIES}/redis* ${BASE_PRODUCT_PATH}/bin

chmod 0755 ${BINDIR}/* ${LIBDIR}/*

## REDIS STACK RULES
VENDOR="Redis Inc"
VERSION="1.0.0"
EMAIL="Redis OSS <oss@redislabs.com>"
LICENSE="MIT"
PRODUCT_USER=redis
PRODUCT_GROUP=redis

function deb() {
    fpm \
        -s dir \
        -t deb \
        -C `pwd`/deps/${OSNICK}-${ARCH} \
        -n ${PRODUCT} \
        --provides redis \
        --provides redis-server \
        --architecture ${ARCH} \
        --vendor "${VENDOR}" \
        --version ${VERSION} \
        --url "https://redistack.io" \
        --license ${LICENSE} \
        --category server \
        --maintainer "${EMAIL}" \
        --deb-user ${PRODUCT_USER} \
        --deb-group ${PRODUCT_GROUP}
}

function rpm() {
    fpm \
        -s dir \
        -t rpm \
        -C `pwd`/deps/${OSNICK}-${ARCH} \
        -n ${PRODUCT} \
        --provides redis \
        --provides redis-server \
        --architecture ${ARCH} \
        --vendor "${VENDOR}" \
        --version ${VERSION} \
        --url "https://redistack.io" \
        --license ${LICENSE} \
        --category server \
        --maintainer "${EMAIL}" \
        --rpm-user ${PRODUCT_USER} \
        --rpm-group ${PRODUCT_GROUP}
}

$1
