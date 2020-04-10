from ogle.ast.ast_node import NodeType
from ogle.symbol_table.symbol_table import *
from ogle.visitors.visitor import visitor


class SymbolTableVisitor(object):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    # This function should never be called
    @visitor(NodeType.GENERAL)
    def visit(self, node, scope):
        assert False

    @visitor(NodeType.ARRAY_DIMENSIONS)
    def visit(self, node, scope):
        def array_size(n):
            optional_int = n.children[0]
            if len(optional_int.children) > 0:
                return optional_int.children[0].value
            else:
                return ''

        to_ret = []
        for child in node.children:
            to_ret.append(array_size(child))
        return to_ret

    @visitor(NodeType.CLASS_DECLARATION)
    def visit(self, node, scope):
        # Get all children nodes
        name = node.children[0]
        inherits = node.children[1]
        member_declarations = node.children[2]

        # Retrieve the result values
        name_value = name.value
        inherits = self.visit(inherits, scope)

        # Create the class identifier
        class_identifier = Class(name_value, inherits, name.location)
        class_scope = class_identifier.scope

        # Add members to scope
        for member in member_declarations.children:
            try:
                class_scope.add_child(self.visit(member, class_scope))
            except DuplicateIdentifierError as e:
                self._handle_duplicate_identifier_error(e)

        return class_identifier

    @visitor(NodeType.FUNCTION_BODY)
    def visit(self, node, scope):
        local_scope = node.children[0]
        self.visit(local_scope, scope)

    @visitor(NodeType.FUNCTION_DECLARATION)
    def visit(self, node, scope):
        # Get all children nodes
        visibility = node.children[0]
        name = node.children[1]
        params = node.children[2]
        return_type = node.children[3]

        # Retrieve the result values
        visibility = Visibility.visibility_from_string(visibility.name)
        name_value = name.value
        params = self.visit(params, scope)
        return_type = self.visit(return_type, scope)

        # Create the Function identifier
        return Function(name_value, params, return_type, name.location, visibility=visibility, is_defined=False)

    @visitor(NodeType.FUNCTION_DEFINITION)
    def visit(self, node, scope):
        signature = node.children[0]
        body = node.children[1]

        try:
            # Fetch function's identifier
            identifier = self._function_identifier(signature, scope)

            # Add function parameters to its scope
            self._add_params_to_func_vars(signature, identifier.scope)

            # Visit function body
            self.visit(body, identifier.scope)
        except DuplicateIdentifierError as e:
            self._handle_duplicate_identifier_error(e)
        except FunctionNotFoundError:
            id_node = signature.children[1]
            self.errors.append((id_node.location, f"Error: function '{id_node.value}' has no declaration."))
        except IdentifierNotFoundError:
            namespace = signature.children[0].children[0]
            self.errors.append((namespace.location, f"Error: use of undeclared class '{namespace.value}'."))

    def _function_identifier(self, func_signature, scope):
        if len(func_signature.children) == 3:
            # It's a free function
            name = func_signature.children[0]
            name_value = name.value
            params = self.visit(func_signature.children[1], scope)
            return_type = self.visit(func_signature.children[2], scope)
            func_identifier = Function(name_value, params, return_type, name.location, is_defined=True)
            try:
                self.symbol_table.global_scope.add_child(func_identifier)
            except DuplicateIdentifierError as e:
                if e.is_overload:
                    self._handle_duplicate_identifier_error(e)
                else:
                    raise e
        else:
            namespace = func_signature.children[0].children[0].value
            name = func_signature.children[1].value
            params = self.visit(func_signature.children[2], scope)
            temp_identifier = Function(name, params, None, None)
            cls = self.symbol_table.global_scope.get_child_by_name(namespace)
            func_identifier = cls.scope.get_child_by_identifier(temp_identifier)
            func_identifier.is_defined = True

        return func_identifier

    def _add_params_to_func_vars(self, signature, scope):
        if len(signature.children) == 3:
            params_node = signature.children[1]
        else:
            params_node = signature.children[2]

        for child in params_node.children:
            var = self._variable_decl(child, scope)
            try:
                scope.add_child(var)
            except DuplicateIdentifierError as e:
                self._handle_duplicate_identifier_error(e)

    @visitor(NodeType.FUNCTION_PARAMETERS)
    def visit(self, node, scope):
        params = FunctionParameters()
        for child in node.children:
            params.add_param(self._variable_decl(child, scope))
        return params

    @visitor(NodeType.INHERITS)
    def visit(self, node, scope):
        to_ret = []
        for child in node.children:
            to_ret.append(child.value)
        return to_ret

    @visitor(NodeType.LOCAL_SCOPE)
    def visit(self, node, scope):
        for child in node.children:
            try:
                scope.add_child(self.visit(child, scope))
            except DuplicateIdentifierError as e:
                self._handle_duplicate_identifier_error(e)

    @visitor(NodeType.MAIN)
    def visit(self, node, scope):
        ret_type = TypeValue(Type.VOID)
        main_function = Function('main', FunctionParameters(), ret_type, node.location, is_defined=True)
        self.symbol_table.global_scope.add_child(main_function)
        # Visit function body
        self.visit(node.children[0], main_function.scope)

    @visitor(NodeType.PROGRAM)
    def visit(self, node, scope):
        class_declarations = node.children[0]
        function_definitions = node.children[1]
        main = node.children[2]

        for class_declaration in class_declarations.children:
            try:
                scope.add_child(self.visit(class_declaration, scope))
            except DuplicateIdentifierError as e:
                self._handle_duplicate_identifier_error(e)
        for function_definition in function_definitions.children:
            self.visit(function_definition, scope)
        self.visit(main, scope)

    @visitor(NodeType.TYPE)
    def visit(self, node, scope):
        type_str = node.children[0].value
        return TypeValue.type_from_string(type_str)

    @visitor(NodeType.VARIABLE_DECLARATION)
    def visit(self, node, scope):
        return self._variable_decl(node, scope)

    def _variable_decl(self, node, scope):
        # If variable has visibility
        if len(node.children) == 4:
            visibility = Visibility.visibility_from_string(node.children[0].name)
            if node.children[1].node_type == NodeType.TYPE:
                var_type = self.visit(node.children[1], scope)
            else:
                var_type = TypeValue.type_from_string(node.children[1].value)
            name = node.children[2]
            dimensions = node.children[3]
        else:
            visibility = None
            var_type = self.visit(node.children[0], scope)
            name = node.children[1]
            dimensions = node.children[2]

        # Extract the result values
        name_value = name.value
        dimensions = self.visit(dimensions, scope)

        return Variable(name_value, var_type, dimensions, name.location, visibility)

    def _handle_duplicate_identifier_error(self, error):
        if error.is_overload:
            error_message = f"Warning: overloading function '{error.identifier.name}'."
        else:
            error_message = f"Error: duplicate identifier '{error.identifier.name}' in the scope."
        self.errors.append((error.identifier.location, error_message))
