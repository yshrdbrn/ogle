from collections import deque
from graphviz import Digraph


terminal_nodes = [
    # Reserved words
    'if',
    'while',
    'class',
    'integer',
    'float',
    'public',
    'private',
    'or',
    'and',
    'not',
    'read',
    'write',
    'return',
    'main',
    'inherits',
    'void',

    'id',
    'intnum',
    'floatnum',
    
    'plus',
    'minus',
    'mult',
    'div',
    'equal',
    'less',
    'greater',

    'eq',
    'lesseq',
    'greatereq',
    'noteq'
]


class Node(object):
    counter = 1

    def __init__(self, name):
        self.name = name
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


class AST(object):
    def __init__(self):
        self.root = None
        self.stack = deque()
        self.ignore_input = False

    def make_node(self, name):
        if self.ignore_input:
            return
        self.stack.append(Node(name))

    def perform_operation(self, operation, lhs_name):
        if self.ignore_input:
            return

        operation_number = int(operation[1])
        if operation_number == 1:
            self.make_node(lhs_name if '(' not in operation else operation[3:-1])
        elif operation_number == 2:
            self._make_right_child()
        elif operation_number == 3:
            self._make_left_child()
        elif operation_number == 4:
            self._adopt_right_children()
        elif operation_number == 5:
            self._group_together()
        elif operation_number == 6:
            self._delete_top()
        elif operation_number == 7:
            self._replace_node_with_child()
        else:
            raise ValueError

    def finish_building(self):
        self.root = self.stack[0]
        self.ignore_input = True

    # Pop X & Y, make Y right child of X, push X
    def _make_right_child(self):
        y = self.stack.pop()
        x = self.stack.pop()
        x.make_right_child(y)
        self.stack.append(x)

    # Pop X & Y, make X left child of Y, push Y
    def _make_left_child(self):
        y = self.stack.pop()
        x = self.stack.pop()
        y.make_left_child(x)
        self.stack.append(y)

    # Pop X & Y, X adopts Y's children, push X
    def _adopt_right_children(self):
        y = self.stack.pop()
        x = self.stack.pop()
        x.adopt_children_right(y)
        self.stack.append(x)

    # Group all the Xs on top the stack with the same name under one Z
    def _group_together(self):
        x = self.stack.pop()
        parent = Node(x.name + '_list')
        parent.children.appendleft(x)
        while self.stack[-1].name == x.name:
            x = self.stack.pop()
            parent.children.appendleft(x)
        self.stack.append(parent)

    def _delete_top(self):
        self.stack.pop()

    # if X has only one child, replace it with the child
    def _replace_node_with_child(self):
        x = self.stack.pop()
        if len(x.children) == 1:
            x = x.children[0]
        self.stack.append(x)


class ASTVisualizer(object):
    def __init__(self, ast):
        self.ast = ast
        self.dot = Digraph(name='AST', comment='Abstract Syntax Tree')

    def visualize(self, input_file_name):
        root = self.ast.root
        self._add_nodes(root)
        self._add_edges(root)
        self.dot.render(filename=input_file_name + '_AST.gv')

    def _add_nodes(self, root):
        self.dot.node(root.unique_id, root.name)
        for child in root.children:
            self._add_nodes(child)

    def _add_edges(self, root):
        for child in root.children:
            self.dot.edge(root.unique_id, child.unique_id)
            self._add_edges(child)
