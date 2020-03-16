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
    MAIN = auto()
    PROGRAM = auto()
    TYPE = auto()
    VARIABLE_DECLARATION = auto()


class Node(object):
    counter = 1

    def __init__(self, name, value=None, location=None):
        self.name = name
        self.node_type = node_name_to_type[name] if name in node_name_to_type else NodeType.GENERAL
        self.value = value if value else name
        self.location = location
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
    'CLASS': NodeType.CLASS_DECLARATION,
    'function': NodeType.FUNCTION_DEFINITION,
    'FUNCTION_BODY': NodeType.FUNCTION_BODY,
    'FUNCTION_DECLARATION': NodeType.FUNCTION_DECLARATION,
    'FUNCTION_PARAMS': NodeType.FUNCTION_PARAMETERS,
    'LOCAL_SCOPE': NodeType.LOCAL_SCOPE,
    'MAIN': NodeType.MAIN,
    'OPTIONAL_INHERITS': NodeType.INHERITS,
    'PROGRAM': NodeType.PROGRAM,
    'TYPE': NodeType.TYPE,
    'VARIABLE_DECLARATION': NodeType.VARIABLE_DECLARATION
}
