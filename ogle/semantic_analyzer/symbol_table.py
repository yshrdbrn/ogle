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


class Function(Identifier):
    def __init__(self, name, parameters, return_type, visibility=None):
        super().__init__(name, IdentifierType.FUNCTION)
        self.parameters = parameters
        self.return_type = return_type
        self.visibility = visibility
        self.scope = Scope()


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


class SymbolTable(object):
    def __init__(self):
        self.global_scope = Scope()
