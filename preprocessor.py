import re

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def write_file(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def has_unclosed_comment(text):
    return text.count("/*") != text.count("*/")

def preprocess(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)

    lines = []
    for line in text.splitlines():
        line = re.sub(r"^[ \t]+|[ \t]+$", "", line)
        line = re.sub(r" {2,}", " ", line)
        if line:
            lines.append(line)

    return "\n".join(lines)

def main():

    input_file = "test.cpp"

    output_file = "cleaned_test.cpp"

 
    try:

        code = read_file(input_file)

 
        if has_unclosed_comment(code):

            print("Ошибка: незакрытый многострочный комментарий.")

            return

 
        cleaned = preprocess(code)

        write_file(output_file, cleaned)

 
        print("Файл обработан успешно.")

        print(f"Результат сохранён в {output_file}")

        print("Ошибок не выявлено.")

 
    except FileNotFoundError:

        print(f"Ошибка: файл {input_file} не найден.")

    except Exception as e:

        print(f"Ошибка: {e}")

 
if __name__ == "__main__":

    main()