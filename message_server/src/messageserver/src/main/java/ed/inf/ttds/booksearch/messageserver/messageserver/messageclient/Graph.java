package ed.inf.ttds.booksearch.messageserver.messageserver.messageclient;
import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.GraphResult;
import java.lang.Integer;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;


@Service
public class Graph {

    private RestTemplate restTemplate = new RestTemplate();

    public GraphResult search(Long bookid, Long neighbor) {
        String url = "http://localhost:30004/graph";
        HashMap<String, Long> body = new HashMap<>();
        body.put("bookid", bookid);
        body.put("neighbor", neighbor);

        HttpEntity<Map<String, Long>> entity = new HttpEntity<>(body);

        ResponseEntity<GraphResult> response = this.restTemplate.postForEntity(url, entity, GraphResult.class);

        // check response status code
        if (response.getStatusCode() == HttpStatus.CREATED) {
            return response.getBody();
        } else {
            return null;
        }
    }
    
}