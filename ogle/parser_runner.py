import argparse
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser
from ogle.parser.ast import ASTVisualizer


def main():
    parser = argparse.ArgumentParser(description='Gets an input file and parses the file')
    parser.add_argument('file_name', type=str)
    file_name = parser.parse_args().file_name
    file_name_no_type = file_name.split('.')[0]

    # open the file and read
    with open(file_name, 'r') as input_file, \
            open(file_name_no_type + '.outderivation', 'w') as derivation_file, \
            open(file_name_no_type + '.outerrors', 'w') as error_file:
        input_text = input_file.read()
        lexer = Lexer(input_text)
        parser = Parser(lexer)
        parser.parse()

        # Output the results
        ASTVisualizer(parser.ast).visualize(file_name_no_type)
        for error in parser.errors:
            error_file.write(error + '\n')
        for derivation in parser.parse_tree.derivation_list:
            derivation_file.write(derivation + '\n')


if __name__ == '__main__':
    main()
