#!/bin/bash

ARGS=""
FILE=""
FORCE=0

while getopts "fhbpYs:i:t:l:" OPT
do
    case ${OPT} in
        f) FORCE=1
           ;;
        h) echo usage
           exit 0
           ;;
        b) ARGS="${ARGS} -b"
           ;;
        Y) ARGS="${ARGS} -Y"
           ;;
        p) ARGS="${ARGS} -p"
           ;;
        s) ARGS="${ARGS} -s ${OPTARG}"
           ;;
        i) FILE=${OPTARG}
           ;;
        t) ARGS="${ARGS} -t ${OPTARG}"
           ;;
        l) ARGS="${ARGS} -l ${OPTARG}"
           ;;
        :) echo Option -${OPTARG} requires an argument
           exit 1
           ;;
        *) echo Invalid option: -$OPTARG
           exit 1
           ;;
    esac
done

shift $((OPTIND-1))

IN=$1
OUT=$2
MOTO="./motoactv_tcx.py"
TD=`which tidy`
TIDY='tidy -q -i -xml'
FILE="OUT-"$$

if [ ! -f ${MOTO} ]
then
    echo ${MOTO} doesn\'t exist
    exit 1
fi

if [ -z ${IN} ]
then
    if [ -z ${FILE} ]
    then
        echo You must enter an input file
        exit 1
    else
        IN=${FILE}
    fi
fi

if [ -z ${OUT} ]
then
    OUT=`echo ${IN} | sed -e "s/.csv$/.tcx/"`
fi

if [ ! "${FORCE}" -eq "1" -a -f ${OUT} ]
then
    echo ${OUT} exists
    exit 1
fi

eval "${MOTO} -i ${IN} ${ARGS} > ${FILE}"

if [ "$?" -ne "0" ]
then
    echo Problems running ${MOTO}, aborting.
    rm ${FILE}
    exit 1
fi

if [ ! -z ${TD} ]
then
   ${TIDY} ${FILE} > ${OUT}
    rm ${FILE}
fi

echo "TCX file written to: ${OUT}"
