class SemanticAnalyzer:
    def __init__(self):
        self.symbols = []
        self.functions = {}
        self.triads = []
        self.current_scope = ""
        self.current_return_type = ""
        self.functions["SetConsoleCP"] = {
            "return_type": "void",
            "params": ["int"]
        }
        self.functions["SetConsoleOutputCP"] = {
            "return_type": "void",
            "params": ["int"]
        }

    def error(self, error_type, message):
        print("Семантическая ошибка:", error_type)
        print("Пояснение:", message)
        raise SystemExit(1)

    def add_triad(self, operation, operand1="-", operand2="-"):
        self.triads.append((operation, operand1, operand2))
        return f"^{len(self.triads)}"

    def add_symbol(self, name, type_name, kind, initialized=False):
        for item in self.symbols:
            if item["name"] == name and item["scope"] == self.current_scope:
                self.error(
                    "повторное объявление",
                    f"Идентификатор '{name}' уже объявлен в области '{self.current_scope}'."
                )

        self.symbols.append({
            "name": name,
            "type": type_name,
            "scope": self.current_scope,
            "kind": kind,
            "declared": True,
            "initialized": initialized
        })

    def find_symbol(self, name):
        for item in reversed(self.symbols):
            if item["name"] == name and item["scope"] == self.current_scope:
                return item
        return None

    def require_symbol(self, name):
        symbol = self.find_symbol(name)
        if symbol is None:
            self.error(
                "использование необъявленной переменной",
                f"Переменная '{name}' используется, но не была объявлена."
            )
        return symbol

    def analyze(self, ast):
        self.collect_functions(ast)

        for node in ast.children:
            if node.name == "Function":
                self.analyze_function(node)

    def collect_functions(self, ast):
        for node in ast.children:
            if node.name != "Function":
                continue
            function_name = node.value
            return_type = node.children[0].value
            params = []

            for child in node.children:
                if child.name == "Parameters":
                    for param in child.children:
                        params.append(param.children[0].value)

            if function_name in self.functions:
                self.error(
                    "повторное объявление функции",
                    f"Функция '{function_name}' уже объявлена."
                )

            self.functions[function_name] = {
                "return_type": return_type,
                "params": params
            }

    

    def print_symbols(self):
        print("Таблица символов")
        print("Имя".ljust(12) + "| Тип".ljust(10) + "| Область".ljust(14) + "| Роль".ljust(12) + "| Объявлена | Инициализирована")
        print("-" * 82)

        for item in self.symbols:
            declared = "+" if item["declared"] else "-"
            initialized = "+" if item["initialized"] else "-"
            print(
                item["name"].ljust(12) + "| " +
                item["type"].ljust(8) + "| " +
                item["scope"].ljust(12) + "| " +
                item["kind"].ljust(10) + "| " +
                declared.center(9) + "| " +
                initialized.center(16)
            )

    def print_triads(self):
        print("Триады")
        for i, triad in enumerate(self.triads, start=1):
            operation, operand1, operand2 = triad
            print(f"{i}) {operation} ({operand1}, {operand2})")


def semantic_analyze(ast):
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    return analyzer


import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import AST as syntax

if hasattr(syntax, "ast"):
    ast = syntax.ast
else:
    with contextlib.redirect_stdout(io.StringIO()):
        import lexical_analyzer as lexer

    filename = "cleaned_test.cpp"
    content = lexer.read_source_file(filename)

    if content.strip() == "":
        print("Ошибка: входной файл пуст.")
        raise SystemExit(1)

    tokens = lexer.lexical_analyze(content)
    lexer.validate(tokens)
    ast = syntax.syntax_analyze(tokens)

analyzer = semantic_analyze(ast)

print("Результат семантического анализа")
print()
analyzer.print_symbols()
print()
print("Семантический анализ завершён успешно. Ошибок не найдено.")
print()
analyzer.print_triads()