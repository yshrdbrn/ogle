import re
from ogle.lexer.lexer import *


def main():
    input_text = 'hello world\n\ninteger a = 5;'
    lexer = Lexer(input_text)
    print(lexer.all_tokens())


if __name__ == '__main__':
    main()
