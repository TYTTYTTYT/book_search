package ed.inf.ttds.booksearch.messageserver.messageserver.messageclient;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import ed.inf.ttds.booksearch.messageserver.messageserver.messagetype.GptResult;


@Service
public class ClientGpt {

    private RestTemplate restTemplate = new RestTemplate();

    public GptResult search(String query) {
        String url = "http://localhost:30004/colbert";
        HashMap<String, String> body = new HashMap<>();
        body.put("query", query);

        HttpEntity<Map<String, String>> entity = new HttpEntity<>(body);

        ResponseEntity<GptResult> response = this.restTemplate.postForEntity(url, entity, GptResult.class);

        // check response status code
        if (response.getStatusCode() == HttpStatus.CREATED) {
            return response.getBody();
        } else {
            return null;
        }
        
    }
}
