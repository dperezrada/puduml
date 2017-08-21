# coding: utf-8
from __future__ import print_function
import gzip
import re
import sys
from bs4 import BeautifulSoup

from puduml_utils import EN_STOPWORDS, print_progress_bar, count_lines_from_file


PROGRESS_STEP = 1000


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


def clean_text(text, parseHTML=False):
    try:
        if parseHTML:
            soup = BeautifulSoup("<br/>" + text, "html.parser")
            parsed_text = soup.get_text()
        else:
            parsed_text = text
        second_clean = parsed_text.replace("\t", " ").replace("\n", " ").replace(
            "\"", "").replace("'", "").replace("\r", "")
        return (" ".join([
            word for word in re.findall(r"(?u)\b\w[\w-]+\b", second_clean)
            if not re.match(r"[0-9]+$", word.strip())
        ][0:200]))
    except:
        return None


def main():
    filepath = sys.argv[1]
    if len(sys.argv) > 2:
        min_ngram = sys.argv[2]
    else:
        min_ngram = 1
    if len(sys.argv) > 3:
        max_ngram = sys.argv[3]
    else:
        max_ngram = 3
    index = 0
    if filepath.find(".gz") > 0:
        file_ = gzip.open(filepath, 'rt', encoding='utf-8')
    else:
        file_ = open(filepath)
    total_lines = count_lines_from_file(filepath)
    total_errors = 0
    for line in file_:
        print_progress_bar(index, total_lines, prefix='Progress:', suffix='Complete', length=50)
        try:
            token, tag, title, raw_paragraphs = line.rstrip("\r\n").split("\t")
            title = clean_text(title)
            paragraphs = clean_text(raw_paragraphs, True)
            new_row = [
                token + "\t" + tag + "\t" + ngram
                for ngram in get_ngrams(title, paragraphs, min_ngram, max_ngram)
            ]
            print("\n".join(new_row))
        except BrokenPipeError as exception:
            raise exception
        except:
            total_errors += 1
        index += 1
    print("%s lines were omited" % total_errors, file=sys.stderr)

    file_.close()


if __name__ == '__main__':
    main()
