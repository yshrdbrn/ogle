import argparse
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser


def main():
    parser = argparse.ArgumentParser(description='Gets an input file and parses the file')
    parser.add_argument('file_name', type=str)
    file_name = parser.parse_args().file_name

    # open the file and read
    with open(file_name, 'r') as input_file:
        input_text = input_file.read()
        lexer = Lexer(input_text)
        parser = Parser(lexer)
        parser.parse()


if __name__ == '__main__':
    main()
