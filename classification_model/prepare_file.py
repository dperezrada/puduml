import re
import sys
import gzip


PROGRESS_STEP = 500

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

def progress(index):
    if index % PROGRESS_STEP == 0:
        print(index, file=sys.stderr)


def process_file(features_filepath, data_filepath, output_filepath):
    features = [feature.rstrip("\r\n") for feature in open(features_filepath, 'rt', encoding='utf-8').readlines()]
    index = 0
    with gzip.open(output_filepath, "wt", encoding="utf-8") as file_:
        file_.write("id,%s,puduml___result\n" % ",".join(features))
        if data_filepath.find(".gz") > 0:
            data_file = gzip.open(data_filepath, 'rt', encoding='utf-8')
        else:
            data_file = open(data_filepath, 'rt', encoding='utf-8')
        for line in data_file:
            try:
                doc_id, result, title, text = line.rstrip("\r\n").split("\t")
            except:
                continue
            found_features = []
            row_features = get_ngrams(title, text, 1, 3)
            for feature in features:
                value = "0"
                if feature in row_features:
                    value = "1"
                found_features.append(value)
            file_.write("%s,%s,%s\n" % (doc_id, ",".join(found_features), result))
            progress(index)
            index += 1

if __name__ == '__main__':
    data_filepath = sys.argv[1]
    features_filepath = sys.argv[2]
    output_filepath = sys.argv[3]
    process_file(features_filepath, data_filepath, output_filepath)
