import re

def lex(code):
    token_patterns = {
        'KEYWORD': r'\b(if|else|while|function|return|input|output)\b',
        'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
        'NUMBER': r'\b\d+\b',
        'OPERATOR': r'[+\-*/=<>!]',
        'DELIMITER': r'[;(),{}]',
        'WHITESPACE': r'\s+',
        'COMMENT': r'//.*|/\*.*?\*/',
        'MISMATCH': r'.',
    }
    
    token_regex = '|'.join(f'(?P<{key}>{pattern})' for key, pattern in token_patterns.items())
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'WHITESPACE' or kind == 'COMMENT':
            continue
        elif kind == 'MISMATCH':
            print(f"Error: Unrecognized symbol '{value}'")
            continue
        tokens.append((kind, value))
    return tokens
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
        return None

    def parse_program(self):
        token = self.eat('KEYWORD')
        if token and token[1] == 'function':
            self.eat('KEYWORD')
            identifier = self.eat('IDENTIFIER')
            self.eat('DELIMITER')
            self.eat('DELIMITER')
            self.eat('DELIMITER')
            
            statements = self.parse_statements()
            self.eat('DELIMITER')
            return {'type': 'program', 'name': identifier[1], 'statements': statements}
        return None

    def parse_statements(self):
        statements = []
        token = self.current_token()
        while token and token[0] != 'DELIMITER':
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            token = self.current_token()
        return statements

    def parse_statement(self):
        token = self.current_token()

        if token and token[0] == 'IDENTIFIER' and token[1] in ['int', 'float', 'string']:
            return self.parse_declaration_statement()
        if token and token[1] == 'if':
            return self.parse_if_statement()
        if token and token[1] == 'return':
            return self.parse_return_statement()
        if token and token[0] == 'IDENTIFIER':
            return self.parse_assignment_statement()
        return None

    def parse_declaration_statement(self):
        var_type = self.eat('IDENTIFIER')
        variable = self.eat('IDENTIFIER')
        self.eat('OPERATOR')
        value = self.parse_expression()
        self.eat('DELIMITER')
        return {'type': 'declaration', 'var_type': var_type[1], 'variable': variable[1], 'value': value}

    def parse_if_statement(self):
        self.eat('KEYWORD')
        self.eat('DELIMITER')
        condition = self.parse_expression()
        self.eat('DELIMITER')
        self.eat('DELIMITER')
        then_block = self.parse_statements()
        self.eat('DELIMITER')
        self.eat('KEYWORD')
        self.eat('DELIMITER')
        else_block = self.parse_statements()
        self.eat('DELIMITER')
        return {'type': 'if', 'condition': condition, 'then': then_block, 'else': else_block}

    def parse_return_statement(self):
        self.eat('KEYWORD')
        expression = self.parse_expression()
        self.eat('DELIMITER')
        return {'type': 'return', 'expression': expression}

    def parse_assignment_statement(self):
        variable = self.eat('IDENTIFIER')
        self.eat('OPERATOR')
        value = self.parse_expression()
        self.eat('DELIMITER')
        return {'type': 'assignment', 'variable': variable[1], 'value': value}

    def parse_expression(self):
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
        return None
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.errors = []

    def analyze(self, ast):
        if ast['type'] == 'program':
            self.visit_program(ast)
        return self.errors

    def visit_program(self, node):
        for statement in node['statements']:
            self.visit_statement(statement)

    def visit_statement(self, node):
        if node['type'] == 'if':
            self.visit_if_statement(node)
        elif node['type'] == 'return':
            self.visit_return_statement(node)
        elif node['type'] == 'assignment':
            self.visit_assignment_statement(node)
        elif node['type'] == 'declaration':
            self.visit_declaration_statement(node)

    def visit_declaration_statement(self, node):
        var_type = node['var_type']
        variable = node['variable']
        self.symbol_table[variable] = var_type

        value_type = self.visit_expression(node['value'])
        if value_type != var_type:
            self.errors.append(f"Semantic Error: Type mismatch in declaration of '{variable}'.")

    def visit_if_statement(self, node):
        self.visit_expression(node['condition'])
        for stmt in node['then']:
            self.visit_statement(stmt)
        for stmt in node['else']:
            self.visit_statement(stmt)

    def visit_return_statement(self, node):
        self.visit_expression(node['expression'])

    def visit_assignment_statement(self, node):
        variable = node['variable']
        if variable not in self.symbol_table:
            self.errors.append(f"Semantic Error: Variable '{variable}' used before declaration.")
        self.visit_expression(node['value'])

    def visit_expression(self, node):
        if node['type'] == 'identifier':
            var_name = node['name']
            if var_name not in self.symbol_table:
                self.errors.append(f"Semantic Error: Variable '{var_name}' used before declaration.")
            return self.symbol_table.get(var_name)
        elif node['type'] == 'number':
            return 'int'
        elif node['type'] == 'operator':
            left_type = self.visit_expression(node['left'])
            right_type = self.visit_expression(node['right'])
            if left_type != right_type:
                self.errors.append(f"Semantic Error: Type mismatch in operation '{node['operator']}' between '{left_type}' and '{right_type}'.")
            return left_type
        return None
class IntermediateCodeGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.ir_code = []

    def generate_temp(self):
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def generate_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def generate_ir(self, ast):
        """ Generate intermediate code from the AST. """
        if ast['type'] == 'program':
            # Iterate over all statements in the program
            for statement in ast['statements']:
                self.visit_statement(statement)
        return self.ir_code

    def visit_statement(self, node):
        """ Visit a statement node. """
        if node['type'] == 'if':
            self.visit_if_statement(node)
        elif node['type'] == 'return':
            self.visit_return_statement(node)
        elif node['type'] == 'assignment':
            self.visit_assignment_statement(node)
        elif node['type'] == 'declaration':
            self.visit_declaration_statement(node)

    def visit_declaration_statement(self, node):
        var_type = node['var_type']
        variable = node['variable']
        self.ir_code.append(f"declare {var_type} {variable}")
        if node['value']['type'] == 'number':
            value = node['value']['value']
            temp = self.generate_temp()
            self.ir_code.append(f"{temp} = {value}")
            self.ir_code.append(f"{variable} = {temp}")

    def visit_if_statement(self, node):
        condition = self.visit_expression(node['condition'])
        true_label = self.generate_label()
        false_label = self.generate_label()
        self.ir_code.append(f"if {condition} goto {true_label}")
        self.ir_code.append(f"goto {false_label}")
        self.ir_code.append(f"{true_label}:")
        for stmt in node['then']:
            self.visit_statement(stmt)
        self.ir_code.append(f"goto {false_label}")
        self.ir_code.append(f"{false_label}:")
        for stmt in node['else']:
            self.visit_statement(stmt)

    def visit_return_statement(self, node):
        expression = self.visit_expression(node['expression'])
        self.ir_code.append(f"return {expression}")

    def visit_assignment_statement(self, node):
        variable = node['variable']
        value = self.visit_expression(node['value'])
        self.ir_code.append(f"{variable} = {value}")

    def visit_expression(self, node):
        """ Visit an expression node. """
        if node['type'] == 'identifier':
            return node['name']
        elif node['type'] == 'number':
            return node['value']
        elif node['type'] == 'operator':
            left = self.visit_expression(node['left'])
            right = self.visit_expression(node['right'])
            temp = self.generate_temp()
            self.ir_code.append(f"{temp} = {left} {node['operator']} {right}")
            return temp
