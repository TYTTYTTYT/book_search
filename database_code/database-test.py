
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["TTDS"]
mycol = mydb["Bookreview"]

class DatabaseTest(BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)

        response = {"bookid_result_list": dict()}
        for bookid in data['bookid_list']:
            # TODO:
            # >>> Your codes goes here, replace the fake data with real data >>>
            
            myquery = {'book_id':bookid}
            data = str(mycol.find_one(myquery))
            response["bookid_result_list"][int(bookid)] = data

            # <<< @Claudia Zhou <<<

        jstring = json.dumps(response).encode('utf8')
        self.wfile.write(jstring)


if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 30001), DatabaseTest)
    httpd.serve_forever()