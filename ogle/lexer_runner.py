import argparse
from ogle.lexer.lexer import Lexer


def main():
    parser = argparse.ArgumentParser(description='Gets an input file and creates token and error files')
    parser.add_argument('file_name', type=str)
    file_name = parser.parse_args().file_name
    file_name_no_type = file_name.split('.')[0]

    # open the file and read
    with open(file_name, 'r') as input_file, \
            open(file_name_no_type + '.outlextokens', 'w') as token_out, \
            open(file_name_no_type + '.outlexerrors', 'w') as error_out:
        input_text = input_file.read()
        lexer = Lexer(input_text)
        all_tokens = lexer.all_tokens()
        tokens = [x for x in all_tokens if x.type is not 'ERROR']
        errors = [x for x in all_tokens if x.type is 'ERROR']

        for token in tokens:
            token_out.write(str(token) + '\n')
        for error in errors:
            error_out.write(str(error) + '\n')


if __name__ == '__main__':
    main()
