from ogle.semantic_analyzer.visitors.visitor import visitor
from ogle.parser.ast_node import Node, NodeType


class SymbolTableVisitor(object):
    # This function should never be called
    @visitor(NodeType.GENERAL)
    def visit(self, node):
        assert False

    @visitor(NodeType.ARRAY_DIMENSIONS)
    def visit(self, node):
        pass

    @visitor(NodeType.CLASS_DECLARATION)
    def visit(self, node):
        pass

    @visitor(NodeType.FUNCTION_BODY)
    def visit(self, node):
        pass

    @visitor(NodeType.FUNCTION_DECLARATION)
    def visit(self, node):
        pass

    @visitor(NodeType.FUNCTION_DEFINITION)
    def visit(self, node):
        pass

    @visitor(NodeType.FUNCTION_PARAMETERS)
    def visit(self, node):
        pass

    @visitor(NodeType.INHERITS)
    def visit(self, node):
        pass

    @visitor(NodeType.LOCAL_SCOPE)
    def visit(self, node):
        pass

    @visitor(NodeType.PROGRAM)
    def visit(self, node):
        pass

    @visitor(NodeType.VARIABLE_DECLARATION)
    def visit(self, node):
        pass
