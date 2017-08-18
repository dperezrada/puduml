#!/bin/bash

INPUT_FILE=$1
OUTPUT_PATH=$2
ONE_CLASSIFICATION=$3
SELECT_TOP_Y=$4
N_PROCESS=$5
MIN_APPEAR="$6"

if [[ -z "$SELECT_TOP_Y" ]]; then
	SELECT_TOP_Y=500
fi
if [[ -z "$MIN_APPEAR" ]]; then
	MIN_APPEAR="5"
fi
if [[ -z "$N_PROCESS" ]]; then
	N_PROCESS=3
fi
FILTER_TOP_X=$(( ${SELECT_TOP_Y} * 4 ))

BASE_PATH=${OUTPUT_PATH}/base
mkdir -p ${BASE_PATH}
# Generate all possible phrases associated with the category
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ ! -f "${BASE_PATH}/all_words_with_category.tsv" ]; then
	echo "Find phrases by category"
	python ${SCRIPT_DIR}/get_phrases_by_category.py $INPUT_FILE > ${BASE_PATH}/all_words_with_category.tsv
fi

if [ ! -f "${BASE_PATH}/all_words_with_count.tsv" ]; then
	echo "Count all words"
	# Calculate 
	cut -d$'\t' -f1,3 ${OUTPUT_PATH}/base/all_words_with_category.tsv | \
		awk '!seen[$0]++' |
		cut -d$'\t' -f2 |
		${SCRIPT_DIR}/../utils/unix/csort | \
		awk -F$'\t' 'BEGIN{OFS="\t"}{print 1,$2}'> ${OUTPUT_PATH}/base/all_words_with_count.tsv
fi

mkdir -p ${OUTPUT_PATH}/classifications/
if [ ! -f "${BASE_PATH}/categories.tsv" ]; then
	cut -d$'\t' -f2 ${OUTPUT_PATH}/base/all_words_with_category.tsv|awk '!seen[$1]++' > ${BASE_PATH}/categories.tsv
fi
CLASSIFICATIONS=$(cut -d$'\t' -f1 ${OUTPUT_PATH}/base/categories.tsv)
for classification in $CLASSIFICATIONS; do
	if [ ! -z "$ONE_CLASSIFICATION" ]; then
		if [[ "$ONE_CLASSIFICATION" != "$classification" ]]; then
			continue
		fi
	fi
	TARGET_PATH=${OUTPUT_PATH}/classifications/${classification}.tsv
	if [ -f $TARGET_PATH  ]; then
		continue
	fi
	echo "Processing classification: ${classification}"

	cat ${OUTPUT_PATH}/base/all_words_with_category.tsv	|
		grep "	${classification}	" |
		grep -v " " |
		cut -d$'\t' -f3 |																# Extract only phrase
		{
			# Count number of phrases
			${SCRIPT_DIR}/../utils/unix/csort > ${OUTPUT_PATH}/classifications/${classification}_numeric_1.tsv
		}

	cat ${OUTPUT_PATH}/base/all_words_with_category.tsv	|
		grep "	${classification}	" |
		grep " " |
		cut -d$'\t' -f3 |																# Extract only phrase
		{
			# Count number of phrases
			${SCRIPT_DIR}/../utils/unix/csort > ${OUTPUT_PATH}/classifications/${classification}_numeric_2.tsv
		}

	# TODO: Refactor this
	${SCRIPT_DIR}/../utils/unix/sjoin -t$'\t' -1 2 -2 2 -a1 -o '1.2,1.1,2.1' ${OUTPUT_PATH}/classifications/${classification}_numeric_1.tsv ${OUTPUT_PATH}/base/all_words_with_count.tsv |
	awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3,($2/$3)}' |			# calculate total in group/total documents
	awk -F$'\t' -v MIN_APPEAR="${MIN_APPEAR}" '{if($2>=MIN_APPEAR)print $0}' |
	LANG=en_EN sort -t$'\t' -k2,2nr |											# sort by group frequency
	awk -F$'\t' 'BEGIN{OFS=FS}{print $0,FNR}'|
	head -n ${FILTER_TOP_X} |										# get only the first X more frequent phrases
	LANG=en_EN sort -t$'\t' -k4,4nr |											# sort by division over total
	awk -F$'\t' 'BEGIN{OFS=FS}{print $0,FNR,($5*0.7+FNR*0.3)}'|
	LANG=en_EN sort -t$'\t' -k7,7n |										# select top Y
	head -n${SELECT_TOP_Y} > ${OUTPUT_PATH}/classifications/${classification}_final_1.tsv

	${SCRIPT_DIR}/../utils/unix/sjoin -t$'\t' -1 2 -2 2 -a1 -o '1.2,1.1,2.1' ${OUTPUT_PATH}/classifications/${classification}_numeric_2.tsv ${OUTPUT_PATH}/base/all_words_with_count.tsv |
	awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3,($2/$3)}' |			# calculate total in group/total documents
	awk -F$'\t' -v MIN_APPEAR="${MIN_APPEAR}" '{if($2>=MIN_APPEAR)print $0}' |
	LANG=en_EN sort -t$'\t' -k2,2nr |											# sort by group frequency
	awk -F$'\t' 'BEGIN{OFS=FS}{print $0,FNR}'|
	head -n ${FILTER_TOP_X} |										# get only the first X more frequent phrases
	LANG=en_EN sort -t$'\t' -k4,4nr |											# sort by division over total
	awk -F$'\t' 'BEGIN{OFS=FS}{print $0,FNR,(($5*0.7+FNR*0.3)*2.5)}'|
	LANG=en_EN sort -t$'\t' -k7,7n |										# select top Y
	head -n${SELECT_TOP_Y} > ${OUTPUT_PATH}/classifications/${classification}_final_2.tsv

	cat ${OUTPUT_PATH}/classifications/${classification}_final* |
	LANG=en_EN sort -t$'\t' -k7,7n |										# select top Y
	awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3}' > ${OUTPUT_PATH}/classifications/${classification}.tsv
	rm ${OUTPUT_PATH}/classifications/${classification}_final_*.tsv
	rm ${OUTPUT_PATH}/classifications/${classification}_numeric*.tsv


	# cat ${OUTPUT_PATH}/base/all_words_with_category.tsv| grep -v "^${classification}	" | cut -d$'\t' -f2 | \
	# 	awk 'BEGIN{OFS="\t"}{seen[$0]++}END{for(key in seen){print seen[key],key}}' | \
	# 	LANG=en_EN sort -t$'\t' -k1,1nr | \
	# 	awk -F$'\t' 'BEGIN{OFS="\t"}{print $1,$2}' > ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
	# ${SCRIPT_DIR}/../utils/unix/sjoin -t$'\t' -1 2 -2 2 -a1 -o '1.2,1.1,2.1' \
	# 	${OUTPUT_PATH}/classifications/${classification}_negative.tsv ${OUTPUT_PATH}/base/all_words_with_count.tsv | \
	# 	awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3,($2/$3)}' | \
	# 	LANG=en_EN sort -t$'\t' -k2,2nr | head -n ${FILTER_TOP_X} | LANG=en_EN sort -t$'\t' -k4,4nr | head -n${SELECT_TOP_Y} | \
	# 	LANG=en_EN sort -t$'\t' -k2,2nr> ${OUTPUT_PATH}/classifications/${classification}_negative_with_all.tsv

	# rm ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
	# mv ${OUTPUT_PATH}/classifications/${classification}_negative_with_all.tsv ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
done