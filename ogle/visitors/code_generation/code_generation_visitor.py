from ogle.ast.ast_node import NodeType
from ogle.symbol_table.symbol_table import *
from ogle.visitors.visitor import visitor

class CodeGenerationVisitor(object):
    def __init__(self, symbol_table, code_writer):
        self.symbol_table = symbol_table
        self.code_writer = code_writer

# This function should never be called
    @visitor(NodeType.GENERAL)
    def visit(self, node, scope):
        assert False

    @visitor(NodeType.FUNCTION_BODY)
    def visit(self, node, scope):
        statements = node.children[1]
        self.visit(statements, scope)

    @visitor(NodeType.INT_NUM)
    def visit(self, node, scope):
        return TypeValue(Type.INTEGER)

    @visitor(NodeType.ITEM)
    def visit(self, node, scope):
        assert len(node.children) == 1
        return scope.get_child_by_name(node.children[0].value)

    @visitor(NodeType.ITEM_LIST)
    def visit(self, node, scope):
        assert len(node.children) == 1
        return self.visit(node.children[0], scope)

    @visitor(NodeType.MAIN)
    def visit(self, node, scope):
        main_identifier = scope.get_child_by_identifier(
            Function('main', FunctionParameters(), None, None))

        self.code_writer.empty_line()
        self.code_writer.operation('entry')
        self.code_writer.operation('addi', 'r14', 'r0', 'topaddr')
        self.code_writer.comment('main function')
        self.code_writer.operation('nop', tag=main_identifier.tag)

        scope = main_identifier.scope
        body = node.children[0]
        self.visit(body, scope)

        self.code_writer.comment('End of program')
        self.code_writer.operation('hlt')
        self.code_writer.empty_line()

    @visitor(NodeType.PROGRAM)
    def visit(self, node, scope):
        function_definitions = node.children[1]
        main = node.children[2]

        for function_definition in function_definitions.children:
            self.visit(function_definition, scope)
        self.visit(main, scope)

    @visitor(NodeType.READ_STATEMENT)
    def visit(self, node, scope):
        identifier = self.visit(node.children[0], scope)

        self.code_writer.comment(f'Read statement: {identifier.name}')
        self.code_writer.operation('jl', 'r15', 'getint')
        self.code_writer.store_word(-(identifier.size + identifier.offset), 'r14', 'r1')

    @visitor(NodeType.STATEMENTS)
    def visit(self, node, scope):
        for child in node.children:
            self.visit(child, scope)

    @visitor(NodeType.WRITE_STATEMENT)
    def visit(self, node, scope):
        identifier = self.visit(node.children[0], scope)

        self.code_writer.comment(f'Write statement: {identifier.name}')
        self.code_writer.load_word('r1', -(identifier.size + identifier.offset), 'r14')
        self.code_writer.operation('jl', 'r15', 'putint')
