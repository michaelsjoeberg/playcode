#!/usr/local python3.11

import sys
from enum import Enum

# print(sys.version)

# tokens
PRINT       = "PRINT"
INTEGER     = "INTEGER"
PLUS        = "PLUS"
MINUS       = "MINUS"

RESERVED = [
    "PRINT"
]

def print_tree(tree, indent_level=-2):
    if isinstance(tree, list):
        for item in tree:
            print_tree(item, indent_level + 1)
    else:
        indent = '\t' * indent_level
        print(f"{indent}{tree}")

# **** token ****

class TokenType(Enum):
    KEYWORD     = 1
    INTEGER     = 2
    PLUS        = 3
    MINUS       = 4

class Token(object):
    def __init__(self, m_type, m_value):
        self.m_type = m_type
        self.m_value = m_value

    def __repr__(self):
        if self.m_value:
            return f"Token({self.m_type}, {self.m_value})"
        else:
            return f"Token({self.m_type})"

# **** lexer ****

def tokenize(source):
    tokens = []
    current_line = 1
    current_char = ''
    current_char_index = 0

    while current_char_index < len(source):
        current_char = source[current_char_index]
        match current_char:
            case ' ' | '\t' | '\r':
                current_char_index += 1
            case '\n':
                current_line += 1
                current_char_index += 1
            case '+':
                tokens.append(Token(TokenType.PLUS, PLUS))
                current_char_index += 1
            case '-':
                tokens.append(Token(TokenType.MINUS, MINUS))
                current_char_index += 1
            case _:
                if current_char.isdigit():
                    number = str(current_char)
                    current_char_index += 1
                    while source[current_char_index].isdigit() and current_char_index < len(source):
                        number += str(source[current_char_index])
                        current_char_index += 1
                    tokens.append(Token(TokenType.INTEGER, number))
                elif current_char.isalpha():
                    identifier = str(current_char)
                    current_char_index += 1
                    while source[current_char_index].isalpha() and current_char_index < len(source):
                        identifier += str(source[current_char_index])
                        current_char_index += 1
                    if identifier.upper() in RESERVED:
                        tokens.append(Token(TokenType.KEYWORD, identifier.upper()))
                else:
                    raise Exception("Unknown character:", current_char)

    return tokens

# **** parser ****

def parse(tokens):
    tree = []
    current_token = None
    current_token_index = 0

    while current_token_index < len(tokens):
        program, current_token_index = parse_program(tokens, current_token_index)
        tree.append(program)

    return tree

# program       ::= PRINT expression
def parse_program(tokens, current_token_index):
    program = []
    current_token = tokens[current_token_index]
    current_token_index += 1
    match current_token.m_type:
        case TokenType.KEYWORD:
            # PRINT
            if current_token.m_value == PRINT:
                program.append(current_token)
                # expression
                expression, current_token_index = parse_expression(tokens, current_token_index)
                program.append(expression)
            else:
                raise Exception("parse_program", "Unexpected token:", tokens[current_token_index])
        case _:
            raise Exception("parse_program", "Unexpected token:", tokens[current_token_index])

    return program, current_token_index

# expression    ::= factor ((PLUS | MINUS) factor)*
def parse_expression(tokens, current_token_index):
    expression = []
    
    # factor
    factor, current_token_index = parse_factor(tokens, current_token_index)
    expression = factor

    while current_token_index < len(tokens) and (tokens[current_token_index].m_type == TokenType.PLUS or tokens[current_token_index].m_type == TokenType.MINUS):
        current_token = tokens[current_token_index]
        current_token_index += 1
        match current_token.m_type:
            # PLUS
            case TokenType.PLUS:
                # factor
                factor, current_token_index = parse_factor(tokens, current_token_index)
                expression = [current_token, [expression, factor]]
            # MINUS
            case TokenType.MINUS:
                # factor
                factor, current_token_index = parse_factor(tokens, current_token_index)
                expression = [current_token, [expression, factor]]
            case _:
                raise Exception("parse_expression", "Unexpected token:", tokens[current_token_index])

    return expression, current_token_index

# factor        ::= INTEGER
def parse_factor(tokens, current_token_index):
    factor = []
    # INTEGER
    current_token = tokens[current_token_index]
    current_token_index += 1
    match current_token.m_type:
        case TokenType.INTEGER:
            factor = current_token
        case _:
            raise Exception("parse_factor", "Unexpected token:", tokens[current_token_index])

    return factor, current_token_index

# **** interpreter ****

def interpret(tree):
    result = ''
    node = tree
    if isinstance(node, list):
        left = node[0]
        right = node[1]
    else:
        left = node
        right = None
    # PRINT
    if left.m_value == PRINT:
        print(interpret(right))
    # PLUS
    elif left.m_value == PLUS:
        result = int(interpret(right[0])) + int(interpret(right[1]))
    # MINUS
    elif left.m_value == MINUS:
        result = int(interpret(right[0])) - int(interpret(right[1]))
    # NUMBER
    elif left.m_value.isdigit():
        return left.m_value
    else:
        raise Exception("interpret", "Unexpected node:", node)

    return result

# **** main ****

source = """
print 40 + 2
"""

tokens = tokenize(source)
# for token in tokens: print(token)

tree = parse(tokens)
# print(tree)
# print_tree(tree)

interpret(tree[0])
