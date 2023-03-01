from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class ColBERTTest(BaseHTTPRequestHandler):

    def do_POST(self):
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

        response = {'rank_info_books': list[range(1000000, 1010000)]}
        # <<< @Xiaochen Zhang <<<

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)


if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 30003), ColBERTTest)
    httpd.serve_forever()
