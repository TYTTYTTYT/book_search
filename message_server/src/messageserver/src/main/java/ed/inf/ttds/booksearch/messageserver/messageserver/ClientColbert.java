package ed.inf.ttds.booksearch.messageserver.messageserver;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ClientColbert {

    private RestTemplate restTemplate = new RestTemplate();

    public ColbertResult rank(List<Long> bookid_list_ranked_short) {
        String url = "http://localhost:30003/colbert";
        HashMap<String, List<Long>> body = new HashMap<>();
        body.put("bookid_list_ranked_short", bookid_list_ranked_short);

        HttpEntity<Map<String, List<Long>>> entity = new HttpEntity<>(body);

        ResponseEntity<ColbertResult> response = this.restTemplate.postForEntity(url, entity, ColbertResult.class);

        // check response status code
        if (response.getStatusCode() == HttpStatus.CREATED) {
            return response.getBody();
        } else {
            return null;
        }
    }
}
