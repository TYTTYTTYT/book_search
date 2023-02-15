package ed.inf.ttds.booksearch.messageserver.messageserver.lrucache;

public class LinkedList<T> {
    public int count;
    public Node<T> head;
    public Node<T> tail;

    public LinkedList(){
        head = new Node<T>(null);
        tail = new Node<T>(null);
        head.next = tail;
        tail.next = head;
    };

    public void insertHead(T value) {
        Node<T> n = new Node<T>(head, head.next, value);
        head.next.previous = n;
        head.next = n;
        count += 1;
    }

    public void insertTail(T value) {
        Node<T> n = new Node<T>(tail.previous, tail, value);
        tail.previous.next = n;
        tail.previous = n;
        count += 1;
    }

    public Node<T> dropHead() {
        if (count <= 0) {
            return null;
        }
        Node<T> dropped = head.next;
        dropped.next.previous = head;
        head.next = dropped.next;
        count -= 1;
        return dropped;
    }

    public Node<T> dropTail() {
        if (count <= 0) {
            return null;
        }
        Node<T> dropped = tail.previous;
        dropped.previous.next = tail;
        tail.previous = dropped.previous;
        count -= 1;
        return dropped;
    }

    public void moveToHead(Node<T> node) {
        node.next.previous = node.previous;
        node.previous.next = node.next;

        head.next.previous = node;
        node.next = head.next;

        head.next = node;
        node.previous = head;
    }
}
