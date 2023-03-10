"""Build the index or execute searches

This python program has two functions, index building and searching. Please 
make sure you use the python 3.10 version or higher. To build the index, run

```
python code.py --build --docpath path/to/trec.5000.xml --stoppath \
    path/to/stopwords.txt --indexpath path/to/save/index
```

If the `--stoppath` is not specified, the program will not perform stopping.

To search documents, run

```
python code.py --search --bool path/to/queries.boolean.txt --boolout \
    path/to/results.boolean.txt --ranked path/to/queries.ranked.txt \
    --rankedout path/to/results.ranked.txt --indexpath path/to/index.bin
```

For more details, please run `python code.py --help`
"""

import os
import re
import pickle
import argparse
from typing import Any, Optional
import xml.etree.ElementTree as ET
from math import log
import logging
import time
from collections import deque
import heapq
import json
from pathlib import Path
from multiprocessing import Pool

from nltk.stem.porter import PorterStemmer
from tqdm import tqdm

from http.server import HTTPServer, BaseHTTPRequestHandler
from cache_dict.cache_dict import CacheDict
# from transformers import GPT2Tokenizer

# Tokenizer pattern
TOKENIZE_PATTERN = r"(?:[a-zA-Z]+)|(?:[a-zA-Z]+'[a-zA-Z]+)|(?:[0-9]+(?:[./,][0-9]+)*)"

# Boolean search query pattern
BOOL_QUERY_PATTERN = r"""['")(]|[0-9a-zA-Z]+"""

# Proximity search query pattern
PROXIMITY_QUERY_PATTERN = r" *\#([0-9]+)\((.+?)\)"

# Unknown token
UNKNOWN = "<unknown>"

# Pattern of batched search
BSB_PATTERN = "([0-9]+) (.*)"
RSB_PATTERN = '([0-9]+) (.*)'

logging.basicConfig(filename='index_server.log', encoding='utf-8', level=logging.INFO)

# encoder = GPT2Tokenizer.from_pretrained('gpt2')
# encoder.max_model_input_sizes['gpt2'] = 1000000
parser = argparse.ArgumentParser(description="Build index or search")

# Build index arguments
parser.add_argument('--build', action='store_true', help='Build index')
parser.add_argument('--datapath', type=str, help='json document path')
parser.add_argument('--stoppath', type=str, help='Stopping word path')
parser.add_argument('--indexpath', type=str, help='Index path')
parser.add_argument('--num_workers', type=int, help='Number of workers')

# Search arguments
parser.add_argument('--search', action='store_true', help='Perform a search')
parser.add_argument('--bool', type=str, help='Bool searh query file')
parser.add_argument('--boolout', type=str, help='Save result of bool search')
parser.add_argument('--ranked', type=str, help='Ranked search query file')
parser.add_argument('--rankedout', type=str, help='Save result of ranked path')

# Serve arguments
parser.add_argument('--serve', action='store_true', help='Init the server')
# parser.add_argument('--max', type=int, help='Maximum number of results')

# Test the functions
parser.add_argument('--test', action='store_true', help='Run the tests')

vocab = None
index_tokenizer = re.compile(TOKENIZE_PATTERN)
def tokenize(sent: str) -> list[str]:
    # Tokenize a string into a list of tokens
    global index_tokenizer
    tokens = index_tokenizer.findall(sent.lower())
    return tokens


stopwords = None
def stopping(tokens: list[str]) -> list[str]:
    # remove the stopping words, if there are no stopping words, do nothing
    global stopwords
    if stopwords is None:
        return tokens
    return list(filter(lambda token: token not in stopwords, tokens))

def stem(tokens: list[str]) -> list[str]:
    # Perform the Porter Stemmer from the NLTK library
    global vocab
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens]
    # Replace OOV with unknown token
    if vocab:
        tokens = list(map(lambda x: x if x in vocab else UNKNOWN, tokens))
    return tokens

