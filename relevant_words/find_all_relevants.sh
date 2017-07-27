#!/bin/bash

PYTHON_PATH="${PYTHON_PATH:-python}"

INPUT_FILE=$1
OUTPUT_PATH=$2
FILTER_TOP_X=2000
SELECT_TOP_Y=500
N_PROCESS=3

mkdir -p ${OUTPUT_PATH}/base
# Generate all possible phrases associated with the category
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$PYTHON_PATH ${SCRIPT_DIR}/get_phrases_by_category.py $INPUT_FILE > ${OUTPUT_PATH}/base/all_words_with_category.tsv


# Calculate 
cat ${OUTPUT_PATH}/base/all_words_with_category.tsv | cut -d$'\t' -f2 | \
	${SCRIPT_DIR}/../utils/csort | \
	sort -t$'\t' -k1,1nr | awk -F$'\t' 'BEGIN{OFS="\t"}{print $1,$2}'> ${OUTPUT_PATH}/base/all_words_with_count.tsv

mkdir -p ${OUTPUT_PATH}/classifications/

CLASSIFICATIONS=$(cut -d$'\t' -f1 ${OUTPUT_PATH}/base/all_words_with_category.tsv|awk '!seen[$1]++')
for classification in $CLASSIFICATIONS; do
	
	echo "Processing classification: ${classification}"

	cat ${OUTPUT_PATH}/base/all_words_with_category.tsv	|
		grep "^${classification}	" |
		cut -d$'\t' -f2 |																# Extract only phrase
		${SCRIPT_DIR}/../utils/csort |													# Count number of phrases
		{
			# Sort by frequency
			sort --parallel=${N_PROCESS} -t$'\t' -k1,1nr > ${OUTPUT_PATH}/classifications/${classification}_positive.tsv
		}

	${SCRIPT_DIR}/../utils/sjoin -t$'\t' -1 2 -2 2 -a1 -o '1.2,1.1,2.1' ${OUTPUT_PATH}/classifications/${classification}_positive.tsv ${OUTPUT_PATH}/base/all_words_with_count.tsv |
		awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3,($2/$3)}' |			# calculate total in group/total documents
		sort -t$'\t' -k2,2nr |											# sort by group frequency
		head -n ${FILTER_TOP_X} |										# get only the first X more frequent phrases
		sort -t$'\t' -k4,4nr |											# sort by division over total
		head -n${SELECT_TOP_Y} |										# select top Y
		sort -t$'\t' -k2,2nr > ${OUTPUT_PATH}/classifications/${classification}_positive_with_all.tsv

	rm ${OUTPUT_PATH}/classifications/${classification}_positive.tsv
	mv ${OUTPUT_PATH}/classifications/${classification}_positive_with_all.tsv ${OUTPUT_PATH}/classifications/${classification}_positive.tsv

	cat ${OUTPUT_PATH}/base/all_words_with_category.tsv| grep -v "^${classification}	" | cut -d$'\t' -f2 | \
		awk 'BEGIN{OFS="\t"}{seen[$0]++}END{for(key in seen){print seen[key],key}}' | \
		sort -t$'\t' -k1,1nr | \
		awk -F$'\t' 'BEGIN{OFS="\t"}{print $1,$2}' > ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
	${SCRIPT_DIR}/../utils/sjoin -t$'\t' -1 2 -2 2 -a1 -o '1.2,1.1,2.1' \
		${OUTPUT_PATH}/classifications/${classification}_negative.tsv ${OUTPUT_PATH}/base/all_words_with_count.tsv | \
		awk -F$'\t' 'BEGIN{OFS=FS}{print $1,$2,$3,($2/$3)}' | \
		sort -t$'\t' -k2,2nr | head -n ${FILTER_TOP_X} | sort -t$'\t' -k4,4nr | head -n${SELECT_TOP_Y} | \
		sort -t$'\t' -k2,2nr> ${OUTPUT_PATH}/classifications/${classification}_negative_with_all.tsv

	rm ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
	mv ${OUTPUT_PATH}/classifications/${classification}_negative_with_all.tsv ${OUTPUT_PATH}/classifications/${classification}_negative.tsv
done