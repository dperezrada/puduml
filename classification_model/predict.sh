#!/bin/bash

INPUT_PATH=$1
MODEL_PATH=$2
FEATURES_PATH=$3
PREPARED_FILE=$4
N_PROCESS=$5

if [[ -z "$N_PROCESS" ]]; then
	N_PROCESS=2
fi


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"



python ${SCRIPT_DIR}/prepare_file.py ${INPUT_PATH} ${FEATURES_PATH} ${PREPARED_FILE} ${N_PROCESS}

python ${SCRIPT_DIR}/predict.py ${PREPARED_FILE} ${MODEL_PATH}


