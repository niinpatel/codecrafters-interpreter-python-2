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

    def scan(self):
        tokens = []

        while self.current < len(self.source_code):
            self.current += 1
            char = self.source_code[self.current - 1]
            if char == " ":
                continue
            if char == "\n":
                continue
            if char == "(":
                tokens.append(Token("LEFT_PAREN", "(", None))
            elif char == ")":
                tokens.append(Token("RIGHT_PAREN", ")", None))

        tokens.append(Token("EOF", "", None))
        return tokens


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
        tokens = Scanner(file_contents).scan()
        for token in tokens:
            print(token)


if __name__ == "__main__":
    main()
