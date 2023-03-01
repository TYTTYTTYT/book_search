from http.server import HTTPServer, BaseHTTPRequestHandler
import json


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
            data = {"isbn": "", "啦啦啦啦中文测试": "7", "series": ["189911"], "country_code": "US", "language_code": "eng", "popular_shelves": [{"count": "58", "name": "to-read"}, {"count": "15", "name": "fantasy"}, {"count": "6", "name": "fiction"}, {"count": "5", "name": "owned"}, {"count": "3", "name": "hardcover"}, {"count": "2", "name": "shelfari-favorites"}, {"count": "2", "name": "series"}, {"count": "1", "name": "might-read"}, {"count": "1", "name": "dnf-d"}, {"count": "1", "name": "hambly-barbara"}, {"count": "1", "name": "strong-females"}, {"count": "1", "name": "first-in-series"}, {"count": "1", "name": "fantasy-sword-sorcery"}, {"count": "1", "name": "no-thanks-series-collections-boxes"}, {"count": "1", "name": "fantasy-all"}, {"count": "1", "name": "entertaining-but-limited"}, {"count": "1", "name": "kate-own"}, {"count": "1", "name": "fantasy-epic"}, {"count": "1", "name": "e-book"}, {"count": "1", "name": "compliation"}, {"count": "1", "name": "my-books"}, {"count": "1", "name": "books-i-own-but-have-not-read"}, {"count": "1", "name": "everything-owned"}, {"count": "1", "name": "books-to-find"}, {"count": "1", "name": "i-own-it"}, {"count": "1", "name": "favorite"}, {"count": "1", "name": "not-read"}, {"count": "1", "name": "read-some-day"}, {"count": "1", "name": "library"}, {"count": "1", "name": "audiobooks"}, {"count": "1", "name": "status-borrowed"}, {"count": "1", "name": "paranormal-mystery"}, {"count": "1", "name": "owned-books"}, {"count": "1", "name": "spec-fic-fantasy-epic"}, {"count": "1", "name": "spec-fic-fantasy"}, {"count": "1", "name": "spec-fic-awd-locus-nom"}, {"count": "1", "name": "spec-fic"}, {"count": "1", "name": "01"}, {"count": "1", "name": "hardbacks"}, {"count": "1", "name": "paper"}, {"count": "1", "name": "german"}, {"count": "1", "name": "hardback"}, {"count": "1", "name": "physical-scifi-fantasy"}, {"count": "1", "name": "childhood-favorites"}, {"count": "1", "name": "bundle-same-author"}, {"count": "1", "name": "aa-sifi-fantasy"}, {"count": "1", "name": "ready-to-read"}, {"count": "1", "name": "bought-on-flee-markets"}, {"count": "1", "name": "fantasy-general"}, {"count": "1", "name": "hardcopy"}, {"count": "1", "name": "box-2"}, {"count": "1", "name": "unfinished"}, {"count": "1", "name": "magic"}, {"count": "1", "name": "duplicates"}, {"count": "1", "name": "favorites"}, {"count": "1", "name": "books-i-own"}, {"count": "1", "name": "fantasy-classic"}, {"count": "1", "name": "own-hard-copy"}, {"count": "1", "name": "fantasy-read"}, {"count": "1", "name": "book-club-edition"}, {"count": "1", "name": "sci-fi-or-fantasy"}, {"count": "1", "name": "fiction-fantasy"}, {"count": "1", "name": "fiction-literature-poetry"}, {"count": "1", "name": "paused-hiatus"}, {"count": "1", "name": "status—borrowed"}, {"count": "1", "name": "recs-fantasy"}, {"count": "1", "name": "fantasy-scifi"}, {"count": "1", "name": "omnibus"}, {"count": "1", "name": "speculative"}, {"count": "1", "name": "sf--fantasy"}, {"count": "1", "name": "in-my-home-library"}, {"count": "1", "name": "fant-myth-para-vamps"}, {"count": "1", "name": "read-in-my-20s"}], "asin": "B00071IKUY", "is_ebook": "false", "average_rating": "4.03", "kindle_asin": "", "similar_books": ["19997", "828466", "1569323", "425389", "1176674", "262740", "3743837", "880461", "2292726", "1883810", "1808197", "625150", "1988046", "390170", "2620131", "383106", "1597281"], "description": "Omnibus book club edition containing the Ladies of Madrigyn and the Witches of Wenshar.", "format": "Hardcover", "link": "https://www.goodreads.com/book/show/7327624-the-unschooled-wizard", "authors": [{"author_id": "10333", "role": ""}], "publisher": "Nelson Doubleday, Inc.", "num_pages": "600", "publication_day": "", "isbn13": "", "publication_month": "", "edition_information": "Book Club Edition", "publication_year": "1987", "url": "https://www.goodreads.com/book/show/7327624-the-unschooled-wizard", "image_url": "https://images.gr-assets.com/books/1304100136m/7327624.jpg", "book_id": "7327624", "ratings_count": "140", "work_id": "8948723", "title": "The Unschooled Wizard (Sun Wolf and Starhawk, #1-2)", "title_without_series": "The Unschooled Wizard (Sun Wolf and Starhawk, #1-2)", "author_list": ["Barbara Hambly"], "series_list": [["Sun Wolf and Starhawk", ""]]}
            response["bookid_result_list"][int(bookid)] = data

            # <<< @Claudia Zhou <<<

        jstring = json.dumps(response).encode('utf8')
        self.wfile.write(jstring)


if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 30001), DatabaseTest)
    httpd.serve_forever()
