from struct import pack, error
from ogle.ast.ast_node import NodeType
from ogle.symbol_table.symbol_table import *
from ogle.visitors.visitor import visitor

class CodeGenerationVisitor(object):
    def __init__(self, symbol_table, code_writer, tag_generator):
        self.symbol_table = symbol_table
        self.code_writer = code_writer
        self.tag_generator = tag_generator

# This function should never be called
    @visitor(NodeType.GENERAL)
    def visit(self, node, scope):
        assert False

    def _binary_operator(self, node, scope):
        self.visit(node.children[0], scope)
        self.code_writer.operation('addi', 'r13', 'r13', -8)
        self.visit(node.children[1], scope)
        self.code_writer.operation('addi', 'r13', 'r13', 8)

        self.code_writer.load_word('r1', -4, 'r13')
        self.code_writer.load_word('r2', -12, 'r13')

    @visitor(NodeType.ADD_OPERATOR)
    def visit(self, node, scope):
        self.code_writer.comment('add operator')
        self._binary_operator(node, scope)

        if node.value == '+':
            self.code_writer.operation('add', 'r1', 'r1', 'r2')
        elif node.value == '-':
            self.code_writer.operation('sub', 'r1', 'r1', 'r2')
        else:  # node.value == or
            self.code_writer.operation('cgt', 'r1', 'r1', 'r0')
            self.code_writer.operation('cgt', 'r2', 'r2', 'r0')
            self.code_writer.operation('or', 'r1', 'r1', 'r2')
        self.code_writer.store_word(-4, 'r13', 'r1')

    @visitor(NodeType.ASSIGN_STATEMENT)
    def visit(self, node, scope):
        self.code_writer.comment('Assign statement')
        self.visit(node.children[0], scope)
        self.code_writer.operation('addi', 'r13', 'r13', -8)
        self.visit(node.children[1], scope)
        self.code_writer.operation('addi', 'r13', 'r13', 8)
        # Do the assignment
        self.code_writer.load_word('r1', -12, 'r13')
        self.code_writer.load_word('r2', -8, 'r13')
        self.code_writer.store_word(0, 'r2', 'r1')

    @visitor(NodeType.COMPARE_OPERATOR)
    def visit(self, node, scope):
        self.code_writer.comment('compare operator')
        self._binary_operator(node, scope)

        if node.value == '<':
            self.code_writer.operation('clt', 'r1', 'r1', 'r2')
        elif node.value == '>':
            self.code_writer.operation('cgt', 'r1', 'r1', 'r2')
        elif node.value == '<=':
            self.code_writer.operation('cle', 'r1', 'r1', 'r2')
        elif node.value == '>=':
            self.code_writer.operation('cge', 'r1', 'r1', 'r2')
        elif node.value == '==':
            self.code_writer.operation('ceq', 'r1', 'r1', 'r2')
        else:  # node.value == '<>'
            self.code_writer.operation('cne', 'r1', 'r1', 'r2')
        self.code_writer.store_word(-4, 'r13', 'r1')

    @visitor(NodeType.FUNCTION_BODY)
    def visit(self, node, scope):
        statements = node.children[1]
        self.visit(statements, scope)

    @visitor(NodeType.IF_STATEMENT)
    def visit(self, node, scope):
        if_tag = self.tag_generator.tag_for_name('if')
        if_tag_else = if_tag + '_else'
        if_tag_end = if_tag + '_end'

        self.code_writer.comment('If statement')
        self.code_writer.operation('nop', tag=if_tag)
        # Get the condition value
        self.visit(node.children[0], scope)
        # Check the condition
        self.code_writer.operation('bz', 'r1', if_tag_else)
        # Then statement
        self.visit(node.children[1], scope)
        self.code_writer.operation('j', if_tag_end)
        # Else statement
        self.code_writer.operation('nop', tag=if_tag_else)
        # End of if statement
        self.code_writer.operation('nop', tag=if_tag_end)

    @visitor(NodeType.INT_NUM)
    def visit(self, node, scope):
        val = int(node.value)
        # Check if it fits into 4 bytes. Throws exception if not
        pack("i", val)
        self.code_writer.comment(f'Load immediate number {val} in stack')
        try:
            # Check if fits in 2 bytes
            pack("h", val)
            self.code_writer.operation('addi', 'r1', 'r0', val)
        except error:
            self.code_writer.operation('addi', 'r1', 'r0', (val >> 16) & 0xffff)
            self.code_writer.operation('sl', 'r1', 16)
            self.code_writer.operation('addi', 'r2', 'r0', val & 0xffff)
            self.code_writer.operation('add', 'r1', 'r1', 'r2')
        self.code_writer.store_word(-4, 'r13', 'r1')

    @visitor(NodeType.ITEM)
    def visit(self, node, scope):
        identifier = scope.get_child_by_name(node.children[0].value)
        self.code_writer.comment(f'identifier {identifier.name}')
        # Value of variable
        self.code_writer.load_word('r1', -(identifier.size + identifier.offset), 'r14')
        # Address of variable
        self.code_writer.operation('addi', 'r2', 'r14', -(identifier.size + identifier.offset))
        self.code_writer.store_word(-4, 'r13', 'r1')
        self.code_writer.store_word(-8, 'r13', 'r2')

    @visitor(NodeType.ITEM_LIST)
    def visit(self, node, scope):
        assert len(node.children) == 1
        self.visit(node.children[0], scope)

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

    @visitor(NodeType.MULT_OPERATOR)
    def visit(self, node, scope):
        self.code_writer.comment('mult operator')
        self._binary_operator(node, scope)

        if node.value == '*':
            self.code_writer.operation('mul', 'r1', 'r1', 'r2')
        elif node.value == '/':
            self.code_writer.operation('div', 'r1', 'r1', 'r2')
        else:  # node.value == and
            self.code_writer.operation('cgt', 'r1', 'r1', 'r0')
            self.code_writer.operation('cgt', 'r2', 'r2', 'r0')
            self.code_writer.operation('and', 'r1', 'r1', 'r2')
        self.code_writer.store_word(-4, 'r13', 'r1')

    @visitor(NodeType.NOT_OPERATOR)
    def visit(self, node, scope):
        self.code_writer.comment('mult operator')
        self.visit(node.children[1], scope)
        self.code_writer.load_word('r1', -4, 'r13')
        self.code_writer.operation('cgt', 'r1', 'r1', 'r0')
        self.code_writer.operation('cq', 'r1', 'r1', 'r0')
        self.code_writer.store_word(-4, 'r13', 'r1')

    @visitor(NodeType.PROGRAM)
    def visit(self, node, scope):
        function_definitions = node.children[1]
        main = node.children[2]

        for function_definition in function_definitions.children:
            self.visit(function_definition, scope)
        self.visit(main, scope)

    @visitor(NodeType.READ_STATEMENT)
    def visit(self, node, scope):
        self.code_writer.empty_line()
        self.visit(node.children[0], scope)
        self.code_writer.operation('jl', 'r15', 'getint')
        self.code_writer.load_word('r2', -8, 'r13')
        self.code_writer.store_word(0, 'r2', 'r1')

    @visitor(NodeType.SIGN_OPERATOR)
    def visit(self, node, scope):
        self.visit(node.children[1], scope)
        self.code_writer.load_word('r1', -4, 'r13')
        self.code_writer.operation('muli', 'r1', 'r1', -1)
        self.code_writer.store_word(-4, 'r13', 'r1')

    @visitor(NodeType.STATEMENTS)
    def visit(self, node, scope):
        for child in node.children:
            # Set computation stack pointer
            self.code_writer.empty_line()
            self.code_writer.operation('subi', 'r13', 'r14', scope.identifier.size)
            self.visit(child, scope)

    @visitor(NodeType.WHILE_STATEMENT)
    def visit(self, node, scope):
        while_tag = self.tag_generator.tag_for_name('while')
        while_tag_end = while_tag + '_end'

        self.code_writer.comment('While statement')
        self.code_writer.operation('nop', tag=while_tag)
        # Compute the condition
        self.visit(node.children[0], scope)
        # Evaluate the condition
        self.code_writer.operation('bz', 'r1', while_tag_end)
        # Execute the statements
        self.visit(node.children[1], scope)
        # Jump back to the beginning of while statement
        self.code_writer.operation('j', while_tag)
        self.code_writer.operation('nop', tag=while_tag_end)

    @visitor(NodeType.WRITE_STATEMENT)
    def visit(self, node, scope):
        self.code_writer.comment(f'Write statement')
        self.visit(node.children[0], scope)
        self.code_writer.load_word('r1', -4, 'r13')
        self.code_writer.operation('jl', 'r15', 'putint')
