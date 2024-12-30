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
        self.visit_statement(node['statement'])

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
