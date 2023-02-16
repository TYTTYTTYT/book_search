package ed.inf.ttds.booksearch.messageserver.messageserver;
import java.util.Arrays;
import java.util.List;

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

    public static void main(String[] args) {
      	SpringApplication.run(MessageserverApplication.class, args);
    }
    @GetMapping("/search")
    public String search(@RequestBody WebQuery query) {
        String sid = query.uid.toString() + query.query_type + query.query;
        List<Long> docids = cache.get(sid);
        if (docids == null) {
            // System.out.println("new sid: " + sid);
            Long[] numbers = new Long[] {1l, 2l, 3l};
            List<Long> fake_result = Arrays.asList(numbers);
            docids = fake_result;
            cache.insert(sid, docids);
        }
      	return String.format("Hello %s!", query.query);
    }
}
