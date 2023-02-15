package ed.inf.ttds.booksearch.messageserver.messageserver.lrucache;

public class Node<T>  {

    public Node<T> previous;
    public Node<T> next;
    public T value;

    public Node(Node<T> previous, Node<T> next, T value) {
        this.previous = previous;
        this.next = next;
        this.value = value;
    }

    public Node(T value) {
        this.value = value;
    }
}