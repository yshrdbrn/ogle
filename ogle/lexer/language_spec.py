tokens = {
    'ID': r'[A-Za-z][A-Za-z_0-9]*',
    'FLOATNUM': r'(([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([Ee][+-]?[0-9]+)?|[0-9]+[Ee][+-]?[0-9]+)',
    'INTNUM': r'[0-9]+',

    # Multi-character operators
    '==': r'==',
    '<=': r'<=',
    '>=': r'>=',
    '<>': r'<>',
    '::': r'::',
}

special_characters = '<>+-*/=(){}[];,.:'

reserved_keywords = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'class': 'CLASS',
    'integer': 'INTEGER',
    'float': 'FLOAT',
    'do': 'DO',
    'end': 'END',
    'public': 'PUBLIC',
    'private': 'PRIVATE',
    'or': 'OR',
    'and': 'AND',
    'not': 'NOT',
    'read': 'READ',
    'write': 'WRITE',
    'return': 'RETURN',
    'main': 'MAIN',
    'inherits': 'INHERITS',
    'local': 'LOCAL',
    'void': 'VOID'
}

comments = r'(/\*(.|\n)*?\*/)|(//.*(\n[ \t]*//.*)*)'

whitespace = ' \t'
line_end = r'\n+'
