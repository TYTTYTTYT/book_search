import json
import re
import numpy as np
from nltk.stem import PorterStemmer
from tqdm import tqdm
import pickle
import time

stemmer = PorterStemmer()

with open('index/word_list_1.pkl', 'rb') as f:
    word_list = pickle.load(f)
print("Done.")
def intersection(list1, list2):
    return list(set(list1).intersection(list2))


def union(list1, list2):
    return list(set(list1).union(list2))


def notin(list1, list2):
    list3 = []
    for n in list2:
        if n not in list1:
            list3.append(n)
    return list3


def phraseSearch(query):
    # Phrase search
    querydoc = []
    queryresult = []
    phraseresult = []
    prephase = []
    phrases = query.strip(' "')
    phraselist = phrases.split()
    for term in phraselist:
        term = stemmer.stem(term)
        term = term.lower()
        prephase.append(term)
        list1 = word_list[term][1]
        querydoc.append(list1)
    queryresult = intersection(querydoc[0], querydoc[1])
    for i in queryresult:
        for a in word_list[prephase[0]][1][i]:
            for b in word_list[prephase[1]][1][i]:
                if b - a == 1:
                    if int(i) not in phraseresult:
                        phraseresult.append(int(i))
    return phraseresult

def booleanSearch(query):

    splitterms = []
    querydoc = []
    list1 = []
    list2 = []
    splitterms = query.split(' AND')


    for word in splitterms:
        notq = word.find('NOT')
        phraseS = word.find('"')
        if notq != -1:
            wordnot = ''.join(word.split('NOT')).strip()
            wordnot = stemmer.stem(wordnot)
            wordnot = wordnot.lower()
            list2 = list(word_list[wordnot][1].keys())
            list2 = notin(list2, docnol)
            querydoc.append(list2)
        elif phraseS != -1:
            phraseresult = phraseSearch(word)
            querydoc.append(phraseresult)
        else:
            word = word.strip()
            print(word)
            word = word.lower()
            print(word)
            word = stemmer.stem(word)
            print(word)
            list1 = list(word_list[word][1].keys())
            querydoc.append(list1)
    queryresult = intersection(querydoc[0], querydoc[1])
    return queryresult


def orSearch(query):
    splitterms = []
    querydoc = []
    list1 = []
    list2 = []
    queryresult = []
    splitterms = query.split('OR')
    for word in splitterms:
        notq = word.find('NOT')
        if notq != -1:
            wordnot = ''.join(word.split('NOT')).strip()
            wordnot = stemmer.stem(wordnot)
            wordnot = wordnot.lower()
            list1 = list(word_list[wordnot][1].keys())
            list2 = notin(list1, docnol)
            querydoc.append(list2)
        else:
            word = word.strip()
            word = stemmer.stem(word)
            word = word.lower()
            list1 = list(word_list[word][1].keys())
            querydoc.append(list1)
    queryresult = union(querydoc[0], querydoc[1])
    return queryresult


def proximitySearch(query):
    # Phrase search
    querydoc = []
    queryresult = []
    phraseresult = []
    prephrase = []
    dis = query[1:3]
    query = query.strip('#')
    query = query.strip(dis)
    query = query.strip('()')
    query = query.strip(' #()')
    phraselist = query.split(', ')
    for term in phraselist:
        term = term.strip(" ")
        term = stemmer.stem(term)
        term = term.lower()
        prephrase.append(term)
        list1 = word_list[term][1]
        querydoc.append(list1)
    queryresult = intersection(querydoc[0], querydoc[1])
    for i in queryresult:
        for a in word_list[prephrase[0]][1][i]:
            for b in word_list[prephrase[1]][1][i]:
                if -int(dis) < (b - a) < int(dis):
                    if int(i) not in phraseresult:
                        phraseresult.append(int(i))
    return phraseresult


from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class IndexTest(BaseHTTPRequestHandler):

    def do_POST(self):
        tic = time.time()
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)
        # print(data)

        # >>> your codes goes here, replace the random numbers with search results >>>
        # print("New query: ", data['query_type'], data['query'])
        query = data['query']
        query_type = data['query_type']
        if query_type == 'boolean':
            bookid_list_ranked_long = booleanSearch(query)
        elif query_type == 'phrase':
            bookid_list_ranked_long = phraseSearch(query)
        elif query_type == 'proximity':
            bookid_list_ranked_long = proximitySearch(query)
        else:
            bookid_list_ranked_long = "服务器开小差了，请稍后再试"
        # random.shuffle(bookid_list_ranked_long)

        response = {'bookid_list_ranked_long': bookid_list_ranked_long}
        # <<< @Ziyi Yan <<<

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)
        print('Elapsed: %s' % (time.time() - tic))


if __name__ == "__main__":
    print("Server start!!")
    httpd = HTTPServer(('localhost', 30002), IndexTest)
    httpd.serve_forever()