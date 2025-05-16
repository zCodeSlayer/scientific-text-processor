from dataclasses import dataclass, field

from term import Term


@dataclass
class Node:
    term: Term
    links: list["Link"] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.term)


@dataclass
class Link:
    next_node: "Node"
    weight: float = 0.0


class SemanticGraph:
    def __init__(self) -> None:
        self.__nodes: dict[int, Node] = {}

    def add_node(self, node: Node) -> None:
        self.__nodes[hash(node)] = node

    def get_node_by_hash(self, node_hash: int) -> Node | None:
        return self.__nodes.get(node_hash)

    def add_link(self, node: Node, next_node: Node, weight: float) -> None:
        ex_message: str = "Node with term {node} not included in graph"
        if self.__nodes.get(hash(node)) is None:
            raise Exception(ex_message.format(node=node.term.title))
        if self.__nodes.get(hash(next_node)) is None:
            raise Exception(ex_message.format(node=next_node.term.title))

        link: Link = Link(next_node, weight)
        self.__nodes.get(hash(node)).links.append(link)
