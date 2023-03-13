package ed.inf.ttds.booksearch.messageserver.messageserver.messagetype;
import java.util.List;
import java.util.Map;

public class GraphResult {
    public List<Long> nodes;
    public List<Map<String, Long>> links;
    public String error_message;
}
