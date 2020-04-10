import pytest
from tests.run_compiler import get_semantic_errors

# Each tuple consists of (input_file, number_of_errors)
input_files_with_errors = [
    # undefined base class
    ('''
class A inherits Undefined {
};

main
    local
        integer x;
    do
        x = 5 + 6;
    end
''', 1),

    # Undefined namespace
    ('''
Undefined::func(): void
    do
    end

main
    local
        integer x;
    do
        x = 5 + 6;
    end
''', 1),

    # function definition/declaration with no counterpart
    ('''
class A {
    public class_func(): void;  
};

A::another_func(): void
    do
    end

main
    local
        integer x;
    do
        x = 5 + 6;
    end
''', 2),

    # Multiple identifiers with the same name
    ('''
class A {
    public class_func(): void;  
    private class_func(): void;
    private integer B;
    public integer B;
};

class A {
};

A::class_func(): void
    do
    end

main
    local
        integer x;
    do
        x = 5 + 6;
    end
''', 3),

    # Circular dependency
    ('''
class A inherits C {
    private float a;
};

class B inherits A {
};

class C inherits B {
};

main
    do
    end
''', 1),
    ('''
class A {
    private B var;
};

class B inherits A {
};

main
    do
    end
''', 1),

    # Variables with wrong types
    ('''
func(): Unknown
    do
    end

main
    local
        Unknown var;
    do
    end
''', 2),
]


@pytest.mark.parametrize("input_file", input_files_with_errors)
def test_symbol_table_errors(input_file):
    errors, _ = get_semantic_errors(input_file[0])
    assert len(errors) == input_file[1]
