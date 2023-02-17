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
public class ClientDatabase {
    
    private RestTemplate restTemplate = new RestTemplate();

    public DatabaseResult getDocs(List<Long> docids) {
        String url = "http://localhost:30001/database";
        HashMap<String, List<Long>> body = new HashMap<>();
        body.put("bookid_list", docids);

        HttpEntity<Map<String, List<Long>>> entity = new HttpEntity<>(body);

        ResponseEntity<DatabaseResult> response = this.restTemplate.postForEntity(url, entity, DatabaseResult.class);

        // check response status code
        if (response.getStatusCode() == HttpStatus.CREATED) {
            return response.getBody();
        } else {
            return null;
        }
    }
}
