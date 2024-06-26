import itertools
import re
from collections import Counter, defaultdict
from typing import Dict, List, NamedTuple

import numpy as np
from numpy.linalg import norm
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from math import log2
from webCrawl import run
# import nltk
# nltk.download('punkt')


num_docs = 0
crawled_data_file = 'extracted.txt'


# the document representing each crawled page
class Document(NamedTuple):
    doc_id: int
    url: str
    title: List[str]
    author: List[str]
    # the body text
    body: List[str]

    def sections(self):
        return [self.url, self.title, self.author, self.body]

    def __repr__(self):
        return (f"doc_id: {self.doc_id}\n" +
            f"  url: {self.url}\n" +
            f"  title: {self.title}\n" +
            f"  author: {self.author}\n" +
            f"  body: {self.body}")


def read_stopwords(file):
    with open(file) as f:
        return set([x.strip() for x in f.readlines()])


stopwords = read_stopwords('common_words')
stemmer = SnowballStemmer('english')


def read_docs(file):
    '''
    Reads the crawled data into a list of Documents
    '''
    docs = []

    i = 0
    doc_id = 1
    with open(file) as f:
        url = ""
        title = []
        author = []
        for line in f:
            line = line.strip()
            if i % 4 == 0: url = line
            else:
                tokens = []
                for word in word_tokenize(line):
                    tokens.append(word)
                if i % 4 == 1: title = tokens
                if i % 4 == 2: author = tokens
                elif i % 4 == 3:
                    docs.append(Document(doc_id, url, title, author, tokens))
                    doc_id += 1
            i += 1

    return docs


def read_docs_intact(file):
    '''
    Reads the crawled data into a list of _untokenized_ Documents
    to facilitate displaying back to the user
    '''
    docs = []

    i = 0
    doc_id = 1
    with open(file) as f:
        url = ""
        title = ""
        author = ""
        for line in f:
            line = line.strip()
            if i % 4 == 0: url = line
            else:
                if i % 4 == 1: title = line
                if i % 4 == 2: author = line
                elif i % 4 == 3:
                    docs.append(Document(doc_id, url, title, author, line))
                    doc_id += 1
            i += 1

    return docs


def stem_doc(doc: Document):
    return Document(doc.doc_id, *[[stemmer.stem(word) for word in sec]
        for sec in doc.sections()])


def stem_docs(docs: List[Document]):
    return [stem_doc(doc) for doc in docs]


def remove_stopwords_doc(doc: Document):
    return Document(doc.doc_id, *[[word for word in sec if word not in stopwords]
        for sec in doc.sections()])


def remove_stopwords(docs: List[Document]):
    return [remove_stopwords_doc(doc) for doc in docs]


# relative weights of the three fields of a page
class TermWeights(NamedTuple):
    title: float
    author: float
    body: float


def compute_doc_freqs(docs: List[Document]):
    '''
    Computes document frequency, i.e. how many documents contain a specific word
    '''
    freq = Counter()
    for doc in docs:
        words = set()
        for sec in doc.sections():
            for word in sec:
                words.add(word)
        for word in words:
            freq[word] += 1
    return freq


# TF weighting
def compute_tf(doc: Document, doc_freqs: Dict[str, int], weights: list):
    vec = defaultdict(float)
    for word in doc.title:
        vec[word] += weights.title
    for word in doc.author:
        vec[word] += weights.author
    for word in doc.body:
        vec[word] += weights.body
    return dict(vec)


# TF weighting - based on TF
def compute_tfidf(doc, doc_freqs, weights):
    tf = compute_tf(doc, doc_freqs, weights)
    for word in tf:
        docs_with_word = doc_freqs[word]
        if docs_with_word == 0:
            tf[word] = 0
        else:
            tf[word] *= log2(num_docs / docs_with_word)
    return tf


# Simple boolean weighting
def compute_boolean(doc, doc_freqs, weights):
    vec = defaultdict(float)
    for word in doc.title:
        vec[word] = 1.0
    for word in doc.author:
        vec[word] = 1.0
    for word in doc.body:
        vec[word] = 1.0
    return dict(vec)


def dictdot(x: Dict[str, float], y: Dict[str, float]):
    '''
    Computes the dot product of vectors x and y, represented as sparse dictionaries.
    '''
    keys = list(x.keys()) if len(x) < len(y) else list(y.keys())
    return sum(x.get(key, 0) * y.get(key, 0) for key in keys)


def cosine_sim(x, y):
    '''
    Computes the cosine similarity between two sparse term vectors represented as dictionaries.
    '''
    num = dictdot(x, y)
    if num == 0:
        return 0
    return num / (norm(list(x.values())) * norm(list(y.values())))


# dice similarity
def dice_sim(x, y):
    num = dictdot(x, y)
    if num == 0:
        return 0
    return (2 * num) / (sum(x.values()) + sum(y.values()))


# jaccard similarity
def jaccard_sim(x, y):
    num = dictdot(x, y)
    if num == 0:
        return 0
    return num / (sum(x.values()) + sum(y.values()) - num + 0.000001)


