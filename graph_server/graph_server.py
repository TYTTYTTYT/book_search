from graph import Graph
import json
from multiprocessing import Pool
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import logging
import argparse

parser = argparse.ArgumentParser(description="Build index or search")

# Build index arguments
parser.add_argument('--index', type=str, help='the graph index path', default='/home/tai/src/projects/book_search/data/goodreads/book_database_data.json')
parser.add_argument('--port', type=str, help='service port', default=30004)

args = parser.parse_args()

FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
logging.basicConfig(encoding='utf-8', level=logging.INFO, format=FORMAT)
logger = logging.getLogger('Graph Server')

def convert(l: list[str]) -> list[int]:
    return [int(s) for s in l]
    
def get_ids(line: str) -> tuple[int, list[int]]:
    j = json.loads(line)
    del line
    return int(j['book_id']), convert(j['similar_books'])

logger.info('Loading the graph index')
graph = Graph()
with open(args.index, 'r') as fin:
    while True:
        line = fin.readline()
        if not line:
            break
        book_id, simis = get_ids(line)
        
        if book_id not in graph:
            graph.add_node(book_id, None)
            for simid in simis:
                if simid not in graph:
                    graph.add_node(simid, None)
                graph.add_edge(book_id, simid)
                graph.add_edge(simid, book_id)

logger.info('Done.')

    
class GraphServer(BaseHTTPRequestHandler):

    def do_POST(self):
        global index
        tic = time.time()
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)
        error_message = ''

        try:
            bookid = int(data['bookid'])
            neighbor = int(data['neighbor'])
            
            nodes, edges = graph.get_neighbor_graph(
                bookid,
                neighbor
            )
            links = []
            for link in edges:
                links.append({"source": link[0], "target": link[1]})

        except Exception:
            error_message = repr(error_message)
            
        response = {
            'nodes': nodes, 
            'error_message': error_message, 
            'links': links
            }

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)
        logger.info(f'Find {len(nodes)}/{len(links)} nodes/edges in {time.time() - tic} seconds.')

if __name__ == '__main__':

    logger.info(f'Start the server on port {args.port}')
    httpd = HTTPServer(('0.0.0.0', args.port), GraphServer)
    httpd.serve_forever()
    