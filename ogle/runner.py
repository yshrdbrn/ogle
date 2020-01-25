import re
from ogle.lexer.lexer import Lexer


def main():
    lexer = Lexer("hello world")
    tokens = lexer.all_tokens()
    print(tokens)


if __name__ == '__main__':
    main()
