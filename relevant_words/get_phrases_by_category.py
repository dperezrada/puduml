# coding: utf-8
from __future__ import print_function
import gzip
import re
import sys
from bs4 import BeautifulSoup


PROCESS_STEP = 500
MIN_NGRAM = 1
MAX_NGRAM = 3

STOPWORDS = [
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
    "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its",
    "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom",
    "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but",
    "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about",
    "against", "between", "into", "through", "during", "before", "after", "above", "below", "to",
    "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
]


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
        if word.strip() and word not in STOPWORDS and not is_number(word)
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


def clean_text(text):
    try:
        soup = BeautifulSoup("<br/>" + text, "html.parser")
        second_clean = soup.get_text().replace("\t", " ").replace("\n", " ").replace(
            "\"", "").replace("'", "").replace("\r", "")
        return (" ".join([
            word for word in re.findall(r"(?u)\b\w\w+\b", second_clean)
            if not re.match(r"[0-9]+$", word.strip())
        ][0:200]))
    except:
        return None


def main():
    filepath = sys.argv[1]
    index = 0
    if filepath.find(".gz") > 0:
        file_ = gzip.open(filepath, 'rt', encoding='utf-8')
    else:
        file_ = open(filepath)
    for line in file_:
        if index % PROCESS_STEP == 0:
            print(index, file=sys.stderr)
        try:
            token, tag, title, raw_paragraphs = line.rstrip("\r\n").split("\t")
            title = clean_text(title)
            paragraphs = clean_text(raw_paragraphs)
            new_row = [
                tag + "\t" + ngram
                for ngram in get_ngrams(title, paragraphs, MIN_NGRAM, MAX_NGRAM)
            ]
            print("\n".join(new_row))
        except BrokenPipeError as exception:
            raise exception
        except:
            print("Error: %s" % line, file=sys.stderr)
        index += 1
    file_.close()


if __name__ == '__main__':
    main()