def preprocess(sent: str, index: Optional[Any]=None) -> list[int]:
    # Combine the tokenization, stopping and stem.
    tokens = tokenize(sent)
    tokens = stopping(tokens)
    tokens = stem(tokens)
    tokens = ' '.join(tokens)
    # tokens = encoder.encode(tokens)
    return tokens

def preprocess_doc(doc: str) -> tuple[int, list[str]]:
    doc = json.loads(doc)
    docid = int(doc['book_id'])
    title = doc['title']
    description = doc['description']
    author_list = doc['author_list']
    sent = ' '.join([title, description] + author_list)
    tokens = preprocess(sent)
    return docid, tokens

class Index(object):
    def __init__(
        self, 
        path: os.PathLike | str, 
        save_path: os.PathLike | str=None,
        num_workers: int=4,
        cache_size: int=1000
        ) -> None:
        super().__init__()
        self.__index = None
        self.num_docs = 0
        self.__vocab = set()
        self.save_path = save_path
        self.num_workers = num_workers
        self.__index = None
        self.cache_size = cache_size

        if os.path.isdir(path):
            self.load_index()
        else:
            self.build_index()

    def save_index(self) -> None:
        # save the index to a new folder
        os.makedirs(self.save_path, exist_ok=True)
        
        # save the binary index
        meta_path = os.path.join(self.save_path, 'meta.bin')
        with open(meta_path, 'wb') as fout:
            global stopwords
            pickle.dump((self.num_docs, stopwords, vocab), fout)
        self.__index.save()

    def load_index(self) -> None:
        # load the binary index
        meta_path = os.path.join(self.path, 'meta.bin')
        with open(meta_path, 'rb') as fin:
            global stopwords
            global vocab
            self.num_docs, stopwords, vocab = pickle.load(fin)
        index_path = os.path.join(self.path, 'index')
        self.__index = CacheDict(self.cache_size, index_path)
        self.__index.load()

    def build_index(self) -> None:
        # build the index as a dict
        with open(self.path, 'r') as fin:
            docs = fin.readlines()
        self.num_docs = len(docs)
        term_pos = []
        heapq.heapify(term_pos)
        
        logging.info('Preprocessing the corpus...')
        with Pool(self.num_workers) as p:
            docs = p.map(preprocess_doc, docs)
        
        logging.info('Sorting the corpus...')
        for _ in tqdm(range(len(docs))):
            docid, tokens = docs.pop()
            # Add all tokens and corresponding docid and position to a list
            for pos, token in enumerate(tokens):
                heapq.heappush(term_pos, (docid, pos, token))
        del docs
        logging.info(f'{len(term_pos)} tokens in total')

        # Build the docid lists and position lists for each token with order
        # Create the token represents the unknown token
        self.__index = dict()
        self.__index[UNKNOWN] = (deque(), dict())
        for _ in tqdm(range(len(term_pos))):
            (docid, pos, token) = heapq.heappop(term_pos)
            if token not in self.__index:
                self.__vocab.add(token)
                self.__index[token] = (deque(), dict())
            if len(self.__index[token][0]) == 0 or self.__index[token][0][-1] != docid:
                self.__index[token][0].append(docid)
            if docid not in self.__index[token][1]:
                self.__index[token][1][docid] = deque()
            self.__index[token][1][docid].append([pos])
            
        global vocab
        vocab = self.__vocab
        
        # transfer the index into a cached index
        index_path = os.path.join(self.save_path, 'index')
        self.__index = CacheDict(self.cache_size, index_path, self.__index)

    def get_docid(self, token: str) -> list[int]:
        # find a token's docid list
        if token not in self.__index:
            return []
        return self.__index[token][0]

    def get_pos(self, token: str, docid: int) -> list[int]:
        # find a token's position list w.r.t. a docid
        return self.__index[token][1][docid]

    def __str__(self) -> str:
        # format the index into a string line by line
        output = ''
        for token, index in self.__index.items():
            output += token + ':' + str(len(index[0])) + '\n'
            for docid, pos in index[1].items():
                pos = map(str, pos)
                output += '\t' + str(docid) + ': ' + ', '.join(pos) + '\n'
        
        return output

    def search_tokens(self, tokens: list[str], mode: str='AND') -> list[int]:
        # find the docid with common tokens
        docid_lists = []
        for token in tokens:
            lst = self.get_docid(token)
            if len(lst) == 0:
                if mode == 'AND':
                    return []
            else:
                docid_lists += [lst]
        if len(docid_lists) == 0:
            return []
        # use the lienar merge to merge the docid lists
        return linear_merge(*docid_lists, mode=mode)

    def search_proximity(self, tokens: list[str], dist: int=1, 
        bidirect: bool=False) -> list[int]:
        # The default behavior of proximity search is term search
        # Find related docids
        docs = self.search_tokens(tokens)
        if len(docs) == 0:
            return docs
        
        # For each docid, merge the coresponding position lists
        doc_matches = []
        for doc in docs:
            pos_lists = [self.get_pos(token, doc) for token in tokens]
            match = linear_merge(*pos_lists, dist=dist)
            if bidirect:
                pos_lists.reverse()
                match += linear_merge(*pos_lists, dist=dist)
            if len(match) > 0:
                doc_matches += [doc]

        return doc_matches

    def tfidf_weight(self, token: str, docid: int) -> float:
        # calculate the TFIDF of a token to a document
        index = self.__index[token]
        if docid not in index[1]:
            return 0.0
        df = len(index[0])
        tf = len(index[1][docid])
        weight = (1 + log(tf, 10)) * log(self.num_docs / df, 10)
        return weight

