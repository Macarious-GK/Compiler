# Project Description: Compiler Construction for MiniLang

## Project Overview

In this project, you'll build a compiler for a simple language called **MiniLang**. The goal is to learn how compilers work by creating one yourself, and to understand the key stages involved in turning a program into machine code.



# Stage 1: Lexical Analysis 

This script is a simple lexical analyzer for a mini programming language. It identifies and processes tokens such as keywords, variables, numbers, and symbols.

## Overview

1. **Recognizes Tokens**:
   - **Keywords**: `if`, `else`, `while`, `function`, `return`, etc.
   - **Identifiers**: Variable and function names.
   - **Numbers**: Numeric values like `10` or `42`.
   - **Operators**: Symbols like `+`, `-`, `*`, `/`, `=`, `>`.
   - **Delimiters**: Symbols like `;`, `,`, `()`, `{}`.
   - **Comments**: Both `//` single-line and `/* ... */` multi-line comments.
2. **Handles Errors**: Reports unrecognized symbols.
3. **Ignores**: Whitespace and comments for cleaner output.

## How It Works

- The `lex` function scans the input code using regular expressions.
- Tokens are matched and added to a list.
- Errors for unknown symbols are reported with line numbers.


### **Example Stage Output**
```cmd
function main() {
    x = 5;
    if (x > 10) {
        return x + 80;
    }
}
```

```plaintext
('KEYWORD', 'function')
('IDENTIFIER', 'main')
('DELIMITER', '(')
('DELIMITER', ')')
('DELIMITER', '{')
('IDENTIFIER', 'x')
('OPERATOR', '=')
('NUMBER', '5')
('DELIMITER', ';')
('KEYWORD', 'if')
('DELIMITER', '(')
('IDENTIFIER', 'x')
('OPERATOR', '>')
('NUMBER', '10')
('DELIMITER', ')')
('DELIMITER', '{')
('KEYWORD', 'return')
('IDENTIFIER', 'x')
('OPERATOR', '+')
('NUMBER', '80')
('DELIMITER', ';')
('DELIMITER', '}')
('DELIMITER', '}')
```
![Tokens](/Figures/Token.png)

# Stage 2: Syntax Analysis

In this stage, the parser checks if the tokens from lexical analysis follow the grammar rules of the language. It verifies the structure of the program, ensuring it is syntactically correct. The result is an Abstract Syntax Tree (AST) that represents the program’s structure.

## Overview

The main goal of syntax analysis is to verify that the tokens match the correct syntax of the language. The `Parser` class does this by analyzing the tokens one by one and building the program's structure.

### Parser Class

The `Parser` class handles the syntax analysis and creates the AST. It performs the following tasks:

#### 1. Token Management

- **Current Token**: The parser keeps track of the current token. The `current_token()` method retrieves the token at the current position.
- **Eat**: The `eat()` method consumes the expected token and moves to the next one. If the token doesn't match, it raises a `SyntaxError`.

#### 2. Parsing Methods

- **Program Parsing**: The parser checks if the program starts with a valid keyword (e.g., `function`) and verifies the function’s name, parameters, and body.
- **Statement Parsing**: It identifies different statements like `if`, `return`, or assignment and processes them accordingly.
- **If Statement**: If the statement is an `if`, it checks the condition and handles the associated blocks of code. It also parses the `else` block.
- **Return Statement**: The parser handles `return` by checking the expression being returned.
- **Assignment Statement**: For assignment statements, the parser verifies the left-hand side (variable) and the right-hand side (value).
- **Expression Parsing**: The parser checks for valid expressions that may include variables, numbers, or operations.
- **Term Parsing**: The parser identifies individual terms, such as identifiers or numbers, which make up expressions.

#### 3. Error Handling

- The parser raises a `SyntaxError` if it encounters an unexpected token or incorrect structure, ensuring the program follows the correct syntax.


### **Example Stage Output**
```cmd
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
```

```plaintext
AST: {
    "type": "program",
    "name": "main",
    "statements": [
        {
            "type": "assignment",
            "variable": "x",     
            "value": {
                "type": "number",
                "value": "5"     
            }
        },
        {
            "type": "if",
            "condition": {
                "type": "operator",
                "operator": ">",
                "left": {
                    "type": "identifier",
                    "name": "x"
                },
                "right": {
                    "type": "number",
                    "value": "10"
                }
            },
            "then": {
                "type": "return",
                "expression": {
                    "type": "operator",
                    "operator": "+",
                    "left": {
                        "type": "identifier",
                        "name": "x"
                    },
                    "right": {
                        "type": "number",
                        "value": "80"
                    }
                }
            },
            "else": {
                "type": "return",
                "expression": {
                    "type": "operator",
                    "operator": "-",
                    "left": {
                        "type": "identifier",
                        "name": "x"
                    },
                    "right": {
                        "type": "number",
                        "value": "70"
                    }
                }
            }
        }
    ]
}
```

![Tokens](/Figures/ASTree.png)

