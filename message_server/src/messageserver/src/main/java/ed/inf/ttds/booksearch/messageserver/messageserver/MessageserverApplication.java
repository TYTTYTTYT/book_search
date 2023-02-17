package ed.inf.ttds.booksearch.messageserver.messageserver;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
// import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestBody;

import ed.inf.ttds.booksearch.messageserver.messageserver.lrucache.LruCache;

@SpringBootApplication
@RestController
public class MessageserverApplication {

    public static LruCache<String, List<Long>> cache = new LruCache<String, List<Long>>(1000000);
    private ClientDatabase dbClient;

    public static void main(String[] args) {
      	SpringApplication.run(MessageserverApplication.class, args);
    }

    public MessageserverApplication() {
        dbClient = new ClientDatabase();
    }

    @GetMapping("/search")
    public WebResult search(@RequestBody WebQuery query) {
        // session id is defined by uid, query_type, and query
        String sid = query.uid.toString() + query.query_type + query.query;

        // Check whether the search result is cached
        List<Long> bookids = cache.get(sid);
        if (bookids == null) {
            // >>> TODO: replace the fake docids with real ranked bookids >>>
            // Add 10000 fake docids
            bookids = new ArrayList<>(10000);
            for (int i = 0; i < 10000; i++) {
                // fake bookid from 1000000 to 1009999
                bookids.add(i, (long)i + 1000000l);
            }
            // <<< TODO: replace the fake docids with real ranked bookids <<<
            cache.insert(sid, bookids);
        }
        
        // get bookids with corresponding indexes
        Long num = query.result_range.get(1) - query.result_range.get(0);
        int num_books = num.intValue();
        List<Long> bookid_list = new ArrayList<>(num_books);

        // create a map from bookid to index
        Map<Long, Long> idToIdx = new HashMap<>();
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
