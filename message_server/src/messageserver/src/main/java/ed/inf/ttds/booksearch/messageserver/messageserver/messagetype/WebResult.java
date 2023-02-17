package ed.inf.ttds.booksearch.messageserver.messageserver.messagetype;

import java.util.HashMap;
import java.util.Map;

public class WebResult {
    public Map<Long, String> result_list;
    public Long result_num;

    public WebResult(Long result_num) {
        result_list = new HashMap<>(result_num.intValue());
        this.result_num = result_num;
    }
}
