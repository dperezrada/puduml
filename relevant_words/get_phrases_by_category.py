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


import re

STOPWORDS = {
    "en": [
        "several", "on", "while", "than", "own", "you've", "itself", "above", "such", "over", "they're", "mainly", "because", "theirs", "too", "most", "must", "myself", "that", "why's", "it", "can't", "show", "overall", "she", "he'd", "it's", "can", "under", "no", "she'll", "should", "therefore", "his", "you", "various", "mustn't", "are", "doing", "really", "up", "they'd", "having", "these", "made", "we'll", "into", "you'll", "more", "ought", "especially", "hasn't", "seem", "nor", "shows", "here's", "here", "he's", "is", "at", "ml", "always", "nearly", "during", "ours", "this", "aren't", "rather", "being", "very", "shown", "them", "cannot", "just", "or", "where", "didn't", "another", "they'll", "shouldn't", "wasn't", "for", "when's", "in", "could", "off", "down", "further", "won't", "due", "however", "each", "i'd", "a", "that's", "where's", "enough", "neither", "its", "isn't", "any", "himself", "was", "they've", "etc", "there's", "whom", "both", "other", "by", "within", "not", "been", "below", "be", "once", "make", "does", "did", "before", "through", "shan't", "ourselves", "which", "kg", "their", "again", "thus", "about", "few", "either", "they", "do", "our", "you'd", "some", "don't", "although", "almost", "i'll", "often", "i'm", "she'd", "we'd", "yourselves", "using", "between", "if", "upon", "him", "we", "done", "as", "so", "hers", "me", "she's", "there", "and", "i've", "may", "but", "with", "how", "found", "her", "yours", "might", "then", "we've", "the", "yourself", "what's", "km", "without", "same", "those", "my", "perhaps", "all", "haven't", "of", "why", "has", "had", "regarding", "significantly", "when", "i", "until", "used", "would", "among", "what", "let's", "am", "how's", "who's", "weren't", "mm", "hadn't", "have", "mg", "wouldn't", "showed", "were", "an", "we're", "obtained", "themselves", "who", "your", "out", "to", "doesn't", "he", "herself", "pmid", "against", "use", "you're", "couldn't", "after", "he'll", "only", "also", "mostly", "quite", "seen", "since"
    ]
}

NUMBERS_STOPWORDS = {
    "en": [
        "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven", "twenty-eight", "twenty-nine", "thirty", "thirty-one", "thirty-two", "thirty-three", "thirty-four", "thirty-five", "thirty-six", "thirty-seven", "thirty-eight", "thirty-nine", "forty", "forty-one", "forty-two", "forty-three", "forty-four", "forty-five", "forty-six", "forty-seven", "forty-eight", "forty-nine", "fifty", "fifty-one", "fifty-two", "fifty-three", "fifty-four", "fifty-five", "fifty-six", "fifty-seven", "fifty-eight", "fifty-nine", "sixty", "sixty-one", "sixty-two", "sixty-three", "sixty-four", "sixty-five", "sixty-six", "sixty-seven", "sixty-eight", "sixty-nine", "seventy", "seventy-one", "seventy-two", "seventy-three", "seventy-four", "seventy-five", "seventy-six", "seventy-seven", "seventy-eight", "seventy-nine", "eighty", "eighty-one", "eighty-two", "eighty-three", "eighty-four", "eighty-five", "eighty-six", "eighty-seven", "eighty-eight", "eighty-nine", "ninety", "ninety-one", "ninety-two", "ninety-three", "ninety-four", "ninety-five", "ninety-six", "ninety-seven", "ninety-eight", "ninety-nine"
    ]
}
### Tokenize

def tokenize_one(text, stopwords=None, additional_stopwords=None, lang="en"):
    if stopwords is None:
        stopwords = STOPWORDS[lang] + NUMBERS_STOPWORDS[lang]
    if additional_stopwords:
        stopwords += additional_stopwords
    stopwords = [
        stopword
        for stopword in stopwords
        if stopword
    ]
    text_part = text.lower()

    # Must be executed in order
    regexs = [
        # Remove all stopwords by a !, we are searching for the stopword (bounded)
        ("\\b" + "\\b|\\b".join(stopwords), "!!"),
        ("’", "'"),
        # Remove all non alpha, numeric, spaces, - or single quote
        (r'([^a-z0-9\u00C0-\u1FFF\u2C00-\uD7FF \t\n\-\'])', "!!"),
        # remove only words numbers
        (r'(^|[ !])[0-9]+([ !]|$)', "!!"),
        # remove hyphen-minus for keywords starting or ending with it
        (r'((^|[ !])[\-\']+)|([\-\']+([ !]|$))', "!!"),
        # remove spaces between !
        (r' *! *', "!!"),
        # generate multiple ! need for next regex
        (r'!', "!!"),
        # remove one character keyword
        (r'(^|!)[^!\n](!|$)', "!!"),
        # remove multiple ! (!!!!)
        (r'!+', "!"),
        # remove first and last !
        (r'(^!+)|(!+$)', ""),
    ]
    for regex, replacement in regexs:
        text_part = re.sub(regex, replacement, text_part, flags=re.M)
    return text_part.split("!")



def get_stopword_tokenizer(title, text, min_ngram, max_ngram):
    list_of_words = tokenize_one(title)
    list_of_words += tokenize_one(text)
    # all_phrases = []
    # for ngram in range(min_ngram, max_ngram + 1):
    #     all_phrases += get_ngram(list_of_words, ngram)
    return list(set(list_of_words))


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
                for ngram in get_stopword_tokenizer(title, paragraphs, min_ngram, max_ngram)
                #for ngram in get_ngrams(title, paragraphs, min_ngram, max_ngram)
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
