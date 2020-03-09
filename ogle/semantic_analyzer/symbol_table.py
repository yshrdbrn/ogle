from enum import Enum, unique


class Scope(object):
    def __init__(self):
        self.child_identifiers = {}

    def add_child(self, identifier):
        name = identifier.name
        self.child_identifiers[name] = identifier

    def get_child(self, name):
        return self.child_identifiers[name]


@unique
class IdentifierType(Enum):
    CLASS = 1
    FUNCTION = 2
    VARIABLE = 3


class Visibility(Enum):
    PUBLIC = 1
    PRIVATE = 2

    @classmethod
    def visibility_from_string(cls, input_string):
        if input_string == 'PUBLIC':
            return Visibility.PUBLIC
        elif input_string == 'PRIVATE':
            return Visibility.PRIVATE
        else:
            assert False


class Identifier(object):
    def __init__(self, name, identifier_type):
        self.name = name
        self.identifier_type = identifier_type


class Class(Identifier):
    def __init__(self, name, inherits):
        super().__init__(name, IdentifierType.CLASS)
        self.inherits = inherits
        self.scope = Scope()

    def __str__(self):
        to_ret = f'class {self.name}'
        if self.inherits:
            to_ret += f' inherits {self.inherits[0]}'
            for i in range(1, len(self.inherits)):
                to_ret += f', {self.inherits[i]}'
        return to_ret

    def __repr__(self):
        return str(self)


class Function(Identifier):
    def __init__(self, name, parameters, return_type, visibility=None):
        super().__init__(name, IdentifierType.FUNCTION)
        self.parameters = parameters
        self.return_type = return_type
        self.visibility = visibility
        self.scope = Scope()

    def __str__(self):
        to_ret = f'func {self.name}('
        if self.parameters.params:
            to_ret += str(self.parameters.params[0])
            for i in range(1, len(self.parameters.params)):
                to_ret += f', {self.parameters.params[i]}'
        to_ret += f') returns {self.return_type}'
        return to_ret

    def __repr__(self):
        return str(self)


class FunctionParameters(object):
    def __init__(self):
        self.params = []

    def add_param(self, variable):
        self.params.append(variable)


class Variable(Identifier):
    def __init__(self, name, var_type, dimensions, visibility=None):
        super().__init__(name, IdentifierType.VARIABLE)
        self.type = var_type
        self.dimensions = dimensions
        self.visibility = visibility

    def __str__(self):
        to_ret = ''
        if self.visibility:
            to_ret += f'{self.visibility} '
        to_ret += f'{self.type} {self.name}'
        for dimension in self.dimensions:
            if dimension:
                to_ret += f'[{dimension}]'
            else:
                to_ret += '[]'
        return to_ret

    def __repr__(self):
        return str(self)


class SymbolTable(object):
    def __init__(self):
        self.global_scope = Scope()


class SymbolTableVisualizer(object):
    def __init__(self, symbol_table):
        self.global_scope = symbol_table.global_scope

    def visualize(self):
        to_ret = 'Global scope:\n'
        for child in self.global_scope.child_identifiers.values():
            to_ret += f'{self._parse_table(child, 1)}\n'
        return to_ret

    def _parse_table(self, identifier, indent):
        to_ret = ''
        for i in range(indent):
            to_ret += '\t'
        to_ret += f'- {identifier}\n'
        if identifier.identifier_type != IdentifierType.VARIABLE:
            for child in identifier.scope.child_identifiers.values():
                to_ret += self._parse_table(child, indent + 1)
        return to_ret
