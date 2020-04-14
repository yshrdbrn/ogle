from pathlib import Path
import pytest
import subprocess
from tests.run_compiler import run

input_files = [
    #
    # Integer arithmetic
    # Read and Write statements
    #
    {
        'code': '''
main
    local
        integer t;
        integer y;
    do
        read(t);
        t = t * 2 + 5;
        y = 7 > 5;
        t = t + y;
        write(t);
    end
        ''',

        'input': '12',
        'output': ['30']
    },

    #
    # If and while statements
    #
    {
        'code': '''
main
    local
        integer a;
        integer b;
    do
        a = 10;
        if (a < 5)
            then
                a = 20;
            else
                a = 5;
        ;
        
        b = 1;
        while (a > 0)
            do
                b = b * 2;
                a = a - 1;
            end;
        write(b);
    end
        ''',

        'input': '0',
        'output': ['32']
    },

    #
    # Functions
    #

    # Multiple function calls
    {
        'code': '''
f1(integer x): integer
    local
    do
        return (x * 2);
    end
    
f2(integer x): integer
    local
    do
        return (x + 2);
    end

main
    local
        integer x;
    do
        write(f1(f2(-5)));
    end
        ''',

        'input': '0',
        'output': ['-6']
    },

    # Recursive function
    {
        'code': '''
factorial(integer x): integer
    local
    do
        if (x == 1)
            then
                return (1);
            else
                return (factorial(x - 1) * x);
        ;
    end
    
main
    local
    do
        write(factorial(5));
    end
        ''',

        'input': '0',
        'output': ['120']
    },

    #
    # Arrays
    #
    {
        'code': '''
func(integer arr[][11]): integer
    local
    do
        // Array is passed by reference
        arr[1][1] = 10;
        return(arr[8][9]);
    end

main
    local
        integer t[11][11];
        integer i;
        integer j;
    do
        i = 1;
        while (i <= 10)
        do
            j = 1;
            while (j <= 10)
            do
                t[i][j] = i * j;
                j = j + 1;
            end;
            i = i + 1;
        end;

        write(func(t) + t[1][1]);
    end
        ''',

        'input': '0',
        'output': ['82']
    },

    #
    # Classes
    #

    # Object variables
    {
        'code': '''
class A {
    public integer x;
    public integer y;
};

main
    local
        A a;
        A objectArray[10][10];
    do
        a.x = 20;
        objectArray[3][4].y = 7;
        write(a.x + objectArray[3][4].y);
    end
        ''',

        'input': '0',
        'output': ['27']
    },

    # Object functions
    {
        'code': '''
class A {
    private integer x;
    private integer y;
    
    public init(integer X, integer Y): void;
    public sum(): integer;
};

A::init(integer X, integer Y): void
    do
        x = X;
        y = Y;
    end

A::sum(): integer
    do
        return (x + y);
    end

main
    local
        A a;
    do
        a.init(100, 20);
        write(a.sum());
    end
        ''',

        'input': '0',
        'output': ['120']
    },

    # Inheritance
    {
        'code': '''
class POLYNOMIAL {
    public evaluate(integer x) : integer;
};

class LINEAR inherits POLYNOMIAL {
    private integer a;
    private integer b;
    
    public build(integer A, integer B) : LINEAR;
    public evaluate(integer x) : integer;
};

class QUADRATIC inherits POLYNOMIAL {
    private integer a;
    private integer b;
    private integer c;
    
    public build(integer A, integer B, integer C) : QUADRATIC;
    public evaluate(integer x) : integer;
};

POLYNOMIAL::evaluate(integer x) : integer
  do
    return (0);
  end

LINEAR::evaluate(integer x) : integer
  local
    integer result;
  do
    result = 0;
    result = a * x + b;
    return (result);
  end
  
QUADRATIC::evaluate(integer x) : integer
  local
    integer result;
  do    //Using Horner's method
    result = a;
    result = result * x + b;
    result = result * x + c;
    return (result);
  end
  
LINEAR::build(integer A, integer B) : LINEAR
  local
    LINEAR new_function;
  do
    new_function.a = A;
    new_function.b = B;
    return (new_function);
  end  
  
QUADRATIC::build(integer A, integer B, integer C) : QUADRATIC
  local
    QUADRATIC new_function;
  do
    new_function.a = A;
    new_function.b = B;
    new_function.c = C;
    return (new_function);
  end
  
main
  local
    LINEAR f1;
    QUADRATIC f2;
  do
    f1 = f1.build(2, 3);
    f2 = f2.build(-2, 1, 0);

    write(f1.evaluate(5));
    write(f2.evaluate(5));
  end
        ''',

        'input': '0',
        'output': ['13', '-45']
    }
]

@pytest.fixture(scope="session")
def directory_with_moon(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp('test')
    moon_dir = Path.cwd().joinpath('moon')
    moon_code = moon_dir.joinpath('moon.c')
    subprocess.run(['gcc', moon_code, '-o', str(tmp_dir.joinpath('moon.out'))], stderr=subprocess.DEVNULL)
    subprocess.run(['cp', moon_dir.joinpath('util.m'), tmp_dir])
    subprocess.run(['cp', moon_dir.joinpath('util_2.m'), tmp_dir])
    return tmp_dir

@pytest.mark.parametrize("input_file", input_files)
def test_sample(directory_with_moon, input_file):
    d = directory_with_moon
    run(input_file['code'], str(d.joinpath('file.m')))
    out = subprocess.run(['./moon.out', 'file.m', 'util.m', 'util_2.m'],
                         cwd=str(d),
                         capture_output=True,
                         input=bytes(input_file['input'], 'utf-8'))\
        .stdout.decode("utf-8")
    assert out.splitlines()[3:-2] == input_file['output']
