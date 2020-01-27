import pytest
import json
import pathlib
from ogle.lexer.lexer import *


@pytest.mark.parametrize("file_name", [
    'comments',
    'float',
    'integer',
    'id',
    'operators',
    'reserved_words'
])
def test_lexer(file_name):
    file_path = pathlib.Path(__file__).parent.absolute()
    with file_path.joinpath('data').joinpath(file_name + '_input.in').open('r') as input_file, \
            file_path.joinpath('data').joinpath(file_name + '_output.json').open('r') as output_file:
        input_text = input_file.read()
        lexer = Lexer(input_text)

        # Get all tokens from lexer and translate to a list of dicts
        token_list = lexer.all_tokens()
        output = [t.__dict__ for t in token_list]

        intended_output = json.load(output_file)
        assert output == intended_output
