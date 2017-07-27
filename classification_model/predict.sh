#!/bin/bash

INPUT_PATH=$1
MODEL_PATH=$2
FEATURES_PATH=$3
PREPARED_FILE=$4

N_PROCESS=3


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"



python ${SCRIPT_DIR}/prepare_file.py ${INPUT_PATH} ${FEATURES_PATH} ${PREPARED_FILE}

python ${SCRIPT_DIR}/predict.py ${PREPARED_FILE} ${MODEL_PATH}


