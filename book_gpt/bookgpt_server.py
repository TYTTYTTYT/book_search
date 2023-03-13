from bookgpt2 import Bookgpt
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import json
import logging

FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
logging.basicConfig(encoding='utf-8', level=logging.INFO, format=FORMAT)
logger = logging.getLogger('GPT server')

message = [{"role": "user", "content": f"You are a book suggestion bot. I will specify the subject matter in my messages, and you will reply with 5 books that includes the subjects I mention in my messages. ONLY reply BOOK TITLE without author for further input. If you understand, say OK."},
            {"role": "assistant", 
             "content": f"OK"}]

gpt = Bookgpt(message)


class GptServer(BaseHTTPRequestHandler):

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
            query = data['query']
            logger.info(f"Received query: {query}")
            
            suggestions = gpt.pre(query)

        except Exception as e:
            error_message = repr(e)
        
        time_consume = time.time() - tic
        response = {
            'suggestions': suggestions, 
            'error_message': error_message,
            'response_time': time.time() - tic
            }

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)
        logger.info(f'GPT suggestions {suggestions}, {time_consume}')


