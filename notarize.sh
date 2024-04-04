#!/bin/sh

if [ -z $1 ]; then
    echo "Usage: $0 {file_to_notarize.zip} {bundle name} {notarization username} {notarization password}"
    exit 3
fi

ZIPFILE=$1  # path to zipfile
BUNDLE=$2   # eg com.redis.redis-stack-server
USERNAME=$3
PASSWORD=$4
TEAM_ID=$5

if [ ! -f ${ZIPFILE} ]; then
    echo "${ZIPFILE} is not a file, exiting."
    exit 3
fi

PACKAGE_ID=`xcrun notarytool submit ${ZIPFILE} --apple-id "${USERNAME}" --password "${PASSWORD}" --team-id "${TEAM_ID}" --wait|grep "id:" | head -1 | cut -d ":" -f 2-2|awk '{print $1}'`
echo "Checking status for package ${PACKAGE_ID}"

for i in `seq 1 20`; do
    status=`xcrun notarytool info ${PACKAGE_ID} --apple-id "${USERNAME}" --password "${PASSWORD}" --team-id "${TEAM_ID}"|grep "status:" | head -1 | cut -d ":" -f 2-2|awk '{print $1}'`
    echo "Status is - ${status}"
    if [ "${status}" == "Accepted" ]; then
        echo "Notarization succeeded!"
        exit 0
    else
        echo "Notarization failed, exiting."
        exit 1
    fi
    echo "Sleeping one minute between notarization checks".
    sleep 60
done

echo "No succesful notarization found, exiting."
exit 1
