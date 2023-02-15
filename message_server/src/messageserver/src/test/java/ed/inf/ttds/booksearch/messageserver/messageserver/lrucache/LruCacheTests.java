package ed.inf.ttds.booksearch.messageserver.messageserver.lrucache;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.concurrent.TimeUnit;

import org.junit.jupiter.api.Assertions;

public class LruCacheTests {
    @Test
    @Timeout(value = 30, unit = TimeUnit.MILLISECONDS)
    public void testInsert() {
        LruCache<Integer, Integer> cache = new LruCache<Integer, Integer>(1000);
        for (int i = 0; i < 1000; i++) {
            Integer key = i;
            Integer value = i + 1;
            cache.insert(key, value);
        }
        for (int i = 0; i < 1000; i++) {
            Integer key = i;
            Integer value = cache.get(key);
            Integer expected = key + 1;
            Assertions.assertEquals(expected, value);
        }
    }

    @Test
    @Timeout(value = 100, unit = TimeUnit.MILLISECONDS)
    public void testDrop() {
        LruCache<Integer, Integer> cache = new LruCache<Integer, Integer>(1000);
        for (int i = 0; i < 1000; i++) {
            Integer key = i;
            Integer value = i + 1;
            cache.insert(key, value);
        }
        for (int i = 999; i >= 0; i--) {
            Integer key = i;
            Integer value = cache.get(key);
            Integer expected = key + 1;
            Assertions.assertEquals(expected, value);
        }
        for (Integer k = 1000; k < 1999; k++) {
            cache.insert(k, k);
        }
        Integer expected = 1;
        Integer key = 0;
        Assertions.assertEquals(expected, cache.get(key));
        System.out.println(cache.get(key));
        for (Integer k = 1; k < 1000; k++) {
            Assertions.assertEquals(null, cache.get(k));
        }
    }
}
