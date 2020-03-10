import argparse
from ogle.parser.ast import ASTVisualizer
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser
from ogle.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from ogle.semantic_analyzer.symbol_table import SymbolTableVisualizer
from ogle.semantic_analyzer.visitors.symbol_table_visitor import SymbolTableVisitor


def check_for_semantic_errors(ast, output_filename):
    ASTVisualizer(ast).visualize(output_filename)
    visitor = SymbolTableVisitor()
    visitor.visit(ast.root)
    with open(output_filename + '.outsymboltable', 'w') as symbol_table_file:
        symbol_table_file.write(SymbolTableVisualizer(visitor.symbol_table).visualize())

def main():
    parser = argparse.ArgumentParser(description='Gets file name and compiles it')
    parser.add_argument('file_name', type=str)
    file_name = parser.parse_args().file_name
    file_name_no_type = file_name.split('.')[0]

    # open the file and read
    with open(file_name, 'r') as input_file:
        input_text = input_file.read()
        lexer = Lexer(input_text)
        parser = Parser(lexer)
        parser.parse()
        if parser.errors:
            with open(file_name_no_type + '.outerrors', 'w') as error_file:
                for error in parser.errors:
                    error_file.write(error + '\n')
        else:
            SemanticAnalyzer(parser.ast).analyze()
            # check_for_semantic_errors(parser.ast, file_name_no_type)


if __name__ == '__main__':
    main()