# Stage 3: Semantic Analysis 

## Overview

The `SemanticAnalyzer` class is designed to analyze an Abstract Syntax Tree (AST) to ensure that the program adheres to semantic rules. It checks for undeclared variables, type mismatches, and updates the symbol table with the types of declared variables. The class aims to detect logical and type-related errors in the code before execution.

## Main Components

### 1. **Symbol Table**
   - A dictionary that tracks variable declarations and their types. It helps in identifying whether variables are used before declaration and allows type checking for expressions.

### 2. **Error List**
   - A list that stores semantic errors detected during the analysis. These errors include issues like undeclared variables and type mismatches.

### 3. **Methods**
   - **`analyze(ast)`**: This method is the entry point for analyzing the AST. It starts by visiting the root of the AST, typically a `program` node, and then proceeds to check the program’s statements.
   - **`visit_program(node)`**: Handles the program node, analyzing the main statements.
   - **`visit_statement(node)`**: Dispatches the analysis to the appropriate method based on the statement type (e.g., `if`, `return`, or `assignment`).
   - **`visit_if_statement(node)`**: Analyzes `if` statements by checking the condition, `then`, and `else` blocks.
   - **`visit_return_statement(node)`**: Analyzes `return` statements and checks the returned expression.
   - **`visit_assignment_statement(node)`**: Analyzes assignment statements, ensuring the variable is declared before use and checking the type of the assigned value.
   - **`visit_expression(node)`**: Handles expressions, checking identifiers, numbers, and operators. It ensures variables are declared before use and checks for type consistency in operations.

## Workflow

1. **AST Traversal**: The class traverses the AST starting from the `program` node. It processes each statement by delegating the work to specific methods based on the type of statement (`if`, `return`, `assignment`).
  
2. **Symbol Table Updates**: As the analysis progresses, the symbol table is updated with variable types, which are used for type checking.

3. **Error Detection**: The class identifies errors related to:
   - **Undeclared Variables**: If a variable is used before being declared, an error is recorded.
   - **Type Mismatches**: If operands of an operation have incompatible types (e.g., adding a number and a string), a semantic error is generated.

4. **Error Reporting**: All detected semantic errors are stored in a list and can be retrieved after the analysis is complete.

## Example Scenario

Consider the following scenario:
- A program declares a variable `x` and assigns it a value.
- An `if` statement checks whether `x` is greater than 10 and returns different results based on the condition.
- The semantic analyzer will ensure that `x` is declared before it is used, and that the types of values being added or subtracted are consistent (e.g., both `x` and the number 80 must be of the same type).

## Conclusion

The `SemanticAnalyzer` class is a critical tool in the process of checking and ensuring that the program is semantically correct. By verifying variable declarations, types, and logical consistency, it helps prevent runtime errors related to variable misuse and type incompatibility.

![Tokens](/Figures/errors.png)

# Stage 4: Intermediate Code Generation

The `IntermediateCodeGenerator` class creates intermediate code from an Abstract Syntax Tree (AST). This code is an intermediate step in compiling a program, making it easier to manipulate before converting it to machine code.

## Class Structure

### 1. **Attributes**
- **temp_counter**: A counter used to generate temporary variable names for intermediate computations. This ensures each temporary variable used in the intermediate code has a unique name.
- **label_counter**: A counter used to generate unique labels, typically used in control flow statements like loops and conditionals.
- **ir_code**: A list that stores the generated intermediate code. This list is built as the program is processed and will eventually be returned as the final output.

### 2. **Methods**

#### `__init__(self)`
Initializes the counters and the `ir_code` list.

#### `generate_temp(self)`
Generates a new temporary variable name, e.g., `t0`, `t1`, etc.

#### `generate_label(self)`
Generates a new label name, e.g., `L0`, `L1`, etc.

#### `generate_ir(self, ast)`
Main method to generate the intermediate code from the AST by visiting each statement.

#### `visit_statement(self, node)`
Visits different types of statement nodes (if, return, assignment, declaration) and calls the appropriate method for each.

#### `visit_declaration_statement(self, node)`
Handles variable declarations, generating code to declare and assign values to variables.

#### `visit_if_statement(self, node)`
Handles `if` statements, generating code for conditional branching.

#### `visit_return_statement(self, node)`
Handles `return` statements, generating code to return an expression.

#### `visit_assignment_statement(self, node)`
Handles assignment statements, generating code to assign values to variables.

#### `visit_expression(self, node)`
Processes expressions (like numbers, variables, or operators) and generates code for them.



## **Example**
```cmd
function main() {
    x = 5;
    if (x > 0) {
        return x;
    } else {
        return 0;
    }
}
```

```plaintext
Intermediate Code: [
    'declare x', 
    't0 = 5', 
    'x = t0', 
    't1 = x > 0', 
    'if t1 goto L0', 
    'goto L1', 
    'L0:', 
    'return x', 
    'goto L1', 
    'L1:', 
    'return 0']
```