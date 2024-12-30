import re

# Define token patterns
token_patterns = {
    'KEYWORD': r'\b(if|else|while|function|return|input|output)\b',
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    'NUMBER': r'\b\d+\b',
    'OPERATOR': r'[+\-*/=<>!]',
    'DELIMITER': r'[;(),{}]',  # Include curly braces
    'WHITESPACE': r'\s+',
    'COMMENT': r'//.*|/\*.*?\*/',  # Single-line and multi-line comments
    'MISMATCH': r'.',  # Any other character that doesn't match the above
}

# Compile the regex patterns
token_regex = '|'.join(f'(?P<{key}>{pattern})' for key, pattern in token_patterns.items())

# Lexical analyzer function
def lex(code):
    tokens = []
    line_number = 1
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        
        # Skip whitespace and comments
        if kind == 'WHITESPACE' or kind == 'COMMENT':
            continue

        # Handle unrecognized symbols
        elif kind == 'MISMATCH':
            print(f"Error: Unrecognized symbol '{value}' at line {line_number}")
            continue

        # Append token to the list
        tokens.append((kind, value))
        
        # Increment line number for each newline character
        line_number += value.count('\n')
        
    return tokens

# Example usage
mini_lang_code = '''
function main() {
    x = 5;
    if (x > 10) {
        return x + 80;
    }
}
'''

tokens = lex(mini_lang_code)
for token in tokens:
    print(token)
