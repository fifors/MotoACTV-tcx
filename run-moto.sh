#!/bin/bash

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
    echo You must enter an input file
    exit 1
fi

if [ -z ${OUT} ]
then
    OUT=`echo ${IN} | sed -e "s/.csv$/.tcx/"`
fi

if [ -f ${OUT} ]
then
    echo ${OUT} exists
    exit 1
fi

eval "${MOTO} -i ${IN} > ${FILE}"

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
