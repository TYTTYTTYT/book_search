from typing import Any, Optional
from pathlib import Path
import os
import pickle
from collections import deque


DATAPATH = os.path.join(Path.home(), '.cache', 'cache_dict')

class Node(object):
    def __init__(self, id: Any, value: Any, cache_path: str) -> None:
        self.id = id
        self.value = value
        self.next = None
        self.prev = None
        self.in_memory = True
        self.path = os.path.join(cache_path, str(hash(id)))
        
    def offLoad(self) -> None:
        with open(self.path, 'wb') as fout:
            pickle.dump(self.value, fout)
        del self.value
        self.value = None
        self.in_memory = False
    
    def load(self) -> None:
        with open(self.path, 'rb') as fin:
            self.value = pickle.load(fin)  
        self.in_memory = True

class CacheDict(object):
    def __init__(self, capacity: int=1000, cache_path: str=DATAPATH, data: Optional[dict]=None) -> None:
        self.cache_path = cache_path
        self.node_path = os.path.join(cache_path, 'nodes')
        os.makedirs(self.node_path, exist_ok=True)
        self.head = Node('head', None, self.node_path)
        self.tail = Node('tail', None, self.node_path)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.count = 0
        self.id2node = dict()
        self.capacity = capacity
        if data:
            keys = list(data.keys())
            for k in keys:
                v = data.pop(k)
                self.__setitem__(k, v)
            del data
    
    def __setitem__(self, id: Any, value: Any) -> None:
        if id in self.id2node:
            raise KeyError(f'Node<{id}> already added!')
        new_node = Node(id, value, self.node_path)
        self.id2node[id] = new_node
        self.__insert_node(new_node)
            
    def __insert_node(self, node: Node) -> None:
        pre_first = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = pre_first
        pre_first.prev = node
        self.count += 1
        if self.count > self.capacity:
            self.__pop()
            
    def __pop(self) -> None:
        last = self.tail.prev
        new_last = last.prev
        last.offLoad()
        last.prev = None
        last.next = None
        new_last.next = self.tail
        self.tail.prev = new_last
        self.count -= 1
                
    def __get_node(self, id: Any) -> Node:
        node = self.id2node[id]
        if node.in_memory:
            pre = node.prev
            nex = node.next
            pre.next = nex
            nex.prev = pre
            self.count -= 1
        else:
            node.load()
        
        return node
                
    def __getitem__(self, id: Any) -> Any:
        if id not in self.id2node:
            raise KeyError(f'id<{id}> does not exist')
        node = self.__get_node(id)
        self.__insert_node(node)
        return node.value
    
    def __contains__(self, id: Any) -> bool:
        return id in self.id2node
    
    def save(self) -> None:
        in_cache_ids = deque()
        current_node = self.head.next
        while current_node.id != 'tail':
            in_cache_ids.append(current_node.id)
            current_node = current_node.next
        while self.count > 0:
            self.__pop()
        

        with open(os.path.join(self.cache_path, 'meta.db'), 'wb') as fout:
            pickle.dump((self.id2node, in_cache_ids, self.capacity), fout)
    
    def load(self) -> None:
        with open(os.path.join(self.cache_path, 'meta.db'), 'rb') as fin:
            self.id2node, in_cache_ids, self.capacity = pickle.load(fin)
        in_cache_ids.reverse()
        for id in in_cache_ids:
            self.__getitem__(id)

if __name__ == '__main__':
    from tqdm import tqdm
    print('inserting the data')
    d = CacheDict(10000, 'data/test')
    for i in tqdm(range(50000)):
        d[i] = str(i)
    ids = list(range(50000))
    ids.reverse()
    print('testing the data')
    for i in tqdm(ids):
        assert d[i] == str(i), f'd:{d[i]}, {i}'
        
    d.save()
    dd = CacheDict(10000, 'data/test')
    dd.load()
    print('testing the recorvered data')
    for i in tqdm(ids[:10000]):
        assert dd[i] == str(i), f'd:{dd[i]}, {i}'
        
    print('this run should be faster with cached data')
    for i in tqdm(ids[:10000]):
        assert dd[i] == str(i), f'd:{dd[i]}, {i}'
        
    print('test load dict')
    d = dict()
    for k in range(50000):
        d[k] = k + 50000
    
    cd = CacheDict(10000, 'data/test', d)
    for k in tqdm(range(40000, 50000)):
        assert cd[k] == k + 50000
        
    for k in tqdm(range(0, 10000)):
        assert cd[k] == k + 50000
    
    