# overlap similarity
def overlap_sim(x, y):
    num = dictdot(x, y)
    if num == 0:
        return 0
    return num / min(sum(x.values()), sum(y.values()))


def interpolate(x1, y1, x2, y2, x):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m * x + b


def precision_at(rec: float, results: List[int], relevant: List[int]) -> float:
    '''
    This function computes the precision at the specified recall level.
    If the recall level is in between two points, you should do a linear interpolation
    between the two closest points. For example, if you have 4 results
    (recall 0.25, 0.5, 0.75, and 1.0), and you need to compute recall @ 0.6, then do something like

    interpolate(0.5, prec @ 0.5, 0.75, prec @ 0.75, 0.6)

    Note that there is implicitly a point (recall=0, precision=1).

    `results` is a sorted list of document ids
    `relevant` is a list of relevant documents
    '''

    rels, ress = 0, 0
    # Recall
    recs = [0]
    # Precision
    precs = [1]

    for d in results:
        ress += 1
        if d in relevant:
            rels += 1
            precs.append(rels / ress)
            recs.append(rels / len(relevant))

    if rec in recs: return precs[recs.index(rec)]
    else:
        rec_up = max([i for i in recs if rec > i])
        idx_up = recs.index(rec_up)
        prec_up = precs[idx_up]
        rec_low = min([i for i in recs if rec < i])
        idx_low = recs.index(rec_low)
        prec_low = precs[idx_low]
        return interpolate(rec_low, prec_low, rec_up, prec_up, rec)
        

def mean_precision1(results, relevant):
    return (precision_at(0.25, results, relevant) +
        precision_at(0.5, results, relevant) +
        precision_at(0.75, results, relevant)) / 3


def mean_precision2(results, relevant):
    return sum([precision_at(i / 10, results, relevant) for i in range(1, 11)]) / 10


def norm_recall(results, relevant):
    rel_len = len(relevant)

    return 1 - ((sum(1 + results.index(relevant[i]) for i in range(rel_len)) - sum(1 + i for i in range(rel_len))) / (rel_len * (len(results) - rel_len)))


def norm_precision(res, rel):
    top = sum(np.log(1 + res.index(rel[i])) for i in range(len(rel))) - sum(np.log(1 + i) for i in range(len(rel)))
    bot = (len(res) * np.log(len(res))) - ((len(res) - len(rel)) * np.log(len(res) - len (rel))) - ((len(rel)) * np.log(len(rel)))

    return 1 - top / bot


# retrieve page based on its ID (index in a batch)
def get_doc(id):
    doc = read_docs_intact(crawled_data_file)[id]
    return [{"id": doc.doc_id,
             "title": doc.title,
             "author": doc.author,
             "body": doc.body}]

# Search relevant web pages
def search(docs, doc_vectors, query_vec, sim, count):
    results_with_score = [(doc_id + 1, sim(query_vec, doc_vec))
                    for doc_id, doc_vec in enumerate(doc_vectors)]
    count = len(results_with_score) if count == -1 else count
    results_with_score = (sorted(results_with_score, key=lambda x: -x[1]))[:count]
    docs = [docs[x[0] - 1] for x in results_with_score]

    return [{"id": doc.doc_id,
             "url": doc.url,
             "title": doc.title,
             "author": doc.author,
             "body": doc.body}
            for doc in docs]


# process user query (along with many tunable options) and search for most relevant web pages
def process_query(T = "", W="news-letter", A="", stem = True, removestop = True, weighting = "tfidf", similarity = "cosine", weights = "114", count = 5, domain = "hub.jhu.edu", latest = False, numPages = 100):
    title = []
    # tokenize title
    for word in word_tokenize(T):
        title.append(word.lower())

    body = []
    # tokenize body text
    for word in word_tokenize(W):
        body.append(word.lower())

    author = []
    # tokenize author
    for word in word_tokenize(A):
        author.append(word.lower())

    # create query document
    query = Document(0, "", title, author, body)

    # if we require the latest data, then first crawl the URLs discovered under the starting `domain` on the fly
    if latest:
        run(domain, max_pages=numPages)

    # the (newly) generated file of crawled pages
    data_file_name = domain + (".latest" if latest else "") + ".txt"
    docs = read_docs(data_file_name)
    # keep a untokenized copy to display back to users
    docs_intact = read_docs_intact(data_file_name)

    global num_docs
    # help with computing TF-IDF
    num_docs = len(docs)

    stopwords = read_stopwords('common_words')

    term_funcs = {
        'tf': compute_tf,
        'tfidf': compute_tfidf,
        'boolean': compute_boolean
    }

    sim_funcs = {
        'cosine': cosine_sim,
        'jaccard': jaccard_sim,
        'dice': dice_sim,
        'overlap': overlap_sim
    }

    # different relative weights between doc fields, depending on which one the user wants to use
    term_weights = TermWeights(author=1, title=3, body=1) if weights == "131" else TermWeights(author=1, title=1, body=4) if weights == "114" else TermWeights(author=1, title=1, body=1)

    # stemming tokens, remove stopwords for both the web pages and the user query
    processed_docs, processed_queries = process_docs_and_queries(docs, [query], stem, removestop, stopwords)
    doc_freqs = compute_doc_freqs(processed_docs)

    # vectorize both web page docs and the query doc
    doc_vectors = [term_funcs[weighting](doc, doc_freqs, term_weights) for doc in processed_docs]
    query_vec = term_funcs[weighting](processed_queries[0], doc_freqs, term_weights)
    
    # search for the most relevant web pages given query
    results = search(docs_intact, doc_vectors, query_vec, sim_funcs[similarity], count)

    return results


