#!/bin/bash

DATA_PATH=/media/ClueWeb09
TEMP_FILE=./temp

mkdir -p $TEMP_FILE

usage="Usage: $0 <WARC-TREC-ID like clueweb09-en0000-00-12345>"

if [ $# -eq 0 ]; then
    echo $usage
    exit 1;
fi

TRECID=$1

dirname=`echo $TRECID | awk -F '-' '{print $2}'`
section=`echo $TRECID | awk -F '-' '{print $3}'`
record=`echo $TRECID | awk -F '-' '{print $4}'`

if [ "$(echo $TRECID | grep -Eoi clueweb09)" == "" ]; then

    dirname=`echo $TRECID | awk -F '-' '{print $1}'`
    section=`echo $TRECID | awk -F '-' '{print $2}'`
    record=`echo $TRECID | awk -F '-' '{print $3}'`

fi

dirpath=$(find $DATA_PATH -name "$dirname" 2>/dev/null)
filename=$dirpath/${section}.warc.gz

echo $filename

exit 0

unzipfile=$TEMP_FILE/$dirname-${section}.warc

if [ -f $unzipfile ]; then
    echo $unzipfile
    exit 0
fi

if [ -f $filename ]; then
    gzip -d $filename -c > $unzipfile
    echo $unzipfile
    exit 0
else
    echo "$filename does not exist."
    exit 1
fi



