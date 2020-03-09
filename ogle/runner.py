import argparse
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser
from ogle.semantic_analyzer.visitors.symbol_table_visitor import SymbolTableVisitor


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
        ast = parser.ast

        # build the symbol table
        visitor = SymbolTableVisitor()
        visitor.visit(ast.root)
        pass


if __name__ == '__main__':
    main()