# remove stopwords and/or stem tokens for both crawled web page docs and queries
def process_docs_and_queries(docs, queries, stem, removestop, stopwords):
    processed_docs = docs
    processed_queries = queries
    if removestop:
        processed_docs = remove_stopwords(processed_docs)
        processed_queries = remove_stopwords(processed_queries)
    if stem:
        processed_docs = stem_docs(processed_docs)
        processed_queries = stem_docs(processed_queries)
    return processed_docs, processed_queries


# remove stopwords and/or stem tokens for just queries
def process_queries(queries, stem, removestop, stopwords):
    processed_queries = queries
    if removestop:
        processed_queries = remove_stopwords(processed_queries)
    if stem:
        processed_queries = stem_docs(processed_queries)
    return processed_queries


# for term, stem, removestop, sim, term_weights in itertools.product(*permutations):
#     processed_docs, processed_queries = process_docs_and_queries(docs, queries, stem, removestop, stopwords)
#     doc_freqs = compute_doc_freqs(processed_docs)
#     doc_vectors = [term_funcs[term](doc, doc_freqs, term_weights) for doc in processed_docs]

#     metrics = []

#     # search_debug3(processed_docs, doc_vectors, sim_funcs[sim])

#     for query in processed_queries:
#         query_vec = term_funcs[term](query, doc_freqs, term_weights)
#         results = search(doc_vectors, query_vec, sim_funcs[sim])
#         # results = search_debug(processed_docs, query, rels[query.doc_id], doc_vectors, query_vec, sim_funcs[sim])
#         # search_debug2(processed_docs, query, rels[query.doc_id], doc_vectors, query_vec, sim_funcs[sim])
#         rel = rels[query.doc_id]

#         metrics.append([
#             precision_at(0.25, results, rel),
#             precision_at(0.5, results, rel),
#             precision_at(0.75, results, rel),
#             precision_at(1.0, results, rel),
#             mean_precision1(results, rel),
#             mean_precision2(results, rel),
#             norm_recall(results, rel),
#             norm_precision(results, rel)
#         ])

#     averages = [f'{np.mean([metric[i] for metric in metrics]):.4f}'
#         for i in range(len(metrics[0]))]
#     print(term, stem, removestop, sim, ','.join(map(str, term_weights)), *averages, sep='\t')


# self-repeating loop to get well-formatted input from user
def loop_input(i, opts, default = ""):
    if i == "" and default != "":
        print(default)
        return default
    elif not i in opts:
        print("Invalid input. Please enter a valid option.")
        loop_input(input(), opts)
    else:
        return i


# self-repeating loop to get well-formatted input integer from user
def loop_count(i):
    if i == '':
        return -1
    elif not i.isdigit() or int(i) < 0:
        print("Invalid input. Please enter a valid option.")
        loop_count(input())
    else:
        return i


# entrypoint to the CLI app of our Hopkins Search Engine
if __name__ == '__main__':
    print("Welcome to Hopkins Search Engine!")
    print("Enter to select default option of multi-choice input.")

    print("Enter a query to search docs:")
    query = input()

    print("Enter title:")
    title = input()

    print("Enter author(s):")
    author = input()

    print("Enable stemming? (y/n) Default y")
    stem = loop_input(input(), ['y', 'n'], 'y') == 'y'

    print("Remove stopwords? (y/n) Default y")
    removestop = loop_input(input(), ['y', 'n'], 'y') == 'y'

    print("What term weighting function to use? (tf/tfidf/boolean) Default tfidf")
    weighting = loop_input(input(), ['tf', 'tfidf', 'boolean'], 'tfidf')

    print("What similarity function to use? (cosine/jaccard/dice/overlap) Default cosine")
    similarity = loop_input(input(), ['cosine', 'jaccard', 'dice', 'overlap'], 'cosine')

    print("What weights to use? (131/114/111) Default 114")
    weights = loop_input(input(), ['131', '114', '111'], '114')

    print("How many docs do you want retrieved? Leave blank for unlimited")
    count = int(loop_count(input()))

    num = "unlimited" if count == -1 else "at most " + str(count)
    print(f"Searching for {num} docs using {query}, {author}, {stem}, {removestop}, {weighting}, {similarity}, {weights}...")

    results = process_query(title, query, author, stem, removestop, weighting, similarity, weights, count)

    # results = process_query()

    print("Found the following docs (ranked by similarity):")
    
    for doc in results:
        print("ID:", doc["id"])
        print("Title:", doc["title"])
        print("Author:", doc["author"])
        print("Body:", doc["body"])
        print("URL:", doc["url"])
        print()
