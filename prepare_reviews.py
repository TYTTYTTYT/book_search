from index_server.cache_dict.cache_dict import CacheDict
import json
import codecs
from collections import deque
from tqdm import tqdm

book_data = CacheDict(100000, 'data2/book_database_with_review/book_data_cache')

print('Loading the book description dataset')
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
            doc = json.loads(line, )
            book_id = doc['book_id']
            doc['comments'] = deque()
            book_data[book_id] = doc
        except:
            print(line)
            errors += 1
            
book_data.save()
book_data.load()
print(f'book description loaded, {errors} errors encountered')


print('Loading the book reviews')
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
book_data.load()

with codecs.open('data2/book_database_with_review/', 'w', encoding='utf-8') as fout:
    for book_id in tqdm(book_data.keys()):
        line = json.dumps(book_data[book_id], ensure_ascii=False) + '\n'
        fout.write(line)
        