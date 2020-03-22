from ogle.semantic_analyzer.semantic_errors import *
from ogle.semantic_analyzer.symbol_table import Type, Visibility
from ogle.semantic_analyzer.visitors.symbol_table_visitor import SymbolTableVisitor
from ogle.semantic_analyzer.visitors.type_checking_visitor import TypeCheckingVisitor


class SemanticAnalyzer(object):
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = None
        self.errors = []

    def analyze(self):
        self.symbol_table = self._get_symbol_table()
        self._analyze_definition_errors()
        self._analyze_statement_errors()
        self.errors.sort()

    def _get_symbol_table(self):
        symbol_table_visitor = SymbolTableVisitor()
        symbol_table_visitor.visit(self.ast.root)
        self.errors.extend(symbol_table_visitor.errors)
        return symbol_table_visitor.symbol_table

    def _analyze_definition_errors(self):
        cdc = CircularDependencyChecker()
        dependency = cdc.check_circular_dependency(self.symbol_table)
        self.errors.extend(cdc.errors)
        self._generate_error_circular_dependency(dependency)

        self._check_undefined_functions()
        self._check_for_unknown_types(self.symbol_table.global_scope)
        self._check_shadowed_members()

    def _analyze_statement_errors(self):
        type_checking_visitor = TypeCheckingVisitor(self.symbol_table)
        type_checking_visitor.visit(self.ast.root)
        self.errors.extend(type_checking_visitor.errors)

    def _generate_error_circular_dependency(self, dependency):
        if not dependency:
            return

        error_message = f"Error: circular dependency between classes '{dependency[0]}' and '{dependency[1]}'."
        location = self.symbol_table.global_scope.get_child_by_name(dependency[0]).location
        self.errors.append((location, error_message))

    def _check_undefined_functions(self):
        # Check each function inside classes
        for class_identifier in self.symbol_table.global_scope.get_classes():
            for child in class_identifier.scope.get_functions():
                if not child.is_defined:
                    error_message = f"Error: function '{child.name}' is declared but not defined."
                    self.errors.append((child.location, error_message))

    def _check_for_unknown_types(self, scope):
        for child in scope.get_classes():
            self._check_for_unknown_types(child.scope)
        for child in scope.get_functions():
            if not self._type_valid(child.return_type, child):
                scope.remove_child(child)
            self._check_for_unknown_types(child.scope)
        for child in scope.get_variables():
            if not self._type_valid(child.type, child):
                scope.remove_child(child)

    def _type_valid(self, t, identifier):
        if t.type != Type.ID:
            return True
        try:
            self.symbol_table.global_scope.get_child_by_name(t.value)
            return True
        except IdentifierNotFoundError:
            self.errors.append((identifier.location, f"Error: Unknown type for identifier '{identifier.name}'."))
            return False

    def _check_shadowed_members(self):
        for cls in self.symbol_table.global_scope.get_classes():
            for child in cls.scope.child_identifiers:
                if self._identifier_exists_in_class(child.name, cls.name, True):
                    self.errors.append(
                        (child.location,
                         f"Warning: identifier '{child.name}' shadows parent's identifier."))

    def _identifier_exists_in_class(self, name, class_name, first_call=False):
        # Get the class identifier object
        try:
            cls = self.symbol_table.global_scope.get_child_by_name(class_name)
        except IdentifierNotFoundError:
            return None

        # Check the child identifiers in cls
        if not first_call:
            try:
                child = cls.scope.get_child_by_name(name)
                if child.visibility == Visibility.PUBLIC:
                    return True
            except IdentifierNotFoundError:
                pass

        # Call the parents to see if identifier exists
        for parent in cls.inherits:
            if self._identifier_exists_in_class(name, parent):
                return True
        return False


class CircularDependencyChecker(object):
    errors = []

    def __init__(self):
        self.errors = []

    def check_circular_dependency(self, symbol_table):
        try:
            adj_list = self._build_adj_list(symbol_table)
            visited = set()
            for class_name in adj_list:
                if class_name not in visited:
                    visiting = set()
                    result = self._dfs(class_name, adj_list, visiting, visited)
                    # If found a circular dependency
                    if result:
                        return result
                    visited |= visiting
        except IdentifierNotFoundError as e:
            self.errors.append((e.location, f"Error: class '{e.requested_string}' not defined."))

    def _build_adj_list(self, symbol_table):
        # dict of {'class': list of dependencies}
        adj_list = {}

        # Add classes to adj_list
        for class_identifier in symbol_table.global_scope.get_classes():
            adj_list[class_identifier.name] = []

        # Add dependency edges
        for class_identifier in symbol_table.global_scope.get_classes():
            for parent in class_identifier.inherits:
                if parent in adj_list:
                    adj_list[class_identifier.name].append(parent)
                else:
                    raise IdentifierNotFoundError(class_identifier, parent)
            for child in class_identifier.scope.get_variables():
                if child.type.type == Type.ID:
                    val = child.type.value
                    if val in adj_list:
                        adj_list[class_identifier.name].append(val)
                    else:
                        raise IdentifierNotFoundError(child.location, child.type)

        return adj_list

    def _dfs(self, class_name, adj_list, visiting, visited):
        visiting.add(class_name)
        for dependency in adj_list[class_name]:
            if dependency in visited:
                continue

            if dependency in visiting:
                return class_name, dependency
            else:
                result = self._dfs(dependency, adj_list, visiting, visited)
                if result:
                    return result
        return None

    def _check_if_class_exists(self, class_name, symbol_table, child_class_identifier):
        try:
            symbol_table.global_scope.get_child_by_name(class_name)
        except IdentifierNotFoundError as e:
            e.declaring_class = child_class_identifier
            raise e
