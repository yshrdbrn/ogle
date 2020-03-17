from enum import Enum, unique
from ogle.semantic_analyzer.semantic_errors import *

class Scope(object):
    def __init__(self, identifier=None):
        self.child_identifiers = []
        self.identifier = identifier

    def add_child(self, identifier):
        name = identifier.name
        found = self._find_child(name)
        if not found:
            self.child_identifiers.append(identifier)
        else:
            is_overload = Function.is_overload(identifier, found)
            if is_overload:
                self.child_identifiers.append(identifier)
            raise DuplicateIdentifierError(identifier, is_overload)

    def remove_child(self, identifier):
        self.child_identifiers.remove(identifier)

    def get_child_by_name(self, name):
        found = self._find_child(name)
        if found:
            return found
        raise IdentifierNotFoundError(requested_string=name)

    def get_child_by_identifier(self, identifier):
        for child in self.child_identifiers:
            if child == identifier:
                return child
        if identifier.identifier_type == IdentifierType.FUNCTION:
            raise FunctionNotFoundError
        raise IdentifierNotFoundError

    def _find_child(self, name):
        for child in self.child_identifiers:
            if child.name == name:
                return child
        return None

    def get_classes(self):
        return self._get_identifier_type(IdentifierType.CLASS)

    def get_functions(self):
        return self._get_identifier_type(IdentifierType.FUNCTION)

    def get_variables(self):
        return self._get_identifier_type(IdentifierType.VARIABLE)

    def _get_identifier_type(self, identifier_type):
        return [child for child in self.child_identifiers if child.identifier_type == identifier_type]


@unique
class Type(Enum):
    VOID = 1
    INTEGER = 2
    FLOAT = 3
    ID = 4


@unique
class IdentifierType(Enum):
    CLASS = 1
    FUNCTION = 2
    VARIABLE = 3


@unique
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

    def __str__(self):
        return self.name.lower()


class Identifier(object):
    def __init__(self, name, identifier_type, location):
        self.name = name
        self.identifier_type = identifier_type
        self.location = location


class Class(Identifier):
    def __init__(self, name, inherits, location):
        super().__init__(name, IdentifierType.CLASS, location)
        self.inherits = inherits
        self.scope = Scope(self)

    def __str__(self):
        to_ret = f'class {self.name}'
        if self.inherits:
            to_ret += f' inherits {self.inherits[0]}'
            for i in range(1, len(self.inherits)):
                to_ret += f', {self.inherits[i]}'
        return to_ret

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Class):
            return self.name == other.name
        return False


class TypeValue(object):
    def __init__(self, _type, value=None):
        self.type = _type
        self.value = value

    def __str__(self):
        if self.value:
            return self.value
        else:
            return self.type.name.lower()

    def __eq__(self, other):
        if isinstance(other, TypeValue):
            return self.type == other.type and self.value == other.value
        return False

    @classmethod
    def type_from_string(cls, type_str):
        val = None
        if type_str == 'void':
            t = Type.VOID
        elif type_str == 'float':
            t = Type.FLOAT
        elif type_str == 'integer':
            t = Type.INTEGER
        else:
            t = Type.ID
            val = type_str
        return TypeValue(t, val)


class Function(Identifier):
    def __init__(self, name, parameters, return_type, location, visibility=None, is_defined=False):
        super().__init__(name, IdentifierType.FUNCTION, location)
        self.parameters = parameters
        self.return_type = return_type
        self.visibility = visibility
        self.scope = Scope(self)
        self.is_defined = is_defined

    def __str__(self):
        to_ret = ''
        if self.visibility:
            to_ret += f'{self.visibility} '
        to_ret += f'func {self.name}({self.parameters}) returns {self.return_type}'
        return to_ret

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Function):
            return self.name == other.name and self.parameters == other.parameters
        return False

    @classmethod
    def is_overload(cls, func1, func2):
        if isinstance(func1, Function) and isinstance(func2, Function):
            return func1.name == func2.name and func1.parameters != func2.parameters
        return False


class FunctionParameters(object):
    def __init__(self):
        self.params = []

    def add_param(self, variable):
        self.params.append(variable)

    def __str__(self):
        def dimensions(dims):
            dims_out = ''
            for dim in dims:
                if dim:
                    dims_out += f'[{dim}]'
                else:
                    dims_out += '[]'
            return dims_out

        to_ret = ''
        if self.params:
            to_ret += f'{self.params[0].type}{dimensions(self.params[0].dimensions)}'
            for i in range(1, len(self.params)):
                to_ret += f', {self.params[i].type}{dimensions(self.params[i].dimensions)}'
        return to_ret

    def __eq__(self, other):
        if isinstance(other, FunctionParameters):
            if len(self.params) != len(other.params):
                return False
            for i in range(len(self.params)):
                if self.params[i] != other.params[i]:
                    return False
            return True
        return False


class Variable(Identifier):
    def __init__(self, name, var_type, dimensions, location, visibility=None):
        super().__init__(name, IdentifierType.VARIABLE, location)
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

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.type == other.type and self.dimensions == other.dimensions


class SymbolTable(object):
    def __init__(self):
        self.global_scope = Scope()


class SymbolTableVisualizer(object):
    def __init__(self, symbol_table):
        self.global_scope = symbol_table.global_scope

    def visualize(self):
        to_ret = 'Global scope:\n'
        for child in self.global_scope.child_identifiers:
            to_ret += f'{self._parse_table(child, 1)}\n'
        return to_ret

    def _parse_table(self, identifier, indent):
        to_ret = ''
        for i in range(indent):
            to_ret += '\t'
        to_ret += f'- {identifier}\n'
        if identifier.identifier_type != IdentifierType.VARIABLE:
            for child in identifier.scope.child_identifiers:
                to_ret += self._parse_table(child, indent + 1)
        return to_ret
