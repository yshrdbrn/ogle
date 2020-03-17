from ogle.parser.ast_node import NodeType
from ogle.semantic_analyzer.symbol_table import *
from ogle.semantic_analyzer.visitors.symbol_table_visitor import SymbolTableVisitor
from ogle.semantic_analyzer.visitors.visitor import visitor


class TypeCheckingVisitor(object):
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []
        self._symbol_table_visitor = SymbolTableVisitor()

    # This function should never be called
    @visitor(NodeType.GENERAL)
    def visit(self, node, scope):
        assert False

    def _handle_lhs_rhs(self, node, scope):
        lhs = self.visit(node.children[0], scope)
        rhs = self.visit(node.children[1], scope)
        if lhs != rhs:
            location = node.location
            error_message = f"Error: Incompatible LHS and RHS types for operator {node.value}. " \
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
        pass

    @visitor(NodeType.FUNCTION_DEFINITION)
    def visit(self, node, scope):
        signature = node.children[0]
        body = node.children[1]

        try:
            func_identifier = self._get_function_scope(signature, scope)
            self.visit(body, func_identifier.scope)
        except IdentifierNotFoundError:
            pass

    def _get_function_scope(self, signature, scope):
        if len(signature.children) == 3:
            name = signature.children[0].value
            params = self._symbol_table_visitor.visit(signature.children[1], scope)
        else:
            namespace = signature.children[0].children[0].value
            scope = scope.get_child_by_name(namespace)
            name = signature.children[1].value
            params = self.visit(signature.children[2], scope)

        sample_func_identifier = Function(name, params, None, None)
        return scope.get_child_by_identifier(sample_func_identifier)

    @visitor(NodeType.IF_STATEMENT)
    def visit(self, node, scope):
        for child in node.children:
            self.visit(child, scope)

    @visitor(NodeType.INDICES)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.INT_NUM)
    def visit(self, node, scope):
        return TypeValue(Type.INTEGER)

    @visitor(NodeType.ITEM)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.ITEM_LIST)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.MAIN)
    def visit(self, node, scope):
        main_function_identifier = Function('main', FunctionParameters(), None, None)
        scope = scope.get_child_by_identifier(main_function_identifier)
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
        return_type = self.visit(node.children[0], scope)
        if return_type.type == Type.VOID:
            location = node.location
            error_message = f"Error: Returning a value inside a void function."
            raise TypeCheckingError(location, error_message)
        if return_type != scope.identifier.return_type:
            location = node.location
            error_message = f"Error: Incompatible return type with function return type. Expected '{return_type}', " \
                            f"received '{scope.identifier.return_type}'."
            raise TypeCheckingError(location, error_message)

    @visitor(NodeType.SIGN_OPERATOR)
    def visit(self, node, scope):
        return self.visit(node.children[0], scope)

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
        self.visit(node.children[0])
