from copy import copy
from ogle.code_generator.code_writer import CodeWriter
from ogle.symbol_table.symbol_table import Type, Visibility
from ogle.visitors.code_generation.code_generation_visitor import CodeGenerationVisitor


def update_variable_size_based_on_dimensions(var):
    var_type = var.type
    no_of_variables = 1
    if not var.is_function_parameter:
        for dim in var_type.dimensions:
            if dim:
                no_of_variables *= int(dim)
        var.size = no_of_variables * var.size
    else:
        if var_type.dimensions:
            var.size = 4


class CodeGenerator(object):
    def __init__(self, ast, symbol_table):
        self.ast = ast
        self.symbol_table = symbol_table
        self.tag_generator = TagGenerator()

    def generate(self, output_file):
        # Pre-calculation
        self._calculate_identifier_sizes()
        self._give_tags_to_functions()
        self._compute_visible_identifiers()

        code_generation_visitor = CodeGenerationVisitor(self.symbol_table, CodeWriter(output_file), self.tag_generator)
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
                var.size = 4
            else:
                class_id = global_scope.get_child_by_name(var.type.value)
                if not class_id.size:
                    self._calculate_class_size(class_id)
                var.size = class_id.size

            update_variable_size_based_on_dimensions(var)
            var.offset = size_so_far
            size_so_far += var.size

        cls.size_of_just_self = size_so_far
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
                var.size = 4
            else:
                class_id = global_scope.get_child_by_name(var.type.value)
                var.size = class_id.size

            update_variable_size_based_on_dimensions(var)
            var.offset = size_so_far
            size_so_far += var.size

        func.size = size_so_far

    def _give_tags_to_functions(self):
        global_scope = self.symbol_table.global_scope
        for cls in global_scope.get_classes():
            for func in cls.scope.get_functions():
                func.tag = self.tag_generator.tag_for_func()
        for func in global_scope.get_functions():
            func.tag = self.tag_generator.tag_for_func()

    def _compute_visible_identifiers(self):
        global_scope = self.symbol_table.global_scope
        # Visible variables in classes
        for cls in global_scope.get_classes():
            self._compute_visible_variables_for_class(cls)
        for cls in global_scope.get_classes():
            cls.scope.seen_scope = False
        # Visible functions in classes
        for cls in global_scope.get_classes():
            self._compute_visible_functions_for_class(cls)
        # Visible variables in free functions
        for func in global_scope.get_functions():
            for var in func.scope.get_variables():
                func.scope.add_visible_variable(var)
        # Visible functions in free functions
        for func in global_scope.get_functions():
            for func2 in global_scope.get_functions():
                func.scope.get_visible_function(func2)
        # Visible variables in class functions
        for cls in global_scope.get_classes():
            for func in cls.scope.get_functions():
                self._compute_visible_variables_for_function(func)
        # Visible functions in class functions
        for cls in global_scope.get_classes():
            for func in cls.scope.get_functions():
                self._computer_visible_functions_for_function(func)

    def _compute_visible_variables_for_class(self, cls):
        global_scope = self.symbol_table.global_scope
        cls.scope.seen_scope = True
        current_offset = 0
        for var in cls.scope.get_variables():
            cls.scope.add_visible_variable(var)
            current_offset += var.size

        # Go through all inherited classes
        for inherit in cls.inherits:
            inherited_class = global_scope.get_child_by_name(inherit)
            if not inherited_class.scope.seen_scope:
                self._compute_visible_variables_for_class(inherited_class)
            # Go through each visible variable of the inherited class
            for var in inherited_class.scope.visible_variables:
                if var.visibility != Visibility.PRIVATE and not cls.scope.get_visible_variable(var.name):
                    new_var = copy(var)
                    new_var.offset = var.offset + current_offset
                    cls.scope.add_visible_variable(new_var)
            current_offset += inherited_class.size

    def _compute_visible_functions_for_class(self, cls):
        global_scope = self.symbol_table.global_scope
        cls.scope.seen_scope = True
        current_offset = 0
        for func in cls.scope.get_functions():
            func.offset = 0
            cls.scope.add_visible_function(func)

        current_offset += cls.size_of_just_self
        # Go through all inherited classes
        for inherit in cls.inherits:
            inherited_class = global_scope.get_child_by_name(inherit)
            if not inherited_class.scope.seen_scope:
                self._compute_visible_functions_for_class(inherited_class)
            # Go through each visible function of the inherited class
            for func in inherited_class.scope.visible_functions:
                if func.visibility != Visibility.PRIVATE and not cls.scope.get_visible_function(func):
                    new_func = copy(func)
                    new_func.offset = current_offset
                    cls.scope.add_visible_function(new_func)
            current_offset += inherited_class.size

    def _compute_visible_variables_for_function(self, func):
        for var in func.scope.get_variables():
            func.scope.add_visible_variable(var)
        for var in func.scope.parent_scope.visible_variables:
            if not func.scope.get_visible_variable(var.name):
                new_var = copy(var)
                new_var.is_namespace_variable = True
                func.scope.add_visible_variable(new_var)

    def _computer_visible_functions_for_function(self, func):
        global_scope = self.symbol_table.global_scope
        for f in func.scope.parent_scope.visible_functions:
            func.scope.add_visible_function(f)
        for f in global_scope.get_functions():
            if not func.scope.get_visible_function(f):
                func.scope.add_visible_function(f)


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

    def tag_for_func(self):
        return self.tag_for_name('func')
