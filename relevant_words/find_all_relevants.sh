#!/bin/bash

PYTHON_PATH="${PYTHON_PATH:-python}"

INPUT_FILE=$1
OUTPUT_PATH=$2
ONE_CLASSIFICATION=$3
SELECT_TOP_Y=$4
N_PROCESS=$5

if [[ -z "$SELECT_TOP_Y" ]]; then
	SELECT_TOP_Y=500
fi
if [[ -z "$N_PROCESS" ]]; then
	N_PROCESS=3
fi
FILTER_TOP_X=$(( ${SELECT_TOP_Y} * 4 ))

mkdir -p ${OUTPUT_PATH}/base
# Generate all possible phrases associated with the category
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Find phrases by category"
$PYTHON_PATH ${SCRIPT_DIR}/get_phrases_by_category.py $INPUT_FILE > ${OUTPUT_PATH}/base/all_words_with_category.tsv


echo "Count all words"
# Calculate 
cut -d$'\t' -f2 ${OUTPUT_PATH}/base/all_words_with_category.tsv | \
	${SCRIPT_DIR}/../utils/unix/csort | \
	awk -F$'\t' 'BEGIN{OFS="\t"}{print $1,$2}'> ${OUTPUT_PATH}/base/all_words_with_count.tsv

mkdir -p ${OUTPUT_PATH}/classifications/

CLASSIFICATIONS=$(cut -d$'\t' -f1 ${OUTPUT_PATH}/base/all_words_with_category.tsv|awk '!seen[$1]++')
for classification in $CLASSIFICATIONS; do
	if [ ! -z "$ONE_CLASSIFICATION" ]; then
		if [[ "$ONE_CLASSIFICATION" != "$classification" ]]; then
			continue
		fi
	fi
	echo "Processing classification: ${classification}"

	cat ${OUTPUT_PATH}/base/all_words_with_category.tsv	|
		grep "^${classification}	" |
		cut -d$'\t' -f2 |																# Extract only phrase
		{
			# Count number of phrases
			${SCRIPT_DIR}/../utils/unix/csort > ${OUTPUT_PATH}/classifications/${classification}_positive.tsv
		}

	${SCRIPT_DIR}/../utils/unix/sjoin -t$'\t' -1 2 -2 2 -a1 -o '1.2,1.1,2.1' ${OUTPUT_PATH}/classifications/${classification}_positive.tsv ${OUTPUT_PATH}/base/all_words_with_count.tsv |
		awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3,($2/$3)}' |			# calculate total in group/total documents
		LANG=en_EN sort -t$'\t' -k2,2nr |											# sort by group frequency
		head -n ${FILTER_TOP_X} |										# get only the first X more frequent phrases
		LANG=en_EN sort -t$'\t' -k4,4nr |											# sort by division over total
		head -n${SELECT_TOP_Y} |										# select top Y
		LANG=en_EN sort -t$'\t' -k2,2nr > ${OUTPUT_PATH}/classifications/${classification}_positive_with_all.tsv

	rm ${OUTPUT_PATH}/classifications/${classification}_positive.tsv
	mv ${OUTPUT_PATH}/classifications/${classification}_positive_with_all.tsv ${OUTPUT_PATH}/classifications/${classification}_positive.tsv

	cat ${OUTPUT_PATH}/base/all_words_with_category.tsv| grep -v "^${classification}	" | cut -d$'\t' -f2 | \
		awk 'BEGIN{OFS="\t"}{seen[$0]++}END{for(key in seen){print seen[key],key}}' | \
		LANG=en_EN sort -t$'\t' -k1,1nr | \
		awk -F$'\t' 'BEGIN{OFS="\t"}{print $1,$2}' > ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
	${SCRIPT_DIR}/../utils/unix/sjoin -t$'\t' -1 2 -2 2 -a1 -o '1.2,1.1,2.1' \
		${OUTPUT_PATH}/classifications/${classification}_negative.tsv ${OUTPUT_PATH}/base/all_words_with_count.tsv | \
		awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3,($2/$3)}' | \
		LANG=en_EN sort -t$'\t' -k2,2nr | head -n ${FILTER_TOP_X} | LANG=en_EN sort -t$'\t' -k4,4nr | head -n${SELECT_TOP_Y} | \
		LANG=en_EN sort -t$'\t' -k2,2nr> ${OUTPUT_PATH}/classifications/${classification}_negative_with_all.tsv

	rm ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
	mv ${OUTPUT_PATH}/classifications/${classification}_negative_with_all.tsv ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
done