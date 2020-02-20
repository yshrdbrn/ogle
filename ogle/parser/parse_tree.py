class ParseNode(object):
    def __init__(self, name):
        self.name = name
        self.children = []
        # Flag is True when the state resolves to epsilon.
        # We don't need to show it in the derivation
        self.deleted = False

    def add_child(self, child):
        self.children.append(child)


class ParseTree(object):
    def __init__(self, root_name):
        self.root = ParseNode(root_name)
        self.derivation_list = []

    def add_derivation(self):
        self.derivation_list.append(self.obtain_derivation(self.root))

    def obtain_derivation(self, node):
        if node.deleted:
            return ''
        if not node.children:
            return node.name + ' '

        to_ret = ''
        for child in node.children:
            to_ret += self.obtain_derivation(child)
        return to_ret
