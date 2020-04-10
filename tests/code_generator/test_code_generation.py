from pathlib import Path
import pytest
import subprocess
from tests.run_compiler import run

input_files = [
    {
        'code': '''
main
    local
        integer t;
    do
        read(t);
        t = t + 5;
        write(t);
    end
        ''',

        'input': '5',
        'output': '10'
    }
]

@pytest.fixture(scope="session")
def directory_with_moon(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp('test')
    moon_dir = Path.cwd().joinpath('moon')
    moon_code = moon_dir.joinpath('moon.c')
    subprocess.run(['gcc', moon_code, '-o', str(tmp_dir.joinpath('moon.out'))], stderr=subprocess.DEVNULL)
    subprocess.run(['cp', moon_dir.joinpath('util.m'), tmp_dir])
    return tmp_dir

@pytest.mark.parametrize("input_file", input_files)
def test_sample(directory_with_moon, input_file):
    d = directory_with_moon
    run(input_file['code'], str(d.joinpath('file.m')))
    out = subprocess.run(['./moon.out', 'file.m', 'util.m'],
                         cwd=str(d),
                         capture_output=True,
                         input=bytes(input_file['input'], 'utf-8'))\
        .stdout.decode("utf-8")
    assert out.splitlines()[2] == input_file['output']
