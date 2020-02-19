from collections import deque


class Node(object):
    def __init__(self, name):
        self.name = name
        self.children = deque()

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
            self.make_node(lhs_name if '#' not in operation else operation[2:-1])
        elif operation_number == 2:
            self._make_right_child()
        elif operation_number == 3:
            self._make_left_child()
        elif operation_number == 4:
            self._adopt_right_children()
        elif operation_number == 5:
            self._adopt_left_children()
        elif operation_number == 6:
            self._adopt_multiple_left_children(operation[2:-1])
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

    # Pop X & Y, Y adopts X's children, push Y
    def _adopt_left_children(self):
        y = self.stack.pop()
        x = self.stack.pop()
        y.adopt_children_left(x)
        self.stack.append(y)

    # Merge all Xs' children out of stack as long as Xs' have the name 'name'
    def _adopt_multiple_left_children(self, name):
        x = self.stack.pop()
        while self.stack[-1].name == name:
            x.adopt_children_left(self.stack[-1])
            self.stack.pop()
