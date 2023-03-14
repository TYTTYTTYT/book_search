
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pymongo
from bson.json_util import dumps
import time

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["TTDS"]
mycol = mydb["Bookreview"]
review_col = mydb['Review']

class DatabaseTest(BaseHTTPRequestHandler):

    def do_POST(self):
        tic = time.time()
        self.send_response(201)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length).decode('utf8')
        data = json.loads(body)
        missing = 0
        
        if 'uid' in data:
            review_col.insert_one(data)
            response = data
        else:
            response = {"bookid_result_list": dict()}
            bookids = list(map(lambda x: str(x), data['bookid_list']))
            not_found = set(bookids)
                
            myquery = {'book_id': {'$in': bookids}}
            for result in mycol.find(myquery):
                response["bookid_result_list"][int(result['book_id'])] = result
                not_found.remove(str(result['book_id']))
            for miss_id in list(not_found):
                missing += 1
                response["bookid_result_list"][int(miss_id)] = None

        jstring = dumps(response).encode('utf8')
        self.wfile.write(jstring)
        print('Elapsed: %s' % (time.time() - tic))
        print(f'{missing} books not found')

if __name__ == "__main__":
    print('Server start.')
    httpd = HTTPServer(('0.0.0.0', 30001), DatabaseTest)
    httpd.serve_forever()
