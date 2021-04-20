#!/usr/bin/env bash

if [ "$#" -ne 1 ]; then
    echo "Must pass in script (.sh) name"
    exit 2
fi

SCRIPTNAME=$(basename ${1} .sh);

DIR="${SCRIPTNAME}.app/Contents/MacOS";

if [ -a "${SCRIPTNAME}.app" ]; then
	echo "${PWD}/${SCRIPTNAME}.app already exists :(";
	exit 1;
fi;

mkdir -p "${DIR}";
cp "${1}" "${DIR}/${SCRIPTNAME}";
chmod +x "${DIR}/${SCRIPTNAME}";

echo "${PWD}/${SCRIPTNAME}.app";
