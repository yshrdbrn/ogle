from ogle.parser.ast_node import NodeType
from ogle.semantic_analyzer.visitors.visitor import visitor


class TypeCheckingVisitor(object):
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []

    # This function should never be called
    @visitor(NodeType.GENERAL)
    def visit(self, node, scope):
        assert False

    @visitor(NodeType.ADD_OPERATOR)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.ASSIGN_OPERATOR)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.ASSIGN_STATEMENT)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.COMPARE_OPERATOR)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.FLOAT_NUM)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.FUNCTION_BODY)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.FUNCTION_CALL)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.FUNCTION_CALL_PARAMETERS)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.FUNCTION_DEFINITION)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.IF_STATEMENT)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.INDICES)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.INT_NUM)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.ITEM)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.ITEM_LIST)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.MAIN)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.MULT_OPERATOR)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.NOT_OPERATOR)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.PROGRAM)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.READ_STATEMENT)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.RETURN_STATEMENT)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.SIGN_OPERATOR)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.STATEMENTS)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.WHILE_STATEMENT)
    def visit(self, node, scope):
        pass

    @visitor(NodeType.WRITE_STATEMENT)
    def visit(self, node, scope):
        pass
