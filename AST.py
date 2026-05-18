import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class SyntaxErrorException(Exception):
    pass
class ASTNode:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []

    def add(self, child):
        if child is not None:
            self.children.append(child)
        return child

    def title(self):
        return f"{self.name} {self.value}" if self.value is not None else self.name

    def to_tree(self, prefix="", is_last=True):
        lines = []
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + self.title())
        next_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            lines.extend(child.to_tree(next_prefix, i == len(self.children) - 1))
        return lines


def print_ast(root):
    print(root.title())
    for i, child in enumerate(root.children):
        for line in child.to_tree("", i == len(root.children) - 1):
            print(line)





def syntax_analyze(tokens):
    parser = Parser(tokens)
    ast = parser.parse_program()
    return ast


if __name__ == "__main__":
    try:
        # Используется лексический анализатор из файла lexical_analyzer.py.
        # Вывод лексера при импорте скрывается, чтобы в результате был только AST.
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            import lexical_analyzer as lexer

        filename = "cleaned_test.cpp"
        content = lexer.read_source_file(filename)
        if content.strip() == "":
            print("Ошибка: входной файл пуст.")
            raise SystemExit(1)

        tokens = lexer.lexical_analyze(content)
        lexer.validate(tokens)

        ast = syntax_analyze(tokens)
        print("Результат")
        print_ast(ast)
        print()
        print("Синтаксический анализ завершён успешно. Ошибок не найдено.")

    except SyntaxErrorException as err:
        print(err)
        raise SystemExit(1)
