import pytest
from tests.run_compiler import get_semantic_errors

# Each tuple consists of (input_file, number_of_errors)
type_checking_errors = [
    # incompatible lhs and rhs
    ('''
func() : float
    do
        return (1.0);
    end
    
main
    local
        integer x;
        float y;
        integer z[5];
    do
        // overflow
        x = 10000000000000;
        
        // arithmetic operators
        x = 1.5 + 3;
        x = 1.5 - 3;
        x = 1.5 * 3;
        x = 1.5 / 3;
        x = 1.5 and 2;
        x = 1.5 or 2;
        x = z[1.5 * 2];
        
        // assignment operator
        y = 2 + 5;
        x = 1.5 * 2.0;
        x = func();
    end
''', 11),

    # function return statement
    ('''
func() : float
    do
        // no return statement
    end
    
func2() : integer
    do
        // incompatible return type
        return (1.0);
    end

func3() : void
    do
        // returning a value in a void function
        return (1);
    end

main
    do
    end
''', 3),

    # function call
    ('''
func(integer x, float y) : void
    do
    end

func2(integer x[][]) : void
    do
    end

func3() : void
    do
    end

main
    local
        integer x[5][6];
    do
        func(1);
        func(1, 2);
        func(1, 2.0, 3);
        func(x[1], 2.0);
        func2(x[5]);
        func3(1);
        
        // correct calls
        func(1, 2.0);
        func2(x);
        func3();
    end
''', 6),

    # dot operator
    ('''
class A {
    public public_func() : integer;
    private private_func() : integer;
};

A::public_func() : integer
    do
        return (0);
    end
    
A::private_func() : integer
    do
        return (1);
    end
    

func() : A
    local
        A a;
    do
        // object read and arithmetic are not allowed
        read(a);
        a = a + a;
        return (a);
    end

func2() : float
    do
        return (1.0);
    end

main
    local
        float x;
        integer y;
    do
        x = func2().public_func();
        y = func().private_func();
        
        // correct call
        y = func().public_func();
    end
''', 4),
]

@pytest.mark.parametrize("input_file", type_checking_errors)
def test_type_checking_errors(input_file):
    errors, _ = get_semantic_errors(input_file[0])
    assert len(errors) == input_file[1]


# Each tuple consists of (input_file, number_of_errors)
symbol_table_type_checking_errors = [
    # dot operator
    ('''
class A {
    // undefined return type
    public func() : unknown_type;
    public unknown_type x;
};

main
    local
        A a;
        integer x;
    do
        a.func();
        x = a.x;
    end
''', 5),
]

@pytest.mark.parametrize("input_file", symbol_table_type_checking_errors)
def test_symbol_table_and_type_checking_errors(input_file):
    errors, _ = get_semantic_errors(input_file[0])
    assert len(errors) == input_file[1]
