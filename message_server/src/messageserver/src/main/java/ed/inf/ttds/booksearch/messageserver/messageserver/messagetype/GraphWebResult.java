package ed.inf.ttds.booksearch.messageserver.messageserver.messagetype;
import java.util.List;
import java.util.Map;

public class GraphWebResult {
    public List<Map<String, String>> nodes;
    public List<Map<String, Long>> links;
    public String error_message;
}
