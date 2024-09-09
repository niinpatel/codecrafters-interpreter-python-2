from abc import ABC, abstractmethod
import sys


class Token:
    def __init__(self, type, lexeme, literal):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal

    def __repr__(self) -> str:
        return f"{self.type} {self.lexeme} {"null" if self.literal is None else self.literal}"


class Scanner:
    def __init__(self, source_code) -> None:
        self.source_code = source_code
        self.current = 0
        self.line = 1
        self.had_error = False
        
    def scan(self):
        tokens = []

        while self.current < len(self.source_code):
            self.current += 1
            char = self.source_code[self.current - 1]
            if char == "(":
                tokens.append(Token("LEFT_PAREN", "(", None))
            elif char == ")":
                tokens.append(Token("RIGHT_PAREN", ")", None))
            elif char == "{":
                tokens.append(Token("LEFT_BRACE", "{", None))
            elif char == "}":
                tokens.append(Token("RIGHT_BRACE", "}", None))
            elif char == "*":
                tokens.append(Token("STAR", "*", None))
            elif char == ".":
                tokens.append(Token("DOT", ".", None))
            elif char == ",":
                tokens.append(Token("COMMA", ",", None))
            elif char == "+":
                tokens.append(Token("PLUS", "+", None))
            elif char == "-":
                tokens.append(Token("MINUS", "-", None))
            elif char == ";":
                tokens.append(Token("SEMICOLON", ";", None))
            elif char == "/":
                # slash can either be division or a comment
                if self.current < len(self.source_code) and self.source_code[self.current] == "/":
                    while self.current < len(self.source_code) and self.source_code[self.current] != "\n":
                        self.current += 1
                else:
                    tokens.append(Token("SLASH", "/", None))

            elif char == "=":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("EQUAL_EQUAL", "==", None))
                    self.current += 1
                else:
                    tokens.append(Token("EQUAL", "=", None))
            elif char == "!":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("BANG_EQUAL", "!=", None))
                    self.current += 1
                else:
                    tokens.append(Token("BANG", "!", None))
            elif char == "<":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("LESS_EQUAL", "<=", None))
                    self.current += 1
                else:
                    tokens.append(Token("LESS", "<", None))
            elif char == ">":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("GREATER_EQUAL", ">=", None))
                    self.current += 1
                else:
                    tokens.append(Token("GREATER", ">", None))
            elif char == "\"":
                string_start = self.current
                while self.current < len(self.source_code) and self.source_code[self.current] != '"':
                    self.current += 1
                if self.current >= len(self.source_code):
                    print(f"[line {self.line}] Error: Unterminated string.", file=sys.stderr)
                    self.had_error = True
                    continue
                self.current += 1
                string_end = self.current - 1
                string_literal = self.source_code[string_start:string_end]
                tokens.append(Token("STRING", f'"{string_literal}"', string_literal))
            elif char.isdigit():
                number_start = self.current - 1
                while self.current < len(self.source_code) and (self.source_code[self.current].isdigit() or self.source_code[self.current] == "."):
                    self.current += 1
                number_end = self.current
                number_literal = self.source_code[number_start:number_end]
                tokens.append(Token("NUMBER", number_literal, float(number_literal)))
            elif char.isalpha() or char == "_":
                identifier_start = self.current - 1
                while self.current < len(self.source_code) and (self.source_code[self.current].isalnum() or self.source_code[self.current] == "_"):
                    self.current += 1
                identifier_end = self.current
                identifier_literal = self.source_code[identifier_start:identifier_end]
                if identifier_literal in ["and", "class", "else", "false", "for", "fun", "if", "nil", "or", "print", "return", "super", "this", "true", "var", "while"]:
                    # reserved words
                    tokens.append(Token(identifier_literal.upper(), identifier_literal, None))
                else:
                    tokens.append(Token("IDENTIFIER", identifier_literal, None))
            elif char == " ":
                pass
            elif char == "\t":
                pass
            elif char == "\r":
                pass
            elif char == "\f":
                pass
            elif char == "\n":
                self.line += 1
            else:
                print(f"[line {self.line}] Error: Unexpected character: {char}", file=sys.stderr)
                self.had_error = True
                
        tokens.append(Token("EOF", "", None))
        return tokens, self.had_error
    

class Expression(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def evaluate(self):
        pass

class LiteralExpression(Expression):
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        if self.value is True: return "true"
        if self.value is False: return "false"
        if self.value is None: return "nil"
        return f"{self.value}"

    def evaluate(self):
        return self.value
    
class GroupExpression(Expression):
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def __str__(self) -> str:
        return f"(group {self.expression})"
    
    def evaluate(self):
        return self.expression.evaluate()
    
class UnaryExpression(Expression):
    def __init__(self, operator: Token, expression: Expression) -> None:
        self.operator = operator
        self.expression = expression

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.expression})"

    def evaluate(self):
        value = self.expression.evaluate()
        if self.operator.type == "MINUS":
            if not isinstance(value, float):
                print(f"Operand must be a number.", file=sys.stderr)
                exit(70)
            return -1 * value
        else:
            return not value