def linear_merge(*lists: list[int], dist: int=0, mode: str='AND') -> list[int]:
    """Merge arbitrary number of integer lists in linear time

    Apply the linear merge algorithm to merge lists. If the mode is "AND", 
    only return common items; if the mode is "AND", return the combined list 
    without repetitions; if the mode is "NOT", only accept two lists as input 
    and remove the item in the second lists from the first list.

    All input lists should be ordered ascending, and the result will remain in 
    the order.
    """
    num_list = len(lists)
    lists = list(lists)
    # Initialize the pointers for each list
    pointer = [0] * num_list
    pointer_max = [len(l) for l in lists]
    # The bias is to bias the pointer for proximity search and phrase search
    bias = [b for b in range(0, - num_list * dist, - dist)] if dist != 0 else [0 for _ in lists]
    match = []
    
    while True:
        idx = [lists[i][pointer[i]] for i in range(num_list)]
        idx_bias = [i + b for i, b in zip(idx, bias)]

        match mode:
            case "AND":
                all_match = True
                # If all lists has this item, add it to the result
                for i, id in enumerate(idx[:-1]):
                    if idx[i + 1] - id > dist or idx[i + 1] - id < 0:
                        all_match = False
                        break
                if all_match:
                    match += [idx[0]]
            case "OR":
                # Do not add repeat items
                if len(match) == 0:
                    match += [min(idx)]
                elif min(idx) > match[-1]:
                    match += [min(idx)]
                # Remove the item appeared in the second list
            case "NOT":
                assert num_list == 2
                if idx[1] > idx[0]:
                    match += [idx[0]]
            case _:
                raise KeyError(f'Merge mode must be "AND", "OR", or "NOT". But get "{mode}".')

        # Find the list with the lowest biased index
        min_list = 0
        min_idx = idx_bias[min_list]
        for i in range(num_list):
            if idx_bias[i] < min_idx:
                min_list = i
                min_idx = idx_bias[i]
        
        # Move the pointer of the list with the lowest biased index
        pointer[min_list] += 1

        # When maxmimum position reached
        if pointer[min_list] >= pointer_max[min_list]:
            # In AND mode, all following items should not appear in result
            if mode == "AND": break
            if mode == "NOT":
                # If the second list ended, the remaining items are kept
                if min_list == 1:
                    match += lists[0][pointer[0]:]
                break
            if mode == "OR":
                if num_list == 1:
                    break
                num_list -= 1
                # Delete the finished lists
                del pointer[min_list]
                del lists[min_list]
                del pointer_max[min_list]
                del bias[min_list]

    return match



