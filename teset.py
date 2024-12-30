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

# Parser class
class Parser:
    # Implementation of Parser class...
    # (You can use the existing implementation from your question)
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

# SemanticAnalyzer class
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}  # Dictionary to track variable declarations and their types
        self.errors = []  # List to store semantic errors

    def analyze(self, ast):
        """Analyze the AST for semantic correctness."""
        if ast['type'] == 'program':
            self.visit_program(ast)
        return self.errors

    def visit_program(self, node):
        """Visit the program node."""
        print("Analyzing program...")
        self.visit_statement(node['statements'][0])  # Start from the first statement

    def visit_statement(self, node):
        """Visit a statement node."""
        if node['type'] == 'if':
            self.visit_if_statement(node)
        elif node['type'] == 'return':
            self.visit_return_statement(node)
        elif node['type'] == 'assignment':
            self.visit_assignment_statement(node)

    def visit_if_statement(self, node):
        """Visit an if statement."""
        print("Analyzing if statement...")
        self.visit_expression(node['condition'])  # Check the condition
        self.visit_statement(node['then'])        # Check the 'then' block
        if node['else']:
            self.visit_statement(node['else'])    # Check the 'else' block

    def visit_return_statement(self, node):
        """Visit a return statement."""
        print("Analyzing return statement...")
        self.visit_expression(node['expression'])

    def visit_assignment_statement(self, node):
        """Visit an assignment statement."""
        print("Analyzing assignment statement...")
        variable = node['variable']
        expression = node['value']

        # Check if the variable is already declared
        if variable not in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{variable}' used before declaration.")

        # Analyze the expression
        expr_type = self.visit_expression(expression)

        # Update the variable type in the symbol table
        self.symbol_table[variable] = expr_type

    def visit_expression(self, node):
        """Visit an expression node."""
        if node['type'] == 'identifier':
            var_name = node['name']
            if var_name not in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration.")
                return None
            return self.symbol_table[var_name]  # Return the variable's type

        elif node['type'] == 'number':
            return 'int'  # Assume numbers are integers

        elif node['type'] == 'operator':
            left_type = self.visit_expression(node['left'])
            right_type = self.visit_expression(node['right'])

            # Check for type mismatch
            if left_type != right_type:
                self.errors.append(f"Semantic Error: Type mismatch in operation '{node['operator']}' between '{left_type}' and '{right_type}'.")
                return None

            return left_type  # Return the resulting type (e.g., 'int' for arithmetic)

        return None


code_valid = '''
function main() {
    if (x > 10) {
        return x + 80;
    } else {
        return x - 70;
    }
    x = 5;
}
'''

tokens_valid = lex(code_valid)
print("Tokens (Valid Code):", tokens_valid)  # Debug: print the tokens

parser_valid = Parser(tokens_valid)
try:
    ast_valid = parser_valid.parse_program()
    print("AST (Valid Code):", json.dumps(ast_valid, indent=4))
except SyntaxError as e:
    print(f"SyntaxError (Valid Code): {e}")
