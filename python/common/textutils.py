#!python
from . import utils, log
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

# download tokenizer
for dataset in ['punkt']:
    try:
        nltk.data.find('tokenizers/{}'.format(dataset))
    except LookupError:
        nltk.download(dataset)

# download corpora
for dataset in ['wordnet', 'stopwords', 'brown']:
    try:
        nltk.data.find('corpora/{}'.format(dataset))
    except LookupError:
        nltk.download(dataset)

lemmatizer = WordNetLemmatizer()
common = set()
lemmatized_common = set()

@utils.run_once
def __load_common_words():
    log.info('loading common words')
    fd = nltk.FreqDist(nltk.corpus.brown.words())
    global common
    global lemmatized_common
    common.update(set([w.lower() for w,c in fd.most_common()[:1000]]))
    common.update(set([w.lower() for w in nltk.corpus.stopwords.words('english')]))
    common.update(list(string.ascii_lowercase))

    lemmatized_common.update([lemmatizer.lemmatize(w) for w in common])
    return True

def tokenize(text):
    return word_tokenize(text)

# extract the core part of a text
# remove common/stop words punctuations
# return array of uncommon words
def extract_core_words(text, lemmatize=True):
    __load_common_words()
    text = text.lower()
    imp_words = []
    if lemmatize:
        words = set([lemmatizer.lemmatize(w.lower()) for w in word_tokenize(text)])
        # remove common words and punctuation
        imp_words = [w for w in words if w not in lemmatized_common and w[0] not in string.punctuation]
    else:
        words = set([w.lower() for w in word_tokenize(text)])
        # remove common words and punctuation
        imp_words = [w for w in words if w not in common and w[0] not in string.punctuation]

    return imp_words

# maintains a sorted comma separated, unique str list
def add_to_stringlist(strlist, value, add_space=False):
    strlist = '' if strlist is None else strlist
    str_set = set(map(str.strip, strlist.split(',')))
    str_set.update(map(str.strip, value.split(',')))
    str_set.discard('')
    glue = ', ' if add_space else ','
    return glue.join(sorted(list(str_set)))

# maintains a sorted comma separated, unique str list
def remove_from_stringlist(strlist, value, add_space=False):
    strlist = '' if strlist is None else strlist
    str_set = set(map(str.strip, strlist.split(',')))
    for item in map(str.strip, value.split(',')):
        str_set.discard(item)
    str_set.discard('')
    glue = ', ' if add_space else ','
    return glue.join(sorted(list(str_set)))