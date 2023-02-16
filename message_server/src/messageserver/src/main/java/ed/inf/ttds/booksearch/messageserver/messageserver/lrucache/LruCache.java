package ed.inf.ttds.booksearch.messageserver.messageserver.lrucache;

import java.util.HashMap;

public class LruCache<K, V> {
    private int size;
    private LinkedList<LruNode<K, V>> list;
    private HashMap<K, Node<LruNode<K, V>>> map;

    public LruCache() {
        this.size = 1000;
        list = new LinkedList<LruNode<K, V>>();
        map = new HashMap<K, Node<LruNode<K, V>>>(size);
    }

    public LruCache(int size) {
        this.size = size;
        list = new LinkedList<LruNode<K, V>>();
        map = new HashMap<K, Node<LruNode<K, V>>>(size);
    }

    public void insert(K key, V value) {
        LruNode<K, V> n = new LruNode<K, V>(key, value);
        list.insertHead(n);
        map.put(key, list.head.next);
        if (list.count() > size) {
            Node<LruNode<K, V>> dropped = list.dropTail();
            map.remove(dropped.value.key);
        }
    }

    public V get(K key) {
        Node<LruNode<K, V>> n = map.get(key);
        if (n == null) {
            return null;
        }
        list.moveToHead(n);
        return n.value.value;
    }

    public int getSize() {
        return size;
    }
}
