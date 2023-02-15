package ed.inf.ttds.booksearch.messageserver.messageserver;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import ed.inf.ttds.booksearch.messageserver.messageserver.lrucache.LinkedList;

@SpringBootApplication
@RestController
public class MessageserverApplication {
    public static void main(String[] args) {
      	SpringApplication.run(MessageserverApplication.class, args);
    }
    @GetMapping("/hello")
    public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {
		LinkedList<String> l = new LinkedList<String>();
		l.insertHead("name");
		l.insertHead("is");
		System.out.println(l.head.next.value);
		l.dropTail();
		System.out.println(l.count);
      	return String.format("Hello %s!", name);
    }
}