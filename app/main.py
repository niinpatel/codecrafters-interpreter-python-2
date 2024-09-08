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
                tokens.append(Token("SLASH", "/", None))
            elif char == "=":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("EQUAL_EQUAL", "==", None))
                    self.current += 1
                else:
                    tokens.append(Token("EQUAL", "=", None))
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


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()
        tokens, had_error = Scanner(file_contents).scan()
        for token in tokens:
            print(token)
        if had_error:
            exit(65)


if __name__ == "__main__":
    main()
