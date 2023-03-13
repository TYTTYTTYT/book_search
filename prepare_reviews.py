from index_server.cache_dict.cache_dict import CacheDict
import json
import codecs
from collections import deque

book_data = CacheDict(100000, 'data/goodreads/book_database_with_review/')

with codecs.open('data/goodreads/book_database_data.json', 'r', encoding='utf-8') as fin:
    num = 0
    errors = 0
    while True:
        num += 1
        if num % 100000 == 0: print(num)
        line = fin.readline()
        if not line:
            break
        try:
            doc = json.loads(line)
            book_id = doc['book_id']
            doc['comments'] = deque()
            book_data[book_id] = doc
        except:
            print(line)
            errors += 1
            
book_data.save()

with codecs.open('data/goodreads/goodreads_reviews_dedup.json', 'r', encoding='utf-8') as fin:
    num = 0
    errors = 0
    while True:
        num += 1
        if num % 1000 == 0: print(num)
        line = fin.readline()
        if not line:
            break
        try:
            review = json.loads(line)
            book_id = review['book_id']
            user_id = review['user_id']
            review_text = review['review_text']
            score = review['rating']
            
            book_data[book_id]['comments'].append((user_id, review_text, score))
        except:
            print(line)
            errors += 1

book_data.save()