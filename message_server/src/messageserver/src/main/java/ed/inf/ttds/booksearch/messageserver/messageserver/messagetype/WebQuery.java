package ed.inf.ttds.booksearch.messageserver.messageserver.messagetype;

import java.util.List;

public class WebQuery {
    public Long uid;
    public String query_type;
    public String query;
    public List<Long> result_range;
}
