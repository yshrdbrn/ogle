from pathlib import Path
import pytest
import subprocess
from tests.run_compiler import run

input_files = [
    # Integer arithmetic
    # Read and Write statements
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
        'output': '30'
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
        'output': '32'
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
        'output': '-6'
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
        'output': '120'
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
        'output': '82'
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
    assert out.splitlines()[3] == input_file['output']
