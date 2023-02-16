package ed.inf.ttds.booksearch.messageserver.messageserver;

import java.io.Serializable;
import java.util.Map;

public class DatabaseResult implements Serializable {
    public Map<Long, String> bookid_result_list;
}
