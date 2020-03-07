from collections import deque
from enum import Enum, unique, auto


@unique
class NodeType(Enum):
    GENERAL = auto()

    ARRAY_DIMENSIONS = auto()
    CLASS_DECLARATION = auto()
    FUNCTION_BODY = auto()
    FUNCTION_DECLARATION = auto()
    FUNCTION_DEFINITION = auto()
    FUNCTION_PARAMETERS = auto()
    INHERITS = auto()
    LOCAL_SCOPE = auto()
    PROGRAM = auto()
    VARIABLE_DECLARATION = auto()


class Node(object):
    counter = 1

    def __init__(self, name, value=None):
        self.name = name
        self.node_type = node_name_to_type[name] if name in node_name_to_type else NodeType.GENERAL
        self.value = value if value else name
        self.children = deque()
        self.unique_id = str(Node.counter)
        Node.counter += 1

    def make_right_child(self, other):
        self.children.append(other)

    def make_left_child(self, other):
        self.children.appendleft(other)

    def adopt_children_right(self, other):
        for child in other.children:
            self.children.append(child)

    def adopt_children_left(self, other):
        for child in reversed(other.children):
            self.children.appendleft(child)

    def __str__(self):
        return 'Node({})'.format(self.name)

    def __repr__(self):
        return str(self)


node_name_to_type = {
    'ARRAY_DIMENSIONS': NodeType.ARRAY_DIMENSIONS,
    'class': NodeType.CLASS_DECLARATION,
    'FUNCTION_BODY': NodeType.FUNCTION_BODY,
    'FUNCTION_DECLARATION': NodeType.FUNCTION_DECLARATION,
    'FUNCTION_DEFINITION': NodeType.FUNCTION_DEFINITION,
    'FUNCTION_PARAMS': NodeType.FUNCTION_PARAMETERS,
    'LOCAL_SCOPE': NodeType.LOCAL_SCOPE,
    'OPTIONAL_INHERITS': NodeType.INHERITS,
    'PROGRAM': NodeType.PROGRAM,
    'VARIABLE_DECLARATION': NodeType.VARIABLE_DECLARATION
}