class OptimizedIntermediateCodeGenerator(IntermediateCodeGenerator):
    def __init__(self):
        super().__init__()

    def optimize_ir(self, ir_code):
        optimized_code = []
        for line in ir_code:
            # Inline constant assignments
            if " = " in line:
                lhs, rhs = line.split(" = ")
                if rhs.isdigit():  # Direct assignment
                    optimized_code.append(f"{lhs} = {rhs}")
                elif lhs in rhs:  # Remove self-assignments
                    continue
                else:
                    optimized_code.append(line)
            else:
                optimized_code.append(line)
        
        # Remove unnecessary gotos to the next line (e.g., redundant jumps)
        final_code = []
        for i, line in enumerate(optimized_code):
            if "goto" in line and i + 1 < len(optimized_code) and line.split(" ")[1] + ":" == optimized_code[i + 1]:
                continue
            final_code.append(line)
        
        return final_code

    def generate_ir(self, ast):
        # Generate initial IR
        ir_code = super().generate_ir(ast)
        # Apply optimizations
        return self.optimize_ir(ir_code)
class AssemblyCodeGenerator:
    def __init__(self):
        self.register_counter = 0

    def generate_register(self):
        register_name = f"R{self.register_counter}"
        self.register_counter += 1
        return register_name

    def generate_assembly(self, ir_code):
        assembly_code = []

        for line in ir_code:
            if "declare" in line:  # Handle declarations
                _, var_type, var_name = line.split()
                assembly_code.append(f"declare {var_type} {var_name}")

            elif "=" in line:  # Handle assignments
                lhs, rhs = line.split(" = ")
                if rhs.isdigit():  # Direct constant assignment
                    assembly_code.append(f"LOAD {rhs}, {lhs}")
                elif " + " in rhs or " - " in rhs:  # Arithmetic operations
                    op = "+" if "+" in rhs else "-"
                    operand1, operand2 = rhs.split(f" {op} ")
                    temp_reg = self.generate_register()
                    assembly_code.append(f"LOAD {operand1}, {temp_reg}")
                    assembly_code.append(f"{'ADD' if op == '+' else 'SUB'} {temp_reg}, {operand2}")
                    assembly_code.append(f"STORE {temp_reg}, {lhs}")
                else:  # Simple assignments
                    assembly_code.append(f"LOAD {rhs}, {lhs}")

            elif "if" in line:  # Handle conditional jumps
                condition, label = line.split(" goto ")
                # Corrected to compare x directly to 10
                assembly_code.append(f"CMP {condition}, 10")
                assembly_code.append(f"IFGT {label}")

            elif "goto" in line:  # Handle unconditional jumps
                _, label = line.split()
                assembly_code.append(f"GOTO {label}")

            elif "return" in line:  # Handle return statements
                _, var = line.split()
                assembly_code.append(f"RETURN {var}")

            elif ":" in line:  # Handle labels
                assembly_code.append(line)

        return assembly_code

import json  # Ensure json module is imported
# Example input
code = '''
function main() {
    int x = 5;
    if (x > 10) {
        return x + 1;
    } else {
        return x - 1;
    }
}
'''

# Tokenization
tokens = lex(code)
print("Tokens:", tokens)

# Parsing
parser = Parser(tokens)
ast = parser.parse_program()
print("AST:", json.dumps(ast, indent=4))

# Semantic Analysis
semantic_analyzer = SemanticAnalyzer()
errors = semantic_analyzer.analyze(ast)

if errors:
    print("\nSemantic Errors:")
    for error in errors:
        print(error)
else:
    print("\nNo Semantic Errors: Program is valid!")

# Stage 4: Intermediate Code Generation
ir_generator = OptimizedIntermediateCodeGenerator()
ir_code = ir_generator.generate_ir(ast)

print("\nOptimized Intermediate Code:")
for line in ir_code:
    print(line)

# Stage 5: Assembly-like Code Generation
assembly_generator = AssemblyCodeGenerator()
assembly_code = assembly_generator.generate_assembly(ir_code)

print("\nGenerated Assembly Code:")
for line in assembly_code:
    print(line)
