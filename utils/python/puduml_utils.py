import gzip
import sys


EN_STOPWORDS = [
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

# Print iterations progress from https://stackoverflow.com/a/34325723/859731
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar_str = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar_str, percent, suffix), end='\r', file=sys.stderr)
    # Print New Line on Complete
    if iteration == total:
        print(file=sys.stderr)

def count_lines_from_file(filepath):
    if filepath.find(".gz") > 0:
        total_lines = sum(1 for line in gzip.open(filepath, 'rt', encoding='utf-8'))
    else:
        total_lines = sum(1 for line in open(filepath, 'rt', encoding='utf-8'))
    return total_lines