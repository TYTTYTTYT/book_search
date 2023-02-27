from urllib import request
from tqdm import tqdm
import json

counter = 0
for i in tqdm(range(1)):
    data = {
        "uid": i,
        "query": "what is that这是哦爱我发觉我i",
        "query_type": "boolean",
        "result_range": [10, 25]
    }
    data = json.dumps(data, ensure_ascii=False).encode('utf8')
    with open('request.json', 'w') as fout:
        fout.write(data.decode('utf8'))
    r = request.Request('http://127.0.0.1:8080/search', data=data, headers={'Content-Type': 'application/json; charset=utf-8'}, method="GET")
    with request.urlopen(r) as f:
        c = f.read().decode('utf-8')
        print(c)
        counter += len(c)