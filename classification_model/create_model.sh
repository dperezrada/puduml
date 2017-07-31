#!/bin/bash

PYTHON_PATH="${PYTHON_PATH:-python}"
CAT_BIN="${CAT_BIN:-zcat}"

INPUT_PATH=$1
CLASSIFICATION=$2
FEATURES_PATH=$3
TARGET_PATH=$4
N_PROCESS=$5

if [[ -z "$N_PROCESS" ]]; then
	N_PROCESS=2
fi

TRAIN_SPLIT=0.7


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


mkdir -p ${TARGET_PATH}/tmp
mkdir -p ${TARGET_PATH}/model/


$CAT_BIN ${INPUT_PATH} |
	awk -F$'\t' -v CLASSIFICATION=${CLASSIFICATION} 'BEGIN{OFS=FS}{if($2!=CLASSIFICATION){$2="other"};print $0}' |
	gzip > ${TARGET_PATH}/tmp/base_input_${CLASSIFICATION}.tsv.gz

$PYTHON_PATH ${SCRIPT_DIR}/prepare_file.py ${TARGET_PATH}/tmp/base_input_${CLASSIFICATION}.tsv.gz ${FEATURES_PATH} ${TARGET_PATH}/tmp/prepared_data_${CLASSIFICATION}.tsv.gz ${N_PROCESS}

$PYTHON_PATH ${SCRIPT_DIR}/train_model.py ${TARGET_PATH}/tmp/prepared_data_${CLASSIFICATION}.tsv.gz ${TARGET_PATH}/model/${CLASSIFICATION}.pkl ${TARGET_PATH}/model/${CLASSIFICATION}.results ${N_PROCESS} ${TRAIN_SPLIT}

cat ${TARGET_PATH}/model/${CLASSIFICATION}.results

