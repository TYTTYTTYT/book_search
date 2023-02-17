package ed.inf.ttds.booksearch.messageserver.messageserver.messageclient;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.IndexResult;

@Service
public class ClientIndex {

    private RestTemplate restTemplate = new RestTemplate();

    public IndexResult search(String query_type, String query) {
        String url = "http://localhost:30002/index";
        HashMap<String, String> body = new HashMap<>();
        body.put("query_type", query_type);
        body.put("query", query);

        HttpEntity<Map<String, String>> entity = new HttpEntity<>(body);

        ResponseEntity<IndexResult> response = this.restTemplate.postForEntity(url, entity, IndexResult.class);

        // check response status code
        if (response.getStatusCode() == HttpStatus.CREATED) {
            return response.getBody();
        } else {
            return null;
        }
    }
}
