from ogle.language_spec import reserved_keywords


# A map from terminals to token types
terminals = dict(reserved_keywords)
terminals.update({
    'id': 'ID',
    'intnum': 'INTNUM',
    'floatnum': 'FLOATNUM',

    'lcurbr': r'{',
    'rcurbr': r'}',
    'semi': r';',
    'lpar': r'(',
    'rpar': r')',
    'lsqbr': r'[',
    'rsqbr': r']',
    'dot': r'.',
    'plus': r'+',
    'minus': r'-',
    'mult': r'*',
    'div': r'/',
    'colon': r':',
    'comma': r',',
    'equal': r'=',
    'less': r'<',
    'greater': r'>',

    'eq': r'==',
    'lesseq': r'<=',
    'greatereq': r'>=',
    'noteq': r'<>',
    'coloncolon': r'::',
})

tokens_to_terminals = {v: k for k, v in terminals.items()}
