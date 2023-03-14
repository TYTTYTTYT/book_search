from typing import NoReturn, Any
import logging
from index_server.cache_dict.cache_dict import CacheDict

FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
logging.basicConfig(encoding='utf-8', level=logging.INFO, format=FORMAT)
logger = logging.getLogger('Graph')


class Graph(object):
    def __init__(self, index_path: str) -> None:
        self.__id2nodes = CacheDict(100000, index_path)
        
    def load(self) -> None:
        self.__id2nodes.load()
        
    def save(self) -> None:
        self.__id2nodes.save()
        
    def add_node(self, id: Any, value: Any) -> None:
        if id in self.__id2nodes:
            raise KeyError(f'Node<{id}> is already existing!')
        self.__id2nodes[id] = (value, [])
    
    def add_edge(self, id_from: Any, id_to: Any) -> None:
        if id_from not in self.__id2nodes or id_to not in self.__id2nodes:
            raise KeyError(f'Node<{id_from}> or Node<{id_to}> does not exist!')
        self.__id2nodes[id_from][1].append(id_to)
    
    def get_neighbor_graph(self, id: Any, layers: int, max_neighbor: int=5) -> tuple[list[Any], list[tuple[Any, Any]]]:
        if id not in self.__id2nodes:
            raise KeyError(f'Id<{id}> not exist')
        title = self.__id2nodes[id][0]
        nodes = set([(id, title)])
        edges = set()
        current_nodes = self.__id2nodes[id][1]
        
        for _ in range(layers):
            new_current_nodes = set()
            for node in current_nodes[:max_neighbor]:
                for nei in self.__id2nodes[node][1][:max_neighbor]:
                    new_current_nodes.add(nei)
                    nei_title = self.__id2nodes[nei][0]
                    nodes.add((nei, nei_title))
                    edges.add((node, nei))
            current_nodes = list(new_current_nodes)
        
        return list(nodes), list(edges)
    
    def __contains__(self, id: Any) -> bool:
        return id in self.__id2nodes
    
    def __getitem__(self, id: Any) -> Any:
        return self.__id2nodes[id]
    
    def __setitem__(self, id: Any, value: Any) -> None:
        if id in self.__id2nodes:
            self.__id2nodes[id] = (value, self.__id2nodes[id][1])
        else:
            self.__id2nodes[id] = (value, [])
