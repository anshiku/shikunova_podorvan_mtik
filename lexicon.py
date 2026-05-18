import re
from dataclasses import dataclass

@dataclass
class Token:
    token_type: str
    lexeme: str

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def has_unclosed_comment(text):
    return text.count("/*") != text.count("*/")

def preprocess(text):
    # Удаление комментариев
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)

    lines = []
    for line in text.splitlines():
        line = re.sub(r"^[ \t]+|[ \t]+$", "", line)
        line = re.sub(r"[ \t]{2,}", " ", line)
        if line:
            lines.append(line)

    return "\n".join(lines)

KEYWORDS = {
    "include",
    "using",
    "namespace",
    "int",
    "return",
    "for"
}

BOOLEAN_CONSTANTS = {
    "true",
    "false"
}

OPERATORS = {
    "<<", ">>", "++", "--",
    "==", "!=", "<=", ">=",
    "&&", "||",
    "=", "+", "-", "*", "/", "<", ">",
    "!", "&", "|"
}

DELIMITERS = {
    "#", ";", ",", "(", ")", "{", "}"
}

def is_identifier_start(ch):
    # Может ли символ быть первым символом идентификатора
    return ch.isalpha() or ch == "_"

def is_identifier_char(ch):
    # Может ли символ быть частью идентификатор
    return ch.isalnum() or ch == "_"

def read_string(text, start):
    quote = text[start]
    i = start + 1

    while i < len(text):
        # Экранирование символов (\')
        if text[i] == "\\":
            i += 2
            continue

        if text[i] == quote:
            # возвращает найденную строку, новую позицию анализа, ошибку None
            return text[start:i + 1], i + 1, None
        
        i += 1

    return text[start:], len(text), f"Ошибка: незакрытый строковый литерал: {text[start:]}"

def read_number(text, start):
    i = start

    while i < len(text) and (text[i].isalnum() or text[i] in "._"):
        i += 1

    lexeme = text[start:i]

    if any(ch.isalpha() or ch == "_" for ch in lexeme):
        # Если есть буква, значит это не число и неправильный идентификатор
        return None, i, f"Ошибка: идентификатор не может начинаться с цифры: {lexeme}"

    if lexeme.count(".") > 1 or ".." in lexeme:
        return None, i, f"Ошибка: некорректно оформленное число: {lexeme}"

    if "." in lexeme:
        left, right = lexeme.split(".")

        if not left.isdigit() or not right.isdigit():
            return None, i, f"Ошибка: некорректно оформленная вещественная константа: {lexeme}"

        return Token("CONSTANT_REAL", lexeme), i, None

    return Token("CONSTANT_INT", lexeme), i, None

def lex_analyze(text):
    tokens = []
    errors = []
 
    i = 0
    sorted_operators = sorted(OPERATORS, key=len, reverse=True)
 
    while i < len(text):
        ch = text[i]
 
        if ch.isspace():
            i += 1
            continue
 
        if ch in ('"', "'"):
            lexeme, new_i, error = read_string(text, i)
 
            if error:
                errors.append(error)
            else:
                tokens.append(Token("CONSTANT_STRING", lexeme))
 
            i = new_i
            continue
 
        if is_identifier_start(ch):
            start = i
 
            while i < len(text) and is_identifier_char(text[i]):
                i += 1
 
            lexeme = text[start:i]
 
            if lexeme in KEYWORDS:
                tokens.append(Token("KEYWORD", lexeme))
            elif lexeme in BOOLEAN_CONSTANTS:
                tokens.append(Token("CONSTANT_BOOL", lexeme))
            else:
                tokens.append(Token("IDENTIFIER", lexeme))
 
            continue
 
        if ch.isdigit():
            token, new_i, error = read_number(text, i)
 
            if error:
                errors.append(error)
            else:
                tokens.append(token)
 
            i = new_i
            continue
 
        matched = False
 
        for op in sorted_operators:
            if text.startswith(op, i):
                tokens.append(Token("OPERATOR", op))
                i += len(op)
                matched = True
                break
 
        if matched:
            continue
 
        if ch in DELIMITERS:
            tokens.append(Token("DELIMITER", ch))
            i += 1
            continue
 
        errors.append(f"Ошибка: недопустимый символ: {ch}")
 
        i += 1
 
    return tokens, errors
 
def print_tokens(tokens):
    print("Лексема".ljust(25) + "| Тип")
    print("-" * 25 + "+" + "-" * 25)
 
    for token in tokens:
        print(token.lexeme.ljust(25) + "| " + token.token_type)
 
def print_token_sequence(tokens):
    sequence = [(token.token_type, token.lexeme) for token in tokens]
    print(sequence)
 
def main():
    input_file = "test.cpp"
    cleaned_file = "cleaned_test.cpp"
 
    try:
        code = read_file(input_file)
 
        if has_unclosed_comment(code):
            print("Ошибка: незакрытый многострочный комментарий.")
            return
 
        cleaned = preprocess(code)
        write_file(cleaned_file, cleaned)
 
        tokens, errors = lex_analyze(cleaned)
 
        print("Результат лексического анализа:")
        print_tokens(tokens)
        print()
 
        if errors:
            print("Обнаружены лексические ошибки:")
            for error in errors:
                print(error)
        else:
            print(f"Лексический анализ завершён успешно. Обнаружено {len(tokens)} токенов. Ошибок не найдено.")
 
    except FileNotFoundError:
        print(f"Ошибка: файл {input_file} не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()