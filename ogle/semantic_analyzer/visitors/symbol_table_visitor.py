from ogle.parser.ast_node import NodeType
from ogle.semantic_analyzer.symbol_table import *
from ogle.semantic_analyzer.visitors.visitor import visitor


class SymbolTableVisitor(object):
    def __init__(self):
        self.symbol_table = SymbolTable()

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
        name = name.value
        inherits = self.visit(inherits, scope)

        # Create the class identifier
        class_identifier = Class(name, inherits)
        class_scope = class_identifier.scope

        # Add members to scope
        for member in member_declarations.children:
            class_scope.add_child(self.visit(member, class_scope))

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
        name = name.value
        params = self.visit(params, scope)
        return_type = return_type.value

        # Create the Function identifier
        return Function(name, params, return_type, visibility)

    @visitor(NodeType.FUNCTION_DEFINITION)
    def visit(self, node, scope):
        signature = node.children[0]
        body = node.children[1]

        # Fetch function's scope
        identifier = self._function_identifier(signature, scope)

        # Visit function body
        self.visit(body, identifier.scope)

    def _function_identifier(self, func_signature, scope):
        if len(func_signature.children) == 3:
            # It's a free function
            name = func_signature.children[0].value
            params = self.visit(func_signature.children[1], scope)
            return_type = func_signature.children[2].value
            func_identifier = Function(name, params, return_type)
            self.symbol_table.global_scope.add_child(func_identifier)
        else:
            namespace = func_signature.children[0].children[0].value
            name = func_signature.children[1].value
            cls = self.symbol_table.global_scope.get_child(namespace)
            func_identifier = cls.scope.get_child(name)

        return func_identifier

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
            scope.add_child(self.visit(child, scope))

    @visitor(NodeType.MAIN)
    def visit(self, node, scope):
        main_function = Function('main', FunctionParameters(), 'void')
        self.symbol_table.global_scope.add_child(main_function)
        # Visit function body
        self.visit(node.children[0], main_function.scope)

    @visitor(NodeType.PROGRAM)
    def visit(self, node, scope):
        class_declarations = node.children[0]
        function_definitions = node.children[1]
        main = node.children[2]

        for class_declaration in class_declarations.children:
            scope.add_child(self.visit(class_declaration, scope))
        for function_definition in function_definitions.children:
            self.visit(function_definition, scope)
        self.visit(main, scope)

    @visitor(NodeType.VARIABLE_DECLARATION)
    def visit(self, node, scope):
        return self._variable_decl(node, scope)

    def _variable_decl(self, node, scope):
        # If variable has visibility
        if len(node.children) == 4:
            visibility = Visibility.visibility_from_string(node.children[0].name)
            var_type = node.children[1].value
            name = node.children[2].value
            dimensions = node.children[3]
        else:
            visibility = None
            var_type = node.children[0].value
            name = node.children[1].value
            dimensions = node.children[2]

        # Extract the result values
        dimensions = self.visit(dimensions, scope)

        return Variable(name, var_type, dimensions, visibility)
