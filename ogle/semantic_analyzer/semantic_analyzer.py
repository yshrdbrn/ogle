from ogle.semantic_analyzer.symbol_table import IdentifierType, SymbolTableVisualizer
from ogle.semantic_analyzer.visitors.symbol_table_visitor import SymbolTableVisitor


class SemanticAnalyzer(object):
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = None
        self.errors = []

    def analyze(self):
        self.symbol_table = self._get_symbol_table()
        dependency = CircularDependencyChecker.check_circular_dependency(self.symbol_table)
        self._generate_error_circular_dependency(dependency)
        self._check_undefined_functions()
        print(self.errors)

    def _get_symbol_table(self):
        symbol_table_visitor = SymbolTableVisitor()
        symbol_table_visitor.visit(self.ast.root)
        self.errors.extend(symbol_table_visitor.errors)
        return symbol_table_visitor.symbol_table

    def _generate_error_circular_dependency(self, dependency):
        if not dependency:
            return

        error_message = f"Error: circular dependency between classes '{dependency[0]}' and '{dependency[1]}'."
        location = self.symbol_table.global_scope.get_child(dependency[0]).location
        self.errors.append((location, error_message))

    def _check_undefined_functions(self):
        # Check each function inside classes
        for class_identifier in self.symbol_table.global_scope.get_classes():
            for child in class_identifier.scope.get_functions():
                if not child.is_defined:
                    error_message = f"Error: function '{child.name}' is declared but not defined."
                    self.errors.append((child.location,error_message))


class CircularDependencyChecker:
    @classmethod
    def check_circular_dependency(cls, symbol_table):
        adj_list = cls._build_adj_list(symbol_table)
        visited = set()
        for class_name in adj_list:
            if class_name not in visited:
                visiting = set()
                result = cls._dfs(class_name, adj_list, visiting, visited)
                # If found a circular dependency
                if result:
                    return result
                visited |= visiting

    @classmethod
    def _build_adj_list(cls, symbol_table):
        # dict of {'class': list of dependencies}
        adj_list = {}

        # Add classes to adj_list
        for class_identifier in symbol_table.global_scope.get_classes():
            adj_list[class_identifier.name] = []

        # Add dependency edges
        for class_identifier in symbol_table.global_scope.get_classes():
            for parent in class_identifier.inherits:
                adj_list[class_identifier.name].append(parent)
            for child in class_identifier.scope.get_variables():
                if child.type in adj_list:
                    adj_list[class_identifier.name].append(child.type)

        return adj_list

    @classmethod
    def _dfs(cls, class_name, adj_list, visiting, visited):
        visiting.add(class_name)
        for dependency in adj_list[class_name]:
            if dependency in visited:
                continue

            if dependency in visiting:
                return class_name, dependency
            else:
                result = cls._dfs(dependency, adj_list, visiting, visited)
                if result:
                    return result
        return None
