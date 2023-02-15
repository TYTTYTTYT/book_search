package ed.inf.ttds.booksearch.messageserver.messageserver.lrucache;

public class LruNode<K, V> {
    public K key;
    public V value;

    public LruNode(K key, V value) {
        this.key = key;
        this.value = value;
    }
}
