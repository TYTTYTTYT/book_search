from .graph import Graph
import json
from multiprocessing import Pool
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import logging
import argparse

parser = argparse.ArgumentParser(description="Build index or search")

# Build index arguments
parser.add_argument('--index', type=str, help='the graph index path', default='/home/tai/src/projects/book_search/data/goodreads/book_database_data.json')
parser.add_argument('--port', type=int, help='service port', default=30004)

args = parser.parse_args()

FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
logging.basicConfig(encoding='utf-8', level=logging.INFO, format=FORMAT)
logger = logging.getLogger('Graph Server')

    
class GraphServer(BaseHTTPRequestHandler):

    def do_POST(self):
        global graph
        tic = time.time()
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)
        error_message = ''
        nodes, links = [], []

        try:
            bookid = int(data['bookid'])
            neighbor = int(data['neighbor'])
            
            nodes, links = graph.get_neighbor_graph(
                bookid,
                neighbor
            )
            
            nodes = list(map(lambda x: {'id': x[0], 'title': x[1]}, nodes))
            links = list(map(lambda x: {'source': x[0], 'target': x[1]}, links))

        except Exception:
            error_message = repr(error_message)
        
        time_consume = time.time() - tic
        response = {
            'nodes': nodes, 
            'error_message': error_message, 
            'links': links,
            'time': time_consume
            }

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)
        if len(error_message) > 0:
            logger.warning(error_message)
        logger.info(f'Find {len(nodes)}/{len(links)} nodes/edges in {time_consume} seconds.')

if __name__ == '__main__':
    logger.info(f'Loading the graph index from <{args.index}>')
    graph = Graph(args.index)
    graph.load()
    logger.info('Graph Loaded.')
    logger.info(f'Start the server on port {args.port}')
    httpd = HTTPServer(('0.0.0.0', args.port), GraphServer)
    httpd.serve_forever()
    