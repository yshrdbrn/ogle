import pytest
from ogle.lexer.lexer import Lexer
from ogle.parser.parser import Parser
from ogle.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

def _get_errors_warnings(all_errors):
    errors = [e for e in all_errors if 'Error' in e[1]]
    warnings = [e for e in all_errors if 'Warning' in e[1]]
    return errors, warnings

def get_semantic_errors(input_file):
    lexer = Lexer(input_file)
    parser = Parser(lexer)
    parser.parse()
    semantic_analyzer = SemanticAnalyzer(parser.ast)
    semantic_analyzer.analyze()
    return _get_errors_warnings(semantic_analyzer.errors)
