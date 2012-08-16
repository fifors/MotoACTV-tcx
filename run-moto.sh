#!/bin/bash

IN=$1
OUT=$2
MOTO="./motoactv_tcx.py"
TD=`which tidy`

if [ ! -f ${MOTO} ]
then
    echo ${MOTO} doesn\'t exist
    exit 1
fi

if [ ! -z ${TD} ]
then
    TIDY='| tidy -q -i -xml'
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

eval "${MOTO} ${IN} ${TIDY} > ${OUT}"

if [ ! $? ]
then
    echo Had problems running the converter
    rm -f ${OUT}
fi

echo "TCX file written to: ${OUT}"
