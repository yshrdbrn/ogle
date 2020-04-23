import pytest
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser

input_codes = [
    # Bare-bones program
    '''
main
    do
    end
''',

    # Class definition, class member calls
    '''
class Test inherits Parent1, Parent2 {
    public test_func() : void;
    private Test a;
};

Test::test_func(): void
    local
        integer y;
    do
        read(y);
        write(y);
        return(y);
    end

main
    local
        Test x;
        integer t;
    do
        t = x.y().z.hello();
    end
''',

    # Free functions
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

    # Arithmetic expressions
    '''
main
    local
        integer arr[7];
        Class temp[20][30];
    do
        arr[1] = 2 + 5 * 6 + test_func().something[5];
        arr[2] = 3 and 4;
        temp[1][1] = 55.2;
    end
    ''',

    # While and If statements
    '''
main
    local
        integer x;
    do
        while (x > 0)
        do
            x = 10;
            while (x > 20)
            do
            end;
        end;
        
        if (x == 15)
            then
                x = 23;
            else
        ;
    end
    '''
]


@pytest.mark.parametrize("input_file", input_codes)
def test_parser_correct_input(input_file):
    lexer = Lexer(input_file)
    parser = Parser(lexer)
    parser.parse()
    assert not parser.errors
