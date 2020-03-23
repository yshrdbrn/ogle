from ogle.parser.ast_node import NodeType
from ogle.semantic_analyzer.symbol_table import *
from ogle.semantic_analyzer.visitors.symbol_table_visitor import SymbolTableVisitor
from ogle.semantic_analyzer.visitors.visitor import visitor


def _fetch_return_type(identifier):
    if isinstance(identifier, Function):
        return identifier.return_type
    else:
        return identifier.type


def _find_in_scope(identifier, scope):
    if isinstance(identifier, Function):
        return scope.get_child_by_identifier(identifier)
    else:
        return scope.get_child_by_name(identifier)


class TypeCheckingVisitor(object):
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
        self._symbol_table_visitor = SymbolTableVisitor()

        self._access_to_private_variable = False
        self._seen_return_statement = False

    # This function should never be called
    @visitor(NodeType.GENERAL)
    def visit(self, node, scope):
        assert False

    def _handle_lhs_rhs(self, node, scope):
        lhs = self.visit(node.children[0], scope)
        rhs = self.visit(node.children[1], scope)
        if lhs != rhs:
            location = node.location
            error_message = f"Error: Incompatible LHS and RHS types for operator '{node.value}'. " \
                            f"LHS: '{lhs}', RHS: '{rhs}'."
            raise TypeCheckingError(location, error_message)
        return lhs

    @visitor(NodeType.ADD_OPERATOR)
    def visit(self, node, scope):
        return self._handle_lhs_rhs(node, scope)

    @visitor(NodeType.ASSIGN_STATEMENT)
    def visit(self, node, scope):
        self._handle_lhs_rhs(node, scope)

    @visitor(NodeType.COMPARE_OPERATOR)
    def visit(self, node, scope):
        return self._handle_lhs_rhs(node, scope)

    @visitor(NodeType.FLOAT_NUM)
    def visit(self, node, scope):
        return TypeValue(Type.FLOAT)

    @visitor(NodeType.FUNCTION_BODY)
    def visit(self, node, scope):
        statements = node.children[1]
        self.visit(statements, scope)

    @visitor(NodeType.FUNCTION_CALL)
    def visit(self, node, scope):
        self.visit(node.children[0], scope)

    @visitor(NodeType.FUNCTION_CALL_PARAMETERS)
    def visit(self, node, scope):
        params = FunctionParameters()
        for child in node.children:
            returned_type = self.visit(child, scope)
            params.add_param(Variable(None, returned_type, returned_type.dimensions, None))
        return params

    @visitor(NodeType.FUNCTION_DEFINITION)
    def visit(self, node, scope):
        signature = node.children[0]
        body = node.children[1]

        self._seen_return_statement = False

        try:
            func_identifier = self._get_function_scope(signature, scope)
            self.visit(body, func_identifier.scope)
            if func_identifier.return_type.type != Type.VOID and not self._seen_return_statement:
                error_message = f"Error: Function definition does not return anything. " \
                                f"Expected '{func_identifier.return_type}'."
                self.errors.append((func_identifier.location, error_message))
        except (IdentifierNotFoundError, FunctionNotFoundError):
            pass

    def _get_function_scope(self, signature, scope):
        if len(signature.children) == 3:
            name = signature.children[0].value
            params = self._symbol_table_visitor.visit(signature.children[1], scope)
        else:
            namespace = signature.children[0].children[0].value
            scope = scope.get_child_by_name(namespace).scope
            name = signature.children[1].value
            params = self._symbol_table_visitor.visit(signature.children[2], scope)

        sample_func_identifier = Function(name, params, None, None)
        return scope.get_child_by_identifier(sample_func_identifier)

    @visitor(NodeType.IF_STATEMENT)
    def visit(self, node, scope):
        for child in node.children:
            self.visit(child, scope)

    @visitor(NodeType.INDICES)
    def visit(self, node, scope):
        to_ret = []
        for child in node.children:
            return_type = self.visit(child, scope)
            if return_type.type != Type.INTEGER:
                raise TypeCheckingError(None, f"Error: Expression inside the index is not integer. "
                                              f"Evaluated type: {return_type.type}.")
            to_ret.append(return_type)
        return to_ret

    @visitor(NodeType.INT_NUM)
    def visit(self, node, scope):
        return TypeValue(Type.INTEGER)

    @visitor(NodeType.ITEM)
    def visit(self, node, scopes):
        if len(node.children) == 2 and node.children[1].node_type == NodeType.FUNCTION_CALL_PARAMETERS:
            return self._handle_function_call(node, scopes)
        else:
            return self._handle_variable(node, scopes)

    def _handle_function_call(self, node, scopes):
        item_list_scope, new_scope = scopes

        name = node.children[0].value
        location = node.children[0].location
        params = self.visit(node.children[1], item_list_scope)
        identifier = Function(name, params, None, None)

        try:
            if isinstance(new_scope.identifier, Function):
                return self._type_of_identifier(identifier, new_scope), location
            else:
                return self._type_of_identifier_in_class(identifier, new_scope.identifier.name), location
        except (IdentifierNotFoundError, FunctionNotFoundError):
            error_message = f"Error: Unknown identifier '{name}'."
            raise TypeCheckingError(location, error_message)

    def _handle_variable(self, node, scopes):
        item_list_scope, new_scope = scopes

        name = node.children[0].value
        location = node.children[0].location
        indices = None
        # If variable has indices
        if len(node.children) == 2:
            try:
                indices = self.visit(node.children[1], item_list_scope)
            # catch TypeCheckingError from INDICES to add location
            except TypeCheckingError as e:
                e.location = location
                raise e

        # Find the variable
        try:
            if isinstance(new_scope.identifier, Function):
                returned_type = self._type_of_identifier(name, new_scope)
            else:
                returned_type = self._type_of_identifier_in_class(name, new_scope.identifier.name)
        except (IdentifierNotFoundError, FunctionNotFoundError):
            error_message = f"Error: Unknown identifier '{name}'."
            raise TypeCheckingError(location, error_message)

        if not indices:
            return returned_type, location

        # Check if the indices are valid
        if len(returned_type.dimensions) != len(indices):
            raise TypeCheckingError(location, f"Error: Unmatching number of indices. "
                                              f"Wanted {len(returned_type.dimensions)}, got {len(indices)}.")
        # Now the type does not have dimensions
        returned_type = TypeValue(returned_type.type, returned_type.value)
        return returned_type, location

    def _type_of_identifier(self, identifier, scope):
        # Search in function scope
        try:
            return _fetch_return_type(_find_in_scope(identifier, scope))
        except (IdentifierNotFoundError, FunctionNotFoundError):
            pass

        scope = scope.parent_scope
        # If the parent scope is a class
        if scope.identifier:
            self._access_to_private_variable = True
            class_name = scope.identifier.name
            try:
                return self._type_of_identifier_in_class(identifier, class_name)
            except (IdentifierNotFoundError, FunctionNotFoundError):
                pass
            # Not found in class. Set the scope to global scope
            scope = scope.parent_scope

        # Search in global scope
        # Might raise IdentifierNotFoundError
        return _fetch_return_type(_find_in_scope(identifier, scope))

    def _type_of_identifier_in_class(self, identifier, class_name):
        cls = self.symbol_table.global_scope.get_child_by_name(class_name)

        # Check the child identifiers in cls
        try:
            child = _find_in_scope(identifier, cls.scope)
            if child.visibility == Visibility.PUBLIC or self._access_to_private_variable:
                self._access_to_private_variable = False
                return _fetch_return_type(child)
        except (IdentifierNotFoundError, FunctionNotFoundError):
            pass

        # Call the parents to see if identifier exists
        for parent in cls.inherits:
            try:
                return self._type_of_identifier_in_class(identifier, parent)
            except (IdentifierNotFoundError, FunctionNotFoundError):
                pass

        raise IdentifierNotFoundError()

    @visitor(NodeType.ITEM_LIST)
    def visit(self, node, scope):
        last_type_location = None
        for item in node.children:
            new_scope = self._get_scope_for_item(last_type_location, scope)
            last_type_location = self.visit(item, (scope, new_scope))
        return last_type_location[0]

    def _get_scope_for_item(self, last_type_location, scope):
        if not last_type_location:
            return scope
        last_type, location = last_type_location
        if last_type.type != Type.ID:
            raise TypeCheckingError(location, f"Error: dot operator cannot be called on type '{last_type.type}'")
        class_id = self.symbol_table.global_scope.get_child_by_name(last_type.value)
        self._access_to_private_variable = scope.parent_scope.identifier == class_id
        return class_id.scope

    @visitor(NodeType.MAIN)
    def visit(self, node, scope):
        main_function_identifier = Function('main', FunctionParameters(), None, None)
        scope = scope.get_child_by_identifier(main_function_identifier).scope
        body = node.children[0]
        self.visit(body, scope)

    @visitor(NodeType.MULT_OPERATOR)
    def visit(self, node, scope):
        return self._handle_lhs_rhs(node, scope)

    @visitor(NodeType.NOT_OPERATOR)
    def visit(self, node, scope):
        return self.visit(node.children[0], scope)

    @visitor(NodeType.PROGRAM)
    def visit(self, node, scope):
        function_definitions = node.children[1]
        main = node.children[2]

        for function_definition in function_definitions.children:
            self.visit(function_definition, scope)
        self.visit(main, scope)

    @visitor(NodeType.READ_STATEMENT)
    def visit(self, node, scope):
        self.visit(node.children[0], scope)

    @visitor(NodeType.RETURN_STATEMENT)
    def visit(self, node, scope):
        self._seen_return_statement = True
        if scope.identifier.return_type.type == Type.VOID:
            location = node.location
            error_message = f"Error: Returning a value inside a void function."
            raise TypeCheckingError(location, error_message)

        return_type = self.visit(node.children[0], scope)
        if return_type != scope.identifier.return_type:
            location = node.location
            error_message = f"Error: Incompatible return type with function return type. Expected '{return_type}', " \
                            f"received '{scope.identifier.return_type}'."
            raise TypeCheckingError(location, error_message)

    @visitor(NodeType.SIGN_OPERATOR)
    def visit(self, node, scope):
        return self.visit(node.children[1], scope)

    @visitor(NodeType.STATEMENTS)
    def visit(self, node, scope):
        for child in node.children:
            try:
                self.visit(child, scope)
            except TypeCheckingError as e:
                self.errors.append((e.location, e.error_string))

    @visitor(NodeType.WHILE_STATEMENT)
    def visit(self, node, scope):
        for child in node.children:
            self.visit(child, scope)

    @visitor(NodeType.WRITE_STATEMENT)
    def visit(self, node, scope):
        self.visit(node.children[0], scope)
