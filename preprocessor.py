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