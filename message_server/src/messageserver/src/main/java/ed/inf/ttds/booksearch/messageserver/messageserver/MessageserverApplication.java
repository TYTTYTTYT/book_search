package ed.inf.ttds.booksearch.messageserver.messageserver;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.lang.Math;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestBody;

import ed.inf.ttds.booksearch.messageserver.messageserver.lrucache.LruCache;

@SpringBootApplication
@RestController
public class MessageserverApplication {

    public static LruCache<String, List<Long>> cache = new LruCache<String, List<Long>>(1000);
    private ClientDatabase dbClient;
    private ClientIndex idxClient;
    private ClientColbert bertClient;

    public static void main(String[] args) {
      	SpringApplication.run(MessageserverApplication.class, args);
    }

    public MessageserverApplication() {
        dbClient = new ClientDatabase();
        idxClient = new ClientIndex();
        bertClient = new ClientColbert();
    }

    @GetMapping("/search")
    public WebResult search(@RequestBody WebQuery query) {
        // session id is defined by uid, query_type, and query
        String sid = query.uid.toString() + query.query_type + query.query;

        // Check whether the search result is cached
        List<Long> bookids = cache.get(sid);
        if (bookids == null) {
            // invoke the index search service
            IndexResult indexResult = idxClient.search(query.query_type, query.query);
            int short_len = Math.min(1000, indexResult.bookid_list_ranked_long.size());

            // if free search, rerank using colBERT service
            if (query.query_type == "free") {
                List<Long> bookid_list_ranked_short = indexResult.bookid_list_ranked_long.subList(0, short_len);
                ColbertResult bertResult = bertClient.rank(bookid_list_ranked_short);
                Collections.copy(bertResult.bookid_list_reranked_short, indexResult.bookid_list_ranked_long);
            }
            bookids = indexResult.bookid_list_ranked_long;

            cache.insert(sid, bookids);
        }
        
        // get bookids with corresponding indexes
        Long num = query.result_range.get(1) - query.result_range.get(0);
        int num_books = num.intValue();
        List<Long> bookid_list = new ArrayList<>(num_books);

        // create a map from bookid to index
        Map<Long, Long> idToIdx = new HashMap<>(num_books * 2);
        int shift = query.result_range.get(0).intValue();
        
        for (Long idx = query.result_range.get(0); idx < query.result_range.get(1); idx++) {
            Long id = bookids.get(idx.intValue());
            bookid_list.add(idx.intValue() - shift, id);
            idToIdx.put(id, idx);
        }

        // get book information from the database, using the bookid as keys
        DatabaseResult dbResult = dbClient.getDocs(bookid_list);

        // convert bookid to indexes
        WebResult webResult = new WebResult((long)bookids.size());

        for (Long bookid: bookid_list) {
            Long idx = idToIdx.get(bookid);
            String bookInfo = dbResult.bookid_result_list.get(bookid);
            webResult.result_list.put(idx, bookInfo);
        }

      	return webResult;
    }
}