class BinaryExpression(Expression):
    def __init__(self, operator: Token, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.left} {self.right})"
    
    def evaluate(self):
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()
        if self.operator.type == "PLUS":
            if not isinstance(left_value, (float, str)) or not isinstance(right_value, (float, str)) or type(left_value) != type(right_value):
                print("Operands must be two numbers or two strings.", file=sys.stderr)
                exit(70)
            return left_value + right_value
        if self.operator.type == "MINUS":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)

            return left_value - right_value
        if self.operator.type == "STAR":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value * right_value
        if self.operator.type == "SLASH":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value / right_value
        if self.operator.type == "BANG_EQUAL":
            return left_value != right_value
        if self.operator.type == "EQUAL_EQUAL":
            return left_value == right_value
        if self.operator.type == "GREATER":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)

            return left_value > right_value
        if self.operator.type == "GREATER_EQUAL":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)

            return left_value >= right_value
        if self.operator.type == "LESS":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)

            return left_value < right_value
        if self.operator.type == "LESS_EQUAL":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)

            return left_value <= right_value

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse_primary(self):
        self.current += 1
        token = self.tokens[self.current - 1]
        if token.type == "TRUE":
            return LiteralExpression(True)
        if token.type == "FALSE":
            return LiteralExpression(False)
        if token.type == "NIL":
            return LiteralExpression(None)
        if token.type in ["NUMBER", "STRING"]:
            return LiteralExpression(token.literal)
        if token.type == "LEFT_PAREN":
            expression = self.parse_expression()
            self.consume("RIGHT_PAREN")
            return GroupExpression(expression)
        
        print(f"Error at {token.lexeme}: Expect expression.", file=sys.stderr)
        exit(65)
    
    def parse_equality(self):
        expression = self.parse_comparison()

        while self.current < len(self.tokens):
            token = self.tokens[self.current]
            if token.type not in ["BANG_EQUAL", "EQUAL_EQUAL"]:
                break
            self.current += 1
            right = self.parse_comparison()
            expression = BinaryExpression(token, expression, right)
        
        return expression

    def parse_comparison(self):
        expression = self.parse_term()

        while self.current < len(self.tokens):
            token = self.tokens[self.current]
            if token.type not in ["GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"]:
                break
            self.current += 1
            right = self.parse_term()
            expression = BinaryExpression(token, expression, right)

        return expression


    def parse_term(self):
        expression = self.parse_factor()

        while self.current < len(self.tokens):
            token = self.tokens[self.current]
            if token.type not in ["PLUS", "MINUS"]:
                break
            self.current += 1
            right = self.parse_factor()
            left = expression
            expression = BinaryExpression(token, left, right)

        return expression
        
    def parse_factor(self):
        expression = self.parse_unary()

        while self.current < len(self.tokens):
            token = self.tokens[self.current]
            if token.type not in ["STAR", "SLASH"]:
                break
            self.current += 1
            right = self.parse_unary()
            left = expression
            expression = BinaryExpression(token, left, right)

        return expression
        
    def parse_unary(self):
        token = self.tokens[self.current]
        if token.type in ["BANG", "MINUS"]:
            self.current += 1
            expression = self.parse_unary()
            return UnaryExpression(token, expression)
        return self.parse_primary()


    def parse_expression(self):
        return self.parse_equality()
    

    def parse_statements(self):
        statements = []
        while self.tokens[self.current].type != "EOF":
            statement = self.parse_statement()
            statements.append(statement)
        return statements

    def parse_statement(self):
        token = self.tokens[self.current] 
        if token.type == "PRINT":
            self.current += 1
            expression = self.parse_expression()
            self.consume("SEMICOLON")
            return PrintStatement(expression)
        
        expression = self.parse_expression()
        self.consume("SEMICOLON");
        return ExpressionStatement(expression)

    def consume(self, type):
        # TODO: check if there is actually a right paren
        self.current += 1


class Statement(ABC):
    @abstractmethod
    def execute(self): pass


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self):
        print(lox_representation(self.expression.evaluate()))

class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression
    
    def execute(self):
        self.expression.evaluate()

def lox_representation(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "nil"
    if isinstance(value, str):
        return value
    if value.is_integer():
        return int(value)
    return value

def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command == "tokenize":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            for token in tokens:
                print(token)
            if had_error:
                exit(65)
            return
        
    if command == "parse":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            if had_error:
                exit(65)
            expression = Parser(tokens).parse_expression()
            print(expression)
            return

    if command == "evaluate":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            if had_error: exit(65)
            expression = Parser(tokens).parse_expression()
            print(lox_representation(expression.evaluate()))
            return
        
    if command == "run":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            if had_error: exit(65)
            statements = Parser(tokens).parse_statements()
            for statement in statements:
                statement.execute()
            return

    

    print(f"Unknown command: {command}", file=sys.stderr)
    exit(1)




if __name__ == "__main__":
    main()
