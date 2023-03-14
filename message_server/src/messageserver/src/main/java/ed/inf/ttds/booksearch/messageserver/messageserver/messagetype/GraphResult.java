package ed.inf.ttds.booksearch.messageserver.messageserver.messagetype;
import java.util.List;
import java.util.Map;

public class GraphResult {
    public List<Map<String, String>> nodes;
    public List<Map<String, String>> links;
    public String error_message;
    public Double time;
}
