#!/bin/bash

INPUT_PATH=$1
CLASSIFICATION=$2
FEATURES_PATH=$3
TARGET_PATH=$4

N_PROCESS=3
TRAIN_SPLIT=0.7


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


mkdir -p ${TARGET_PATH}/tmp
mkdir -p ${TARGET_PATH}/model/


zcat ${INPUT_PATH} |
	awk -F$'\t' -v CLASSIFICATION=${CLASSIFICATION} 'BEGIN{OFS=FS}{if($2!=CLASSIFICATION){$2="other"};print $0}' |
	gzip > ${TARGET_PATH}/tmp/base_input_${CLASSIFICATION}.tsv.gz

python ${SCRIPT_DIR}/prepare_file.py ${TARGET_PATH}/tmp/base_input_${CLASSIFICATION}.tsv.gz ${FEATURES_PATH} ${TARGET_PATH}/tmp/prepared_data_${CLASSIFICATION}.tsv.gz

python ${SCRIPT_DIR}/train_model.py ${TARGET_PATH}/tmp/prepared_data_${CLASSIFICATION}.tsv.gz ${TARGET_PATH}/model/${CLASSIFICATION}.pkl ${TARGET_PATH}/model/${CLASSIFICATION}.results ${N_PROCESS} ${TRAIN_SPLIT}

cat ${TARGET_PATH}/model/${CLASSIFICATION}.results

