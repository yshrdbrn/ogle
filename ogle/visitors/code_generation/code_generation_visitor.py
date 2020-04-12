from struct import pack, error
from ogle.ast.ast_node import NodeType
from ogle.symbol_table.symbol_table import *
from ogle.visitors.visitor import visitor


# Registers to save in stack when calling a subroutine
important_registers = ['r15', 'r14', 'r13']


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

    @visitor(NodeType.FUNCTION_CALL)
    def visit(self, node, scope):
        self.visit(node.children[0], scope)

    @visitor(NodeType.FUNCTION_CALL_PARAMETERS)
    def visit(self, node, scope):
        identifier = node.identifier
        params = identifier.parameters.params
        number_of_bytes_moved = 0
        self.code_writer.comment('writing function parameters')
        for index, child in enumerate(node.children):
            self.visit(child, scope)
            # If parameter was array type
            if params[index].type.dimensions:
                # Replace the address with the value
                self.code_writer.load_word('r1', -8, 'r13')
                self.code_writer.store_word(-4, 'r13', 'r1')
            self.code_writer.operation('subi', 'r13', 'r13', 4)
            number_of_bytes_moved += 4
        self.code_writer.operation('addi', 'r13', 'r13', number_of_bytes_moved)

    @visitor(NodeType.FUNCTION_DEFINITION)
    def visit(self, node, scope):
        body = node.children[1]

        assert node.identifier
        func_identifier = node.identifier
        # Define the function
        self.code_writer.empty_line()
        self.code_writer.operation('nop', tag=func_identifier.tag)
        # Store all registers
        self.code_writer.comment('store all important registers in stack')
        for index, register in enumerate(important_registers):
            self.code_writer.store_word(-4 * (index + 1), 'r13', register)
        # Update r14
        self.code_writer.operation('subi', 'r14', 'r13', len(important_registers) * 4)

        self.visit(body, func_identifier.scope)

        self.code_writer.operation('nop', tag=func_identifier.tag+'_end')
        self.code_writer.operation('addi', 'r13', 'r14', len(important_registers) * 4)
        # Restore all registers
        self.code_writer.comment('restore important registers')
        for index, register in enumerate(important_registers):
            self.code_writer.load_word(register, -4 * (index + 1), 'r13')
        if func_identifier.return_type.type != Type.VOID:
            # Copy the return value to r13 address
            self.code_writer.comment('copy the return value')
            self.code_writer.operation('add', 'r1', 'r12', 'r0')
            self.code_writer.operation('add', 'r2', 'r13', 'r0')
            # TODO Change the size from 1 to the returned object size
            self.code_writer.operation('addi', 'r3', 'r0', 1)
            self.code_writer.operation('jl', 'r10', 'copybytes')

        self.code_writer.operation('jr', 'r15')

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
        self.visit(node.children[2], scope)
        # End of if statement
        self.code_writer.operation('nop', tag=if_tag_end)

    @visitor(NodeType.INDICES)
    def visit(self, node, scope):
        identifier = node.identifier

        dims = [0 for i in range(len(identifier.type.dimensions))]
        for i in range(1, len(identifier.type.dimensions)):
            dims[i] = int(identifier.type.dimensions[i])

        self.code_writer.operation('subi', 'r13', 'r13', 8)
        for index, child in enumerate(node.children):
            self.visit(child, scope)
            self.code_writer.comment(f'calculating variable address after index {index}')
            # TODO objects: move forward number number of size instead of 4
            if index != len(dims) - 1:
                sub_array_size = sum(dims[index+1:])
                self.code_writer.operation('addi', 'r1', 'r0', sub_array_size)
                self.code_writer.load_word('r2', -4, 'r13')
                self.code_writer.operation('mul', 'r1', 'r1', 'r2')
            else:  # index == len(dims) -1
                self.code_writer.load_word('r1', -4, 'r13')
            self.code_writer.operation('muli', 'r1', 'r1', 4)
            self.code_writer.load_word('r3', 0, 'r13')
            self.code_writer.operation('add', 'r3', 'r3', 'r1')
            self.code_writer.store_word(0, 'r13', 'r3')
        self.code_writer.operation('addi', 'r13', 'r13', 8)

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
        assert node.identifier
        identifier = node.identifier
        if isinstance(identifier, Function):
            self._handle_function(node, scope)
        else:
            self._handle_variable(node, scope)

    def _handle_function(self, node, scope):
        self.code_writer.comment(f'Calling function {node.identifier.name}')
        self.code_writer.operation('subi', 'r13', 'r13', len(important_registers) * 4)
        node.children[1].identifier = node.identifier
        self.visit(node.children[1], scope)
        self.code_writer.operation('addi', 'r13', 'r13', len(important_registers) * 4)
        self.code_writer.operation('jl', 'r15', node.identifier.tag)

    def _handle_variable(self, node, scope):
        identifier = node.identifier
        self.code_writer.comment(f'variable {identifier.name}')
        # Store the variable address in stack
        if identifier.is_function_parameter and identifier.type.dimensions:
            # If the variable is a function parameter and an array type,
            # its value is the address of the variable
            self.code_writer.load_word('r1', -(identifier.size + identifier.offset), 'r14')
        else:
            self.code_writer.operation('addi', 'r1', 'r14', -(identifier.size + identifier.offset))
        self.code_writer.store_word(-8, 'r13', 'r1')

        # If variable has indices
        if len(node.children) == 2:
            # Check the indices
            indices_node = node.children[1]
            indices_node.identifier = identifier
            self.visit(indices_node, scope)

        # Store the value of the variable
        self.code_writer.load_word('r1', -8, 'r13')
        self.code_writer.load_word('r2', 0, 'r1')
        self.code_writer.store_word(-4, 'r13', 'r2')

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

    @visitor(NodeType.RETURN_STATEMENT)
    def visit(self, node, scope):
        end_of_func_tag = scope.identifier.tag + '_end'
        self.code_writer.comment('Return statement')
        self.visit(node.children[0], scope)
        self.code_writer.comment('Store return value address in r12')
        self.code_writer.operation('add', 'r12', 'r13', 'r0')
        self.code_writer.operation('j', end_of_func_tag)

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
