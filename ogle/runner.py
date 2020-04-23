import argparse
from ogle.code_generator.code_generator import CodeGenerator
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser
from ogle.semantic_analyzer.semantic_analyzer import SemanticAnalyzer


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
            for error in parser.errors:
                print(error)
            return

        semantic_analyzer = SemanticAnalyzer(parser.ast)
        semantic_analyzer.analyze()
        if semantic_analyzer.errors:
            only_warnings = True
            for error in semantic_analyzer.errors:
                location = error[0]
                error_message = error[1]
                if 'Error' in error_message:
                    only_warnings = False
                print(f'Line {location[0]}:{location[1]}, {error_message}')
            if not only_warnings:
                return

        with open(file_name_no_type + '.m', 'w') as output:
            code_generator = CodeGenerator(parser.ast, semantic_analyzer.symbol_table)
            code_generator.generate(output)


if __name__ == '__main__':
    main()
