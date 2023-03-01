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
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.CrossOrigin;

import ed.inf.ttds.booksearch.messageserver.messageserver.lrucache.LruCache;
import ed.inf.ttds.booksearch.messageserver.messageserver.messageclient.ClientColbert;
import ed.inf.ttds.booksearch.messageserver.messageserver.messageclient.ClientDatabase;
import ed.inf.ttds.booksearch.messageserver.messageserver.messageclient.ClientIndex;
import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.ColbertResult;
import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.DatabaseResult;
import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.ColbertResultK;
import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.IndexResult;
import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.WebQuery;
import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.WebResult;

@CrossOrigin
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

    @GetMapping("/searchbybody")
    public WebResult search(@RequestBody WebQuery query) {
        // session id is defined by uid, query_type, and query
        String sid = query.uid.toString() + query.query_type + query.query;

        // Check whether the search result is cached
        List<Long> bookids = cache.get(sid);
        if (bookids == null) {
            // invoke the index search service
            IndexResult indexResult = idxClient.search(query.query_type, query.query);
            int index_result_num = indexResult.bookid_list_ranked_long.size();

            // if free search, rerank using colBERT service
            // if (query.query_type == "free") {
            //     List<Long> bookid_list_ranked_short = indexResult.bookid_list_ranked_long.subList(0, short_len);
            //     ColbertResult bertResult = bertClient.rank(bookid_list_ranked_short);
            //     Collections.copy(bertResult.bookid_list_reranked_short, indexResult.bookid_list_ranked_long);
            // }
            if (query.query_type == "phrase") {
                Long k = (long) Math.max(1000, indexResult.bookid_list_ranked_long.size());
                if (k > 10000l) {
                    k = 10000l;
                }
                ColbertResultK bertResult = bertClient.search(query.query, k);
                int bert_result_num = bertResult.rank_info_books.size();
                if (index_result_num >= bert_result_num) {
                    Collections.copy(indexResult.bookid_list_ranked_long, bertResult.rank_info_books);
                } else {
                    indexResult.bookid_list_ranked_long = bertResult.rank_info_books;
                }
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
            Map<Object, Object> bookInfo = dbResult.bookid_result_list.get(bookid);
            webResult.result_list.put(idx, bookInfo);
        }

      	return webResult;
    }

    @GetMapping("/search")
    public WebResult search(
        @RequestParam Long uid, 
        @RequestParam String query_type,
        @RequestParam String query,
        @RequestParam Long result_range_from,
        @RequestParam Long result_range_to
        ) {
        // session id is defined by uid, query_type, and query
        String sid = query_type + query;
        System.out.println(sid);

        // Check whether the search result is cached
        List<Long> bookids = cache.get(sid);
        if (bookids == null) {
            System.out.println("Cache miss");
            // invoke the index search service
            IndexResult indexResult = idxClient.search(query_type, query);
            int index_result_num = indexResult.bookid_list_ranked_long.size();
            System.out.println(index_result_num);

            // if free search, rerank using colBERT service
            // if (query.query_type == "free") {
            //     List<Long> bookid_list_ranked_short = indexResult.bookid_list_ranked_long.subList(0, short_len);
            //     ColbertResult bertResult = bertClient.rank(bookid_list_ranked_short);
            //     Collections.copy(bertResult.bookid_list_reranked_short, indexResult.bookid_list_ranked_long);
            // }
            if (query_type.equals("phrase")) {
                System.out.println("new phrase search");
                System.out.flush();
                Long k = (long) Math.max(1000, index_result_num);
                if (k > 10000l) {
                    k = 10000l;
                }
                System.out.println(k);
                ColbertResultK bertResult = bertClient.search(query, k);
                int bert_result_num = bertResult.rank_info_books.size();
                if (index_result_num >= bert_result_num) {
                    System.out.println("index num is >= bert num");
                    System.out.println(index_result_num);
                    System.out.println(bert_result_num);
                    Collections.copy(indexResult.bookid_list_ranked_long, bertResult.rank_info_books);
                    System.out.println("result copied");
                } else {
                    indexResult.bookid_list_ranked_long = bertResult.rank_info_books;
                }
            }
            bookids = indexResult.bookid_list_ranked_long;

            cache.insert(sid, bookids);
        } else {
            System.out.println("Cache hit");
        }
        // Number of query result
        Long result_num = (long) bookids.size();

        // Check whether the requested range exceed the number of results
        if (result_range_from < result_num) {
            if (result_range_to >= result_num) {
                // the result range should not exceed the number of results
                result_range_to = result_num - 1;
            }
        } else {
            WebResult response = new WebResult(0l);
            response.result_num = result_num;
            return response;
        }

        // initialize the response
        int response_num = (int)(result_range_to - result_range_from + 1l);
        WebResult response = new WebResult(result_range_to - result_range_from + 1l);
        response.result_num = result_num;
        
        // get bookids with corresponding indexes
        List<Long> bookid_list = new ArrayList<>(response_num);
        Long shifted;
        for (Long idx = result_range_from; idx <= result_range_to; idx++) {
            shifted = idx - result_range_from;
            System.out.println("Shift index");
            bookid_list.add(shifted.intValue(), bookids.get(idx.intValue()));
        }

        // request the database
        DatabaseResult db_result = dbClient.getDocs(bookid_list);

        System.out.println("database requested");

        // insert the database result to the response accordingly
        for (Long idx = 0l; idx <= result_range_to - result_range_from; idx++) {
            response.result_list.put(
                idx, 
                db_result.bookid_result_list.get(
                    bookid_list.get(
                        idx.intValue()
                        )
                    )
                );
        }

        return response;
        
        // Long num = result_range_to - result_range_from + 1;
        // int num_books = num.intValue();
        // List<Long> bookid_list = new ArrayList<>(num_books);

        // // create a map from bookid to index
        // Map<Long, Long> idToIdx = new HashMap<>(num_books * 2);
        // int shift = result_range_from.intValue();
        
        // for (Long idx = result_range_from; idx <= result_range_to; idx++) {
        //     Long id = bookids.get(idx.intValue());
        //     bookid_list.add(idx.intValue() - shift, id);
        //     idToIdx.put(id, idx);
        // }

        // // get book information from the database, using the bookid as keys
        // DatabaseResult dbResult = dbClient.getDocs(bookid_list);

        // // convert bookid to indexes
        // WebResult webResult = new WebResult((long)bookids.size());

        // for (Long bookid: bookid_list) {
        //     Long idx = idToIdx.get(bookid);
        //     Map<Object, Object> bookInfo = dbResult.bookid_result_list.get(bookid);
        //     webResult.result_list.put(idx, bookInfo);
        // }

      	// return webResult;
    }
}
