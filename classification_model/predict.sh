#!/bin/bash

PYTHON_PATH="${PYTHON_PATH:-python}"

INPUT_PATH=$1
MODEL_PATH=$2
FEATURES_PATH=$3
TMP_PATH=$4

N_PROCESS=3


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"



$PYTHON_PATH ${SCRIPT_DIR}/prepare_file.py ${INPUT_PATH} ${FEATURES_PATH} ${TMP_PATH}/predict_prepared_data_${CLASSIFICATION}.tsv.gz

$PYTHON_PATH ${SCRIPT_DIR}/predict.py ${TMP_PATH}/predict_prepared_data_${CLASSIFICATION}.tsv.gz ${MODEL_PATH}


