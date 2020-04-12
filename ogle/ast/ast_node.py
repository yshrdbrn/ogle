from collections import deque
from enum import Enum, unique, auto


@unique
class NodeType(Enum):
    GENERAL = auto()

    ADD_OPERATOR = auto()
    ARRAY_DIMENSIONS = auto()
    ASSIGN_STATEMENT = auto()
    CLASS_DECLARATION = auto()
    COMPARE_OPERATOR = auto()
    FLOAT_NUM = auto()
    FUNCTION_BODY = auto()
    FUNCTION_CALL = auto()
    FUNCTION_CALL_PARAMETERS = auto()
    FUNCTION_DECLARATION = auto()
    FUNCTION_DEFINITION = auto()
    FUNCTION_PARAMETERS = auto()
    IF_STATEMENT = auto()
    INDICES = auto()
    INHERITS = auto()
    INT_NUM = auto()
    ITEM = auto()
    ITEM_LIST = auto()
    LOCAL_SCOPE = auto()
    MAIN = auto()
    MULT_OPERATOR = auto()
    NOT_OPERATOR = auto()
    PROGRAM = auto()
    READ_STATEMENT = auto()
    RETURN_STATEMENT = auto()
    SIGN_OPERATOR = auto()
    STATEMENTS = auto()
    TYPE = auto()
    VARIABLE_DECLARATION = auto()
    WHILE_STATEMENT = auto()
    WRITE_STATEMENT = auto()


class Node(object):
    counter = 1

    def __init__(self, name, value=None, location=None):
        self.name = name
        self.node_type = node_name_to_type[name] if name in node_name_to_type else NodeType.GENERAL
        self.value = value if value else name
        self.location = location
        self.children = deque()
        self.identifier = None
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
    'FLOATNUM': NodeType.FLOAT_NUM,
    'function': NodeType.FUNCTION_DEFINITION,
    'FUNCTION_BODY': NodeType.FUNCTION_BODY,
    'FUNCTION_CALL_PARAMS': NodeType.FUNCTION_CALL_PARAMETERS,
    'FUNCTION_DECLARATION': NodeType.FUNCTION_DECLARATION,
    'FUNCTION_PARAMS': NodeType.FUNCTION_PARAMETERS,
    'func_call': NodeType.FUNCTION_CALL,
    'IF': NodeType.IF_STATEMENT,
    'INDICES': NodeType.INDICES,
    'INTNUM': NodeType.INT_NUM,
    'item': NodeType.ITEM,
    'item_list': NodeType.ITEM_LIST,
    'LOCAL_SCOPE': NodeType.LOCAL_SCOPE,
    'MAIN': NodeType.MAIN,
    'NOT': NodeType.NOT_OPERATOR,
    'OPTIONAL_INHERITS': NodeType.INHERITS,
    'PROGRAM': NodeType.PROGRAM,
    'READ': NodeType.READ_STATEMENT,
    'RETURN': NodeType.RETURN_STATEMENT,
    'SIGN': NodeType.SIGN_OPERATOR,
    'STATEMENT_BLOCK': NodeType.STATEMENTS,
    'STATEMENTS': NodeType.STATEMENTS,
    'TYPE': NodeType.TYPE,
    'VARIABLE_DECLARATION': NodeType.VARIABLE_DECLARATION,
    'WHILE': NodeType.WHILE_STATEMENT,
    'WRITE': NodeType.WRITE_STATEMENT,

    '=': NodeType.ASSIGN_STATEMENT,

    '==': NodeType.COMPARE_OPERATOR,
    '<=': NodeType.COMPARE_OPERATOR,
    '>=': NodeType.COMPARE_OPERATOR,
    '<>': NodeType.COMPARE_OPERATOR,
    '>': NodeType.COMPARE_OPERATOR,
    '<': NodeType.COMPARE_OPERATOR,

    '+': NodeType.ADD_OPERATOR,
    '-': NodeType.ADD_OPERATOR,
    'OR': NodeType.ADD_OPERATOR,

    '*': NodeType.MULT_OPERATOR,
    '/': NodeType.MULT_OPERATOR,
    'AND': NodeType.MULT_OPERATOR
}
