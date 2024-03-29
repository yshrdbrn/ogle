import re
from ogle.lexer.language_spec import *


class LexToken(object):
    def __init__(self, token_type, value, line_number, line_position):
        self.type = token_type
        self.value = value
        self.line_number = line_number
        self.line_position = line_position

    def __str__(self):
        return 'LexToken({0}, {1}, {2}, {3})'.format(self.type, self.value, self.line_number, self.line_position)

    def __repr__(self):
        # return str(self)
        return str(self)

    def location(self):
        return '{}:{}'.format(self.line_number, self.line_position)

    def lexer_error_message(self):
        return 'Unknown identifier at {}.'.format(self.location())


class Lexer(object):
    def __init__(self, input_text):
        self.text = input_text
        self.text_len = len(input_text)
        self.pointer_pos = 0
        self.line_number = 1
        self.line_position = 1
        self.line_end = re.compile(line_end)
        self.comments = re.compile(comments)

        self.token_regex = {}
        for key, value in tokens.items():
            self.token_regex[key] = re.compile(value)

    def next_token(self):
        while self.pointer_pos < self.text_len:
            # Skip any whitespace
            if self.text[self.pointer_pos] in whitespace:
                self.line_position += 4 if self.text[self.pointer_pos] == '\t' else 1
                self.pointer_pos += 1
                continue

            # Check for line end character
            match = self.line_end.match(self.text, self.pointer_pos)
            if match:
                self._new_line_found(match)
                continue

            # Check for comments
            match = self.comments.match(self.text, self.pointer_pos)
            if match:
                self._comments_found(match)
                continue

            # Check for any regex matches in tokens dict
            for token, regex in self.token_regex.items():
                match = regex.match(self.text, self.pointer_pos)
                if match:
                    # Token found
                    token_obj = LexToken(token, match.group(), self.line_number, self.line_position)
                    # Check if the token is a reserved word
                    if token == 'ID' and token_obj.value in reserved_keywords.keys():
                        token_obj.type = reserved_keywords[token_obj.value]
                    self.pointer_pos = match.end()
                    self.line_position += len(match.group())
                    return token_obj

            # No match found. Check for special character matches
            if self.text[self.pointer_pos] in special_characters:
                token_obj = LexToken(self.text[self.pointer_pos],
                                     self.text[self.pointer_pos],
                                     self.line_number,
                                     self.line_position)
                self.pointer_pos += 1
                self.line_position += 1
                return token_obj

            # Error found in the next token
            # Find all the non-space characters and take them as one token
            match = re.compile(r'\S*').match(self.text, self.pointer_pos)
            token_obj = LexToken('ERROR', match.group(), self.line_number, self.line_position)
            self.pointer_pos = match.end()
            self.line_position += len(match.group())
            return token_obj

        # End of file reached
        return None

    def all_tokens(self):
        to_ret = []
        token = self.next_token()
        while token:
            to_ret.append(token)
            token = self.next_token()

        return to_ret

    def _new_line_found(self, match):
        self.line_number += len(match.group())
        self.line_position = 1
        self.pointer_pos = match.end()

    def _comments_found(self, match):
        self.line_number += match.group().count('\n')
        self.line_position = 1
        self.pointer_pos = match.end()
