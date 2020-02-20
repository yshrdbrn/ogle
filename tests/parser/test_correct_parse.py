import pytest
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser

input_codes = [
    '''
main
    do
    end
''',

    '''
class Test {
    public test_func() : void;
    private Test a;
};
main
    do
    end
''',

    '''
test_func(int x) : integer
    local
        float something;
    do
        some_id = a[5].test();
    end
main
    do
    end
    ''',

    '''
main
    local
        integer arr[7];
    do
        arr[1] = 2 + 5 * 6 + test_func().something[5];
    end
    '''
]


@pytest.mark.parametrize("input_file", input_codes)
def test_parser_correct_input(input_file):
    lexer = Lexer(input_file)
    parser = Parser(lexer)
    parser.parse()
    assert not parser.errors
