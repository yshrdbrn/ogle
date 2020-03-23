import argparse
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser
from ogle.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from ogle.semantic_analyzer.symbol_table import SymbolTableVisualizer


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
            with open(file_name_no_type + '.outparseerrors', 'w') as error_file:
                for error in parser.errors:
                    error_file.write(error + '\n')
        else:
            semantic_analyzer = SemanticAnalyzer(parser.ast)
            semantic_analyzer.analyze()
            with open(file_name_no_type + '.outsymboltable', 'w') as symbol_table_file, \
                    open(file_name_no_type + '.outsemanticerrors', 'w') as error_file:
                symbol_table_file.write(SymbolTableVisualizer(semantic_analyzer.symbol_table).visualize())
                for error in semantic_analyzer.errors:
                    location = error[0]
                    error_message = error[1]
                    error_file.write(f'Line {location[0]}:{location[1]}, {error_message}\n')


if __name__ == '__main__':
    main()
