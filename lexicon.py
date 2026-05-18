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



if __name__ == "__main__":
    main()