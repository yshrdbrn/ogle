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
        for member in member_declarations:
            class_scope.add_child(self.visit(member, class_scope))

        return class_identifier

    @visitor(NodeType.FUNCTION_BODY)
    def visit(self, node, scope):
        pass

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
    def visit(self, node):
        pass

    @visitor(NodeType.FUNCTION_PARAMETERS)
    def visit(self, node, scope):
        params = FunctionParameters()
        for child in node.children:
            params.add_param(self._variable_decl(child))
        return params

    @visitor(NodeType.INHERITS)
    def visit(self, node, scope):
        to_ret = []
        for child in node.children:
            to_ret.append(child.value)
        return to_ret

    @visitor(NodeType.LOCAL_SCOPE)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.MAIN)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.PROGRAM)
    def visit(self, node, scope):
        class_declarations = node.children[0]
        function_definitions = node.children[1]
        main = node.children[2]

        for class_declaration in class_declarations:
            scope.add_child(self.visit(class_declaration, scope))
        for function_definition in function_definitions:
            scope.add_child(self.visit(function_definition, scope))
        scope.add_child(self.visit(main, scope))

    @visitor(NodeType.VARIABLE_DECLARATION)
    def visit(self, node, scope):
        return self._variable_decl(node, scope)

    def _variable_decl(self, node, scope):
        # If variable has visibility
        if len(node.children) == 4:
            visibility = node.children[0].value
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
