import re
import sys
import os
import gzip
from multiprocessing import Pool

from puduml_utils import print_progress_bar, EN_STOPWORDS


PROGRESS_STEP = 5000


def is_number(possible_number):
    try:
        float(possible_number)
        return True
    except ValueError:
        return False


def get_words_from_text(text):
    return [
        word
        for word in re.sub(r"[^\w\-']", " ", text.lower().strip()).split(" ")
        if word.strip() and word not in EN_STOPWORDS and not is_number(word)
    ]


def get_ngram(list_of_words, ngram):
    return [
        " ".join(list_of_words[i:i + ngram])
        for i in iter(range(len(list_of_words) - ngram + 1))
    ]


def get_ngrams(title, text, min_ngram, max_ngram):
    list_of_words = get_words_from_text(title)
    list_of_words += get_words_from_text(text)
    all_phrases = []
    for ngram in range(min_ngram, max_ngram + 1):
        all_phrases += get_ngram(list_of_words, ngram)
    return list(set(all_phrases))


def get_previous_words(target_word, text):
    words = get_words_from_text(text)
    words_index = [
        index - 1
        for index, current_word in enumerate(words)
        if current_word == target_word and index > 0
    ]
    return [words[word_index] for word_index in words_index]


def process_file_base(features_filepath, data_filepath, total_lines, output_filepath, start=None, end=None, progress_bar=True):
    if start is None:
        start = 0
    if end is None:
        end = total_lines
    features = [feature.rstrip("\r\n") for feature in open(features_filepath, 'rt', encoding='utf-8').readlines()]
    with gzip.open(output_filepath, "wt", encoding="utf-8") as file_:
        if data_filepath.find(".gz") > 0:
            data_file = gzip.open(data_filepath, 'rt', encoding='utf-8')
        else:
            data_file = open(data_filepath, 'rt', encoding='utf-8')
        for line_number, line in enumerate(data_file):
            if not (line_number >= start and line_number < end):
                continue
            try:
                splitted_row = line.rstrip("\r\n").split("\t")
                doc_id = splitted_row[0]
                result = splitted_row[1]
                title = splitted_row[2]
                text = " ".join(splitted_row[3:])
            except:
                import ipdb;ipdb.set_trace()
                print("ERROR line number: %s" % line_number, file=sys.stderr)
                continue
            found_features = []
            row_features = get_ngrams(title, text, 1, 3)
            for feature in features:
                value = "0"
                if feature in row_features:
                    value = "1"
                found_features.append(value)
            file_.write("%s,%s,%s\n" % (doc_id, ",".join(found_features), result))
            if progress_bar:
                print_progress_bar(line_number, total_lines, prefix='Progress:', suffix='Complete', length=50)
            else:
                if line_number % PROGRESS_STEP == 0:
                    print("batch %s ok" % line_number, file=sys.stderr)

def process_file(features_filepath, data_filepath, output_filepath):
    if data_filepath.find(".gz") > 0:
        total_lines = sum(1 for line in gzip.open(data_filepath, 'rt', encoding='utf-8'))
    else:
        total_lines = sum(1 for line in open(data_filepath, 'rt', encoding='utf-8'))
    process_file_base(features_filepath, data_filepath, total_lines, output_filepath)

def multiple_proccessors(features_filepath, data_filepath, output_filepath, n_proc=3):
    if data_filepath.find(".gz") > 0:
        total_lines = sum(1 for line in gzip.open(data_filepath, 'rt', encoding='utf-8'))
    else:
        total_lines = sum(1 for line in open(data_filepath, 'rt', encoding='utf-8'))
    step = int(total_lines/n_proc)
    ranges = [(index * step, (index + 1) * step) for index in range(0, n_proc)]
    args_pool = [
        (
            features_filepath,
            data_filepath,
            step,
            output_filepath + ".%s.tmp" % range_el[0],
            range_el[0],
            range_el[1],
            False

        )
        for range_el in ranges
    ]
    with Pool(n_proc) as pool:
        pool.starmap(process_file_base, args_pool)

    features = [feature.rstrip("\r\n") for feature in open(features_filepath, 'rt', encoding='utf-8').readlines()]
    with gzip.open(output_filepath, "wt", encoding="utf-8") as file_:
        file_.write("id,%s,puduml___result\n" % ",".join(features))
        for args_row in args_pool:
            with gzip.open(args_row[3], 'rt', encoding='utf-8') as pool_file:
                for line in pool_file:
                    file_.write(line)
            os.remove(args_row[3])


if __name__ == '__main__':
    data_filepath = sys.argv[1]
    features_filepath = sys.argv[2]
    output_filepath = sys.argv[3]
    n_process = None
    if len(sys.argv) > 4:
        try:
            n_process = int(sys.argv[4])
        except:
            pass
    if n_process:
        multiple_proccessors(features_filepath, data_filepath, output_filepath, int(n_process))
    else:
        process_file(features_filepath, data_filepath, output_filepath)