# The syntax of the boolean query is defined below:

# query -> query op term
#        | term
# op    -> AND
#        | OR
#        | AND NOT
#        | NOT
# term  -> " phrase "
#        | ' phrase '
#        | word
#        | ( query )

# which could be converted to below to avoid infinite recursion

# query  -> term queryt
# queryt -> op term queryt
#         | END
# op     -> AND
#         | OR
#         | NOT
#         | AND NOT
# term   -> " phrase "
#         | ' phrase '
#         | word
#         | ( query )


def parse_query(tokens: list[str], index: Index) -> tuple[list[int], list[str]]:
    # A query is consists of a term and a query tail
    term, remain = parse_term(tokens, index)
    result, remain = parse_queryt(remain, index, term)
    return result, remain

def parse_queryt(tokens: list[str], index: Index, pre_term: list[int] | str | list[str]) -> tuple[list[int], list[str]]:
    # parse the query tail
    if len(tokens) == 0 or tokens[0] == ')':
        if isinstance(pre_term, list) and len(pre_term) > 0 and isinstance(pre_term[0], str):
            preprocessed = preprocess(' '.join(pre_term))
        elif isinstance(pre_term, str):
            preprocessed = preprocess(pre_term)
        elif isinstance(pre_term, list) and len(pre_term) > 0 and isinstance(pre_term[0], int):
            return pre_term, tokens
        else:
            raise SyntaxError(f'queryt cannot parse {tokens}')
        # When previous operations are AND operations, find all token docids
        result = index.search_tokens(preprocessed)
        return result, tokens

    # parse the operator and the term
    op, remain = parse_op(tokens, index)
    term, remain = parse_term(remain, index)

    if op == 'AND' and isinstance(term, str) and (isinstance(pre_term, str) or (isinstance(pre_term, list) and len(pre_term) > 0 and isinstance(pre_term[0], str))):
        pre_term = [pre_term] if isinstance(pre_term, str) else pre_term
        partial_result = pre_term + [term]
        return parse_queryt(remain, index, partial_result)

    if isinstance(term, str):
        term = index.search_tokens(preprocess(term))
    if isinstance(pre_term, str):
        pre_term = index.search_tokens(preprocess(pre_term))
    elif isinstance(pre_term, list) and len(pre_term) > 0 and isinstance(pre_term[0], str):
        tokens = preprocess(' '.join(pre_term))
        pre_term = index.search_tokens(tokens)

    if len(pre_term) == 0:
        if op == "AND":
            partial_result = []
        elif op == 'OR':
            partial_result = term
        elif op == 'NOT':
            partial_result = []
    elif len(term) == 0:
        if op == "AND":
            partial_result = []
        elif op == 'OR':
            partial_result = pre_term
        elif op == 'NOT':
            partial_result = pre_term
    else:
        partial_result = linear_merge(pre_term, term, mode=op)

    return parse_queryt(remain, index, partial_result)

def parse_term(tokens: list[str], index: Index) -> tuple[list[int] | str, list[str]]:
    assert isinstance(tokens, list)
    if tokens[0] == '"' or tokens[0] == "'":
        quote = tokens[0]
        words = []
        idx = 0
        while True:
            idx += 1
            if tokens[idx] == quote:
                break
            words += [tokens[idx]]
        docs = index.search_proximity(preprocess(' '.join(words)))
        remain = tokens[idx + 1:]
        return docs, remain
    elif tokens[0] == '(':
        docs, remain = parse_query(tokens[1:], index)
        if len(remain) == 0 or remain[0] != ')':
            raise SyntaxError(f'Parentheses are not closed! {remain}')
        return docs, remain[1:]
    else:
        return tokens[0], tokens[1:]

