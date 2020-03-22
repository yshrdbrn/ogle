import pytest
from tests.semantic_analyzer.run_compiler import get_semantic_errors

correct_input_files = [
    '''
func(integer x) : void
  local
    integer temp[5]; 
  do
    temp[0] = 5 * x + 4;
  end

main  
  local
    integer arr[2]; 
  do
    arr[1] = 2020;
    func(arr[1]);
  end
''',


    '''
// Class declarations
class A {
    public func(integer x) : integer;
    public float var;
};

class B inherits A {    
    public another_func() : A;
};

// Function definitions
A::func(integer x) : integer
    do
        var = 5.0 * var;
        return (1990);
    end

B::another_func() : A
    local
        A sample_object;
        integer random_int;
    do
        func(random_int);
        return (sample_object);
    end

main
    local
        B obj;
        integer y;
    do
        y = obj.another_func().func(y + 20);
    end
''',
]

# Each tuple consists of (input_file, number_of_warnings)
input_files_with_warnings = [
    ('''
// Class declarations
class A {
    public func(integer x) : void;
    public float var;
};

class B inherits A {    
    public func(integer x) : void;
};

class C inherits A {
    public float var;
};

// Function definitions
A::func(integer x) : void
    do
    end

B::func(integer x) : void
    do
    end

main
    do
    end
''', 2),


    ('''
// Class declarations
class A {
    public func(integer x) : void;
    public func(integer x, float y) : void;
};

// Function definitions
A::func(integer x) : void
    do
    end

A::func(integer x, float y) : void
    do
    end
    
test_func() : void
    do
    end

test_func(integer x): void
    do
    end

main
    do
    end
''', 2)
]

@pytest.mark.parametrize("input_file", correct_input_files)
def test_correct_input(input_file):
    errors, warnings = get_semantic_errors(input_file)
    assert not errors and not warnings

@pytest.mark.parametrize("input_file", input_files_with_warnings)
def test_input_with_warnings(input_file):
    errors, warnings = get_semantic_errors(input_file[0])
    assert not errors
    assert len(warnings) == input_file[1]
