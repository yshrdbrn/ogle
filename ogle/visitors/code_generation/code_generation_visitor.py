from struct import pack, error
from ogle.ast.ast_node import NodeType
from ogle.symbol_table.symbol_table import *
from ogle.visitors.semantic_checking.type_checking_visitor import fetch_return_type
from ogle.visitors.visitor import visitor


# Registers to save in stack when calling a subroutine
# * r13 should always be at the end of the list *
important_registers = ['r15', 'r14', 'r11', 'r13']


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
        return_type = self.visit(node.children[0], scope)
        size_of_type = self._size_of_type_no_array(return_type)
        assert size_of_type % 4 == 0
        self.code_writer.operation('addi', 'r13', 'r13', -(size_of_type + 4))
        self.visit(node.children[1], scope)
        self.code_writer.operation('addi', 'r13', 'r13', (size_of_type + 4))
        # Do the assignment
        self.code_writer.operation('addi', 'r1', 'r13', -(size_of_type + 4))
        self.code_writer.load_word('r2', -(size_of_type + 4), 'r13')
        self.code_writer.operation('addi', 'r3', 'r0', int(size_of_type / 4))
        self.code_writer.operation('jl', 'r10', 'copywords')

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
            size_no_array = self._size_of_type_no_array(params[index].type)
            # If parameter was array type
            if params[index].type.dimensions:
                # Replace the address with the value
                self.code_writer.load_word('r1', -(size_no_array + 4), 'r13')
                self.code_writer.store_word(-4, 'r13', 'r1')
                self.code_writer.operation('subi', 'r13', 'r13', 4)
                number_of_bytes_moved += 4
            else:
                self.code_writer.operation('subi', 'r13', 'r13', size_no_array)
                number_of_bytes_moved += size_no_array
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
            size_of_return_type = self._size_of_type_no_array(fetch_return_type(func_identifier))
            assert size_of_return_type % 4 == 0
            # Copy the return value to r13 address
            self.code_writer.comment('copy the return value')
            self.code_writer.operation('add', 'r1', 'r12', 'r0')
            self.code_writer.operation('add', 'r2', 'r13', 'r0')
            self.code_writer.operation('addi', 'r3', 'r0', int(size_of_return_type / 4))
            self.code_writer.operation('jl', 'r10', 'copywords')

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
        size_no_array = self._size_of_type_no_array(fetch_return_type(identifier))

        dims = [0 for _ in range(len(identifier.type.dimensions))]
        for i in range(1, len(identifier.type.dimensions)):
            dims[i] = int(identifier.type.dimensions[i])

        self.code_writer.operation('subi', 'r13', 'r13', (size_no_array + 4))
        for index, child in enumerate(node.children):
            self.visit(child, scope)
            self.code_writer.comment(f'calculating variable address after index {index}')
            if index != len(dims) - 1:
                sub_array_size = sum(dims[index+1:])
                self.code_writer.operation('addi', 'r1', 'r0', sub_array_size)
                self.code_writer.load_word('r2', -4, 'r13')
                self.code_writer.operation('mul', 'r1', 'r1', 'r2')
            else:  # index == len(dims) -1
                self.code_writer.load_word('r1', -4, 'r13')
            self.code_writer.operation('muli', 'r1', 'r1', size_no_array)
            self.code_writer.load_word('r3', 0, 'r13')
            self.code_writer.operation('sub', 'r3', 'r3', 'r1')
            self.code_writer.store_word(0, 'r13', 'r3')
        self.code_writer.operation('addi', 'r13', 'r13', (size_no_array + 4))

    @visitor(NodeType.INT_NUM)
    def visit(self, node, scope):
        val = int(node.value)
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
    def visit(self, node, scopes):
        assert node.identifier
        identifier = node.identifier
        if isinstance(identifier, Function):
            return self._handle_function(node, scopes)
        else:
            return self._handle_variable(node, scopes)

    def _handle_function(self, node, scopes):
        item_list_scope, new_scope = scopes

        func = new_scope.get_visible_function(node.identifier)
        self.code_writer.comment(f'Calling function {node.identifier.name}')
        self.code_writer.operation('subi', 'r13', 'r13', len(important_registers) * 4 + 4)
        node.children[1].identifier = node.identifier
        self.visit(node.children[1], item_list_scope)
        self.code_writer.operation('addi', 'r13', 'r13', len(important_registers) * 4 + 4)
        # Save the content of r9 on stack
        self.code_writer.store_word(-4, 'r13', 'r9')
        self.code_writer.operation('subi', 'r13', 'r13', 4)
        # Check if the function needs a namespace pointer
        if func.has_namespace():
            self.code_writer.comment('Set up the namespace register')
            # the callee's namespace is the same as the caller's namespace
            if item_list_scope.identifier == new_scope.identifier:
                self.code_writer.operation('subi', 'r9', 'r9', func.offset)
            else:
                self.code_writer.operation('subi', 'r9', 'r11', func.offset)
        # Call the function
        self.code_writer.operation('jl', 'r15', node.identifier.tag)
        # Restore the value of r9
        self.code_writer.operation('addi', 'r13', 'r13', 4)
        self.code_writer.load_word('r9', -4, 'r13')
        # Move the returned value 4 bytes
        if func.return_type.type != Type.VOID:
            size_of_return_type = self._size_of_type_no_array(fetch_return_type(func))
            assert size_of_return_type % 4 == 0
            self.code_writer.operation('addi', 'r1', 'r13', -4)
            self.code_writer.operation('add', 'r2', 'r13', 'r0')
            self.code_writer.operation('addi', 'r3', 'r0', int(size_of_return_type / 4))
            self.code_writer.operation('jl', 'r10', 'copywords')
        # Move r11 to the returned value's position, which is r13
        self.code_writer.comment('Move r11 to the returned value position')
        self.code_writer.operation('add', 'r11', 'r13', 'r0')

        return node.identifier.return_type

    def _handle_variable(self, node, scopes):
        item_list_scope, new_scope = scopes

        identifier = new_scope.get_visible_variable(node.identifier.name)
        size_no_array = self._size_of_type_no_array(fetch_return_type(identifier))

        self.code_writer.comment(f'variable {identifier.name}')
        # Store the variable address in stack
        if identifier.is_function_parameter and identifier.type.dimensions:
            # If the variable is a function parameter and an array type,
            # its value is the address of the variable
            self.code_writer.load_word('r1', -(4 + identifier.offset), 'r14')
        else:
            if identifier.is_namespace_variable:
                # Use namespace register (r9) instead of itemlist register
                self.code_writer.operation('addi', 'r1', 'r9', -identifier.offset)
            else:
                self.code_writer.operation('addi', 'r1', 'r11', -identifier.offset)
        self.code_writer.store_word(-(size_no_array + 4), 'r13', 'r1')

        # If variable has indices
        if len(node.children) == 2:
            # Check the indices
            indices_node = node.children[1]
            indices_node.identifier = identifier
            self.visit(indices_node, item_list_scope)

        # Store the value of the variable

        # Set up inputs for copywords
        self.code_writer.load_word('r1', -(size_no_array + 4), 'r13')
        self.code_writer.operation('add', 'r2', 'r13', 'r0')
        assert size_no_array % 4 == 0
        self.code_writer.operation('addi', 'r3', 'r0', int(size_no_array / 4))
        self.code_writer.operation('jl', 'r10', 'copywords')

        # Move r11 to the variable's position
        self.code_writer.load_word('r11', -(size_no_array + 4), 'r13')

        return identifier.type

    def _size_of_type_no_array(self, _type):
        global_scope = self.symbol_table.global_scope
        if _type.type != Type.ID:
            return 4
        else:
            class_id = global_scope.get_child_by_name(_type.value)
            return class_id.size

    @visitor(NodeType.ITEM_LIST)
    def visit(self, node, scope):
        # r11 -> dot operator object pointer
        # Save the current value of r11
        self.code_writer.store_word(-4, 'r13', 'r11')
        self.code_writer.operation('subi', 'r13', 'r13', 4)
        # Set r11 to current scope's stack pointer (r14)
        self.code_writer.operation('add', 'r11', 'r14', 'r0')
        last_return_type = None
        for child in node.children:
            new_scope = self._get_scope_for_item(last_return_type, scope)
            last_return_type = self.visit(child, (scope, new_scope))
        # restore r11
        return_type_size = self._size_of_type_no_array(last_return_type)
        assert return_type_size % 4 == 0
        self.code_writer.load_word('r11', 0, 'r13')
        self.code_writer.operation('addi', 'r13', 'r13', 4)
        # Move the returned value (its value + address) 4 bytes
        self.code_writer.operation('addi', 'r1', 'r13', -4)
        self.code_writer.operation('add', 'r2', 'r13', 'r0')
        self.code_writer.operation('addi', 'r3', 'r0', int((return_type_size / 4) + 1))
        self.code_writer.operation('jl', 'r10', 'copywords')

        return last_return_type

    def _get_scope_for_item(self, last_return_type, scope):
        if not last_return_type:
            return scope
        class_id = self.symbol_table.global_scope.get_child_by_name(last_return_type.value)
        return class_id.scope

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
        self.code_writer.comment('not operator')
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
        self.code_writer.comment('Read statement')
        self.visit(node.children[0], scope)
        self.code_writer.operation('jl', 'r15', 'getint')
        self.code_writer.load_word('r2', -8, 'r13')
        # r2 is the address to the end of the variable.
        # In order to use store_word, we need to pass -4(r2)
        self.code_writer.store_word(-4, 'r2', 'r1')

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
        if node.children[0].value == '-':
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
