
import re
import json

# Tokenizer function (from Stage 1)
def lex(code):
    token_patterns = {
        'KEYWORD': r'\b(if|else|while|function|return|input|output)\b',
        'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
        'NUMBER': r'\b\d+\b',
        'OPERATOR': r'[+\-*/=<>!]',
        'DELIMITER': r'[;(),{}]',
        'WHITESPACE': r'\s+',

        'COMMENT': r'//.*|/\*.*?\*/',  # Single-line and multi-line comments
        'MISMATCH': r'.',  # Any other character that doesn't match the above
    }
    
    token_regex = '|'.join(f'(?P<{key}>{pattern})' for key, pattern in token_patterns.items())
    tokens = []
    line_number = 1
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        
        if kind == 'WHITESPACE' or kind == 'COMMENT':
            continue
        elif kind == 'MISMATCH':
            print(f"Error: Unrecognized symbol '{value}' at line {line_number}")
            continue
        tokens.append((kind, value))
        line_number += value.count('\n')
    return tokens

# Parser implementation
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        token = self.current_token()
        if token and token[0] == token_type:
            self.pos += 1
            return token
        raise SyntaxError(f"Unexpected token: {token}, expected {token_type}")

    def parse_program(self):
        print("Parsing program...")
        token = self.eat('KEYWORD')
        if token and token[1] == 'function':
            identifier = self.eat('IDENTIFIER')
            self.eat('DELIMITER')  # '('
            self.eat('DELIMITER')  # ')'
            self.eat('DELIMITER')  # '{'
            
            statements = []
            while self.current_token() and self.current_token()[0] != 'DELIMITER' or self.current_token()[1] != '}':
                statement = self.parse_statement()
                statements.append(statement)
            
            self.eat('DELIMITER')  # '}'
            return {'type': 'program', 'name': identifier[1], 'statements': statements}
        raise SyntaxError("Program must start with a 'function' keyword")

    def parse_statement(self):
        print("Parsing statement...")
        token = self.current_token()
        if token and token[1] == 'if':
            return self.parse_if_statement()
        elif token and token[1] == 'return':
            return self.parse_return_statement()
        elif token and token[0] == 'IDENTIFIER':
            return self.parse_assignment_statement()
        raise SyntaxError(f"Unexpected token in statement: {token}")

    def parse_if_statement(self):
        print("Parsing if statement...")
        self.eat('KEYWORD')  # 'if'
        self.eat('DELIMITER')  # '('
        expr = self.parse_expression()
        self.eat('DELIMITER')  # ')'
        self.eat('DELIMITER')  # '{'
        stmt1 = self.parse_statement()
        self.eat('DELIMITER')  # '}'
        self.eat('KEYWORD')  # 'else'
        self.eat('DELIMITER')  # '{'
        stmt2 = self.parse_statement()
        self.eat('DELIMITER')  # '}'
        return {'type': 'if', 'condition': expr, 'then': stmt1, 'else': stmt2}

    def parse_return_statement(self):
        print("Parsing return statement...")
        self.eat('KEYWORD')  # 'return'
        expr = self.parse_expression()
        self.eat('DELIMITER')  # ';'
        return {'type': 'return', 'expression': expr}

    def parse_assignment_statement(self):
        print("Parsing assignment statement...")
        identifier = self.eat('IDENTIFIER')
        self.eat('OPERATOR')  # '='
        expr = self.parse_expression()
        self.eat('DELIMITER')  # ';'
        return {'type': 'assignment', 'variable': identifier[1], 'value': expr}

    def parse_expression(self):
        print("Parsing expression...")
        left = self.parse_term()
        token = self.current_token()
        while token and token[0] == 'OPERATOR':
            operator = self.eat('OPERATOR')
            right = self.parse_term()
            left = {'type': 'operator', 'operator': operator[1], 'left': left, 'right': right}
            token = self.current_token()
        return left

    def parse_term(self):
        token = self.current_token()
        if token and token[0] == 'IDENTIFIER':
            return {'type': 'identifier', 'name': self.eat('IDENTIFIER')[1]}
        elif token and token[0] == 'NUMBER':
            return {'type': 'number', 'value': self.eat('NUMBER')[1]}
        raise SyntaxError(f"Unexpected token in term: {token}")

# Example usage
code = '''
function main() {
    
    x = 5;
    if (x > 10) {
        return x + 80;
    }else{
        return x - 70;
    }
}
'''

tokens = lex(code)
print("Tokens:", tokens)  # Debug: print the tokens

parser = Parser(tokens)
ast = parser.parse_program()

# Print the generated AST
print("AST:", json.dumps(ast, indent=4))