def parse_op(tokens: list[str]) -> tuple[str, list[str]]:
    if len(tokens) == 0:
        raise SyntaxError('Missing operator')
    if not (tokens[0] == 'AND' or tokens[0] == 'OR' or tokens[0] == 'NOT'):
        raise SyntaxError(f'Expect operator "AND", "OR", or "NOT", but get <{tokens[0]}>')
    if tokens[0] == 'AND' and tokens[1] == 'NOT':
        return 'NOT', tokens[2:]
    return tokens[0], tokens[1:]

bool_tokenizer = re.compile(BOOL_QUERY_PATTERN)
def boolean_search(query: str, index: Index) -> list[int]:
    # Perform a boolean search query
    tokens = bool_tokenizer.findall(query)
    result, _ = parse_query(tokens, index)
    return result

proximity_partern = re.compile(PROXIMITY_QUERY_PATTERN)
def proximity_search(query: str, index: Index) -> list[int]:
    # perform a proximity search query
    global proximity_partern
    match = proximity_partern.match(query)
    # Use the regular expression to get the distance number
    dist = int(match.group(1))
    tokens = preprocess(match.group(2))

    return index.search_proximity(tokens, dist, bidirect=True)

def ranked_search(query: str, index: Index) -> list[tuple[int, float]]:
    # perform a ranked search query using TFIDF weight
    tokens = preprocess(query)
    docids = index.search_tokens(tokens, mode='OR')
    result = []
    for docid in docids:
        weight = 0.0
        for token in tokens:
            # Use TFIDF weight
            weight += index.tfidf_weight(token, docid)
        result += [(docid, weight)]
    # Sort the result using the scores
    result.sort(key=lambda x: x[1], reverse=True)

    return result


index = None
class IndexTest(BaseHTTPRequestHandler):

    def do_POST(self):
        global index
        tic = time.time()
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)

        try:
            query = data['query']
            query_type = data['query_type']
            if query_type == 'boolean':
                bookid_list_ranked_long = boolean_search(query, index)
            elif query_type == 'phrase':
                bookid_list_ranked_long = ranked_search(query, index)
            elif query_type == 'proximity':
                bookid_list_ranked_long = proximity_search(query, index)
            else:
                bookid_list_ranked_long = []
        except Exception as e:
            error_message = str(e)
            logging.error(error_message)
            bookid_list_ranked_long = []

        toc = time.time()
        response = {
            'bookid_list_ranked_long': bookid_list_ranked_long, 
            'error_message': error_message, 
            'search_time': toc - tic
            }

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)
        logging.info('Elapsed: %s' % toc - tic)

    
if __name__ == "__main__":
    # Parse the arguments
    args = parser.parse_args()
    index = None

    # If the build index command is specified
    if args.build:
        logging.info('building the index')
        # Read the stopwords if which is specified
        if args.stoppath is not None:
            with open(args.stoppath, 'r') as f:
                stopwords = set(f.read().split())
        
        # Build and save the index
        logging.info('Begin to build the index...')
        index = Index(args.datapath, args.indexpath, args.num_workers)
        logging.info('The index is built successfully.')
        index.save_index()
        logging.info(f'The index is saved to {args.indexpath}.')

    # If the search command is specified
    elif args.serve:
        # load the index
        if index is None:
            logging.info('Initializing index...')
            index = Index(args.indexpath)
            logging.info('Index initialized.')
            
        logging.info('Start the server')
        httpd = HTTPServer(('localhost', 30002), IndexTest)
        httpd.serve_forever()

    # Test the functions
    elif args.test:
        r1 = boolean_search('(car OR vehicle) AND (motor OR engine) AND NOT (cooler)', index)
        car = set(index.search_tokens(preprocess('car')))
        veh = set(index.search_tokens(preprocess('vehicle')))
        mot = set(index.search_tokens(preprocess('motor')))
        eng = set(index.search_tokens(preprocess('engine')))
        coo = set(index.search_tokens(preprocess('cooler')))
        r2 = list((car.union(veh)).intersection(mot.union(eng)) - coo)
        r2.sort()
        for i, j in zip(r1, r2):
            assert i == j
        print('Complex query test passed')
