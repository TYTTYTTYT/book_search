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
        bookid_list_ranked_short = data['bookid_list_ranked_short']
        bookid_list_ranked_short.reverse()

        response = {'bookid_list_reranked_short': bookid_list_ranked_short}
        # <<< @Xiaochen Zhang <<<

        jstring = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.wfile.write(jstring)


if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 30003), ColBERTTest)
    httpd.serve_forever()
