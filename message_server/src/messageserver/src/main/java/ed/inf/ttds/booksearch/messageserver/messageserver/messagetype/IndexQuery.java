package ed.inf.ttds.booksearch.messageserver.messageserver.messagetype;

public class IndexQuery {
    public String query_type;
    public String query;

    public IndexQuery(String query_type, String query) {
        this.query_type = query_type;
        this.query = query;
    }
}
