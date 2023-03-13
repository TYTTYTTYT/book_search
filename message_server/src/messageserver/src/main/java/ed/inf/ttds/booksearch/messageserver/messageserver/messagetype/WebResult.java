package ed.inf.ttds.booksearch.messageserver.messageserver.messagetype;

import java.util.HashMap;
import java.util.Map;

public class WebResult {
    public Map<Long, Map<Object, Object>> result_list;
    public Long result_num;
    public String error_message;
    public Double time;

    public WebResult(Long result_num) {
        result_list = new HashMap<>(result_num.intValue());
    }
}
