from ogle.code_generator.code_writer import CodeWriter
from ogle.symbol_table.symbol_table import Type
from ogle.visitors.code_generation.code_generation_visitor import CodeGenerationVisitor


def get_variable_size(var_type):
    no_of_variables = 1
    for dim in var_type.dimensions:
        if dim:
            no_of_variables *= int(dim)
    return no_of_variables * 4


class CodeGenerator(object):
    def __init__(self, ast, symbol_table):
        self.ast = ast
        self.symbol_table = symbol_table
        self.tag_generator = TagGenerator()

    def generate(self, output_file):
        # Pre-calculation
        self._calculate_identifier_sizes()
        self._give_tags_to_functions()

        code_generation_visitor = CodeGenerationVisitor(self.symbol_table, CodeWriter(output_file))
        code_generation_visitor.visit(self.ast.root)

    # Calculate sizes of all identifier in symbol table
    def _calculate_identifier_sizes(self):
        global_scope = self.symbol_table.global_scope
        for cls in global_scope.get_classes():
            self._calculate_class_size(cls)
        for cls in global_scope.get_classes():
            for func in cls.scope.get_functions():
                self._calculate_function_size(func)
        for func in global_scope.get_functions():
            self._calculate_function_size(func)

    def _calculate_class_size(self, cls):
        global_scope = self.symbol_table.global_scope
        size_so_far = 0
        # Calculate all variable sizes
        for var in cls.scope.get_variables():
            if var.type.type != Type.ID:
                var.size = get_variable_size(var.type)
            else:
                class_id = global_scope.get_child_by_name(var.type.value)
                if not class_id.size:
                    self._calculate_class_size(class_id)
                var.size = class_id.size

            var.offset = size_so_far
            size_so_far += var.size

        # Calculate inherited class sizes
        for inherit in cls.inherits:
            inherited_class = global_scope.get_child_by_name(inherit)
            if not inherited_class.size:
                self._calculate_class_size(inherited_class)
            size_so_far += inherited_class.size

        cls.size = size_so_far

    def _calculate_function_size(self, func):
        global_scope = self.symbol_table.global_scope
        size_so_far = 0
        for var in func.scope.get_variables():
            if var.type.type != Type.ID:
                var.size = get_variable_size(var.type)
            else:
                class_id = global_scope.get_child_by_name(var.type.value)
                var.size = class_id.size

            var.offset = size_so_far
            size_so_far += var.size

        func.size = size_so_far

    def _give_tags_to_functions(self):
        global_scope = self.symbol_table.global_scope
        for cls in global_scope.get_classes():
            for func in cls.scope.get_functions():
                func.tag = self.tag_generator.tag_for_name(func.name)
        for func in global_scope.get_functions():
            func.tag = self.tag_generator.tag_for_name(func.name)


class TagGenerator(object):
    def __init__(self):
        self.name_repetitions = {}

    def tag_for_name(self, name):
        if name in self.name_repetitions:
            self.name_repetitions[name] += 1
            return f'{name}_{self.name_repetitions[name]}'
        else:
            self.name_repetitions[name] = 1
            return f'{name}_1'
