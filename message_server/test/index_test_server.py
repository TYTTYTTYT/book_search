from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random


class IndexTest(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)
        print(data)

        # >>> your codes goes here, replace the random numbers with search results >>>
        print("New query: ", data['query_type'], data['query'])
        bookid_list_ranked_long = list(range(1000000, 1100000))
        # random.shuffle(bookid_list_ranked_long)

        response = {'bookid_list_ranked_long': bookid_list_ranked_long}
        # <<< @Ziyi Yan <<<

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)


if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 30002), IndexTest)
    httpd.serve_forever()
