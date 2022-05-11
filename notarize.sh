#!/bin/sh

if [ -z $1 ]; then
    echo "Usage: $0 {file_to_notarize.zip} {bundle name} {notarization username} {notarization password}"
    exit 3
fi

ZIPFILE=$1  # path to zipfile
BUNDLE=$2   # eg com.redis.redis-stack-server
USERNAME=$3
PASSWORD=$4

if [ ! -f ${ZIPFILE} ]; then
    echo "${ZIPFILE} is not a file, exiting."
    exit 3
fi

PACKAGE_ID=`xcrun altool --notarize-app --primary-bundle-id ${BUNDLE} --username "${USERNAME}" --password "${PASSWORD}" --file ${ZIPFILE}|grep RequestUUID|cut -d "=" -f 2-2`
echo "Checking status for package ${PACKAGE_ID}"

for i in `seq 1 20`; do
    status=`xcrun altool --notarization-info ${PACKAGE_ID} --username "${USERNAME}" --password "${PASSWORD}"|grep "Status:" | cut -d ":" -f 2-2|awk '{print $1}'`
    echo "Status is - ${status}"
    if [ "${status}" == "invalid" ]; then
        echo "Notarization failed, exiting."
        exit 1
    elif [ "${status}" == "success" ]; then
        echo "Notarization succeeded!"
        exit 0
    fi
    echo "Sleeping one minute between notarization checks".
    sleep 60
done

echo "No succesful notarization found, exiting."
exit 1
