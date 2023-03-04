import os
import sys
from tqdm import tqdm
import time
sys.path.insert(0, '../')

from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert.data import Queries, Collection
from colbert import Indexer, Searcher

nbits = 2   # encode each dimension with 2 bits
doc_maxlen = 300   # truncate passages at 300 tokens

checkpoint = 'index/colbertv2.0'
index_name = 'index/indexes/lifestyle.dev.2bits'
file_path = 'index/id_pid.tsv'
# dataroot = 'downloads/lotte'
# dataset = 'lifestyle'
# datasplit = 'dev'

# queries = os.path.join(dataroot, dataset, datasplit, 'questions.search.tsv')
# collection = os.path.join(dataroot, dataset, datasplit, 'collection.tsv')

# queries = Queries(path=queries)
# collection = Collection(path=collection)

# f'Loaded {len(queries)} queries and {len(collection):,} passages'
# To create the searcher using its relative name (i.e., not a full path), set
# experiment=value_used_for_indexing in the RunConfig.
with Run().context(RunConfig(experiment='notebook')):
    searcher = Searcher(index=index_name)

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
# use dict to store id and pid
id_pid = {}
for line in lines:
    line = line.strip()
    line = line.split('\t')
    id_pid[line[0]] = line[1]

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class ColBERTTest(BaseHTTPRequestHandler):

    def do_POST(self):
        tic = time.time()
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)
        print(data)

        # >>> your codes goes here, replace the random numbers with search results >>>
        query = data['query']
        k = int(data['k'])
        results = searcher.search(query, k=k)
        # query = "Chinese cooking recepit"
        # k = 3
        # print(f"#> {query}")
        rank_info_books = []
        for passage_id, passage_rank, passage_score in zip(*results):
            book_id = id_pid[str(passage_id)]
            rank_info_books.append(book_id)
        response = {'rank_info_books': rank_info_books}
        # <<< @Xiaochen Zhang <<<

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)
        print('Elapsed: %s' % (time.time() - tic))


if __name__ == "__main__":
    print("Starting server on port 30003")
    httpd = HTTPServer(('localhost', 30003), ColBERTTest)
    httpd.serve_forever()