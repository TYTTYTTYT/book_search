from typing import NoReturn, Any
from collections import deque

class Node(object):
    def __init__(self, id: Any, value: Any) -> NoReturn:
        self.id = id
        self.neighbors = deque()
        self.value = value

class Graph(object):
    def __init__(self) -> None:
        self.__id2nodes = dict()
        
    def add_node(self, id: Any, value: Any) -> None:
        if id in self.__id2nodes:
            raise KeyError(f'Node<{id}> is already existing!')
        self.__id2nodes[id] = Node(id, value)
    
    def add_edge(self, id_from: Any, id_to: Any) -> None:
        if id_from not in self.__id2nodes or id_to not in self.__id2nodes:
            raise KeyError(f'Node<{id_from}> or Node<{id_to}> does not exist!')
        self.__id2nodes[id_from].neighbors.append(self.__id2nodes[id_to])
    
    def get_neighbor_graph(self, id: Any, layers: int) -> tuple[list[Any], list[tuple[Any, Any]]]:
        if id not in self.__id2nodes:
            raise KeyError(f'Id<{id}> not exist')
        
        nodes = set([id])
        edges = set()
        current_nodes = [self.__id2nodes[id]]
        
        for l in range(layers):
            new_current_nodes = set()
            for node in current_nodes:
                for nei in node.neighbors:
                    new_current_nodes.add(nei)
                    nodes.add(nei.id)
                    edges.add((node.id, nei.id))
            current_nodes = list(new_current_nodes)
        
        return list(nodes), list(edges)
        