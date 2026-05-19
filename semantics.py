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

    def analyze_function(self, node):
        self.current_scope = node.value
        self.current_return_type = node.children[0].value
 
        for child in node.children:
            if child.name == "Parameters":
                self.analyze_parameters(child)
 
        for child in node.children:
            if child.name == "Body":
                self.analyze_body(child)
 
    def analyze_parameters(self, node):
        for param in node.children:
            type_name = param.children[0].value
            name = param.children[1].value
            self.add_symbol(name, type_name, "parameter", True)
 
    def analyze_body(self, node):
        for child in node.children:
            self.analyze_statement(child)
 
    def analyze_statement(self, node):
        if node.name == "VarDecl":
            self.analyze_var_decl(node)
        elif node.name == "Assign":
            self.analyze_assign(node)
        elif node.name == "Input":
            self.analyze_input(node)
        elif node.name == "Output":
            self.analyze_output(node)
        elif node.name == "Return":
            self.analyze_return(node)
        elif node.name == "If":
            self.analyze_if(node)
        elif node.name == "While":
            self.analyze_while(node)
        elif node.name == "Switch":
            self.analyze_switch(node)
        elif node.name == "Call":
            self.analyze_call(node)
 
    def analyze_var_decl(self, node):
        type_name = node.children[0].value
 
        for item in node.children[1:]:
            var_name = item.value
            initialized = False
            init_place = None
            init_type = None
            if item.children:
                init_type, init_place = self.analyze_expression(item.children[0].children[0])
                initialized = True
                if init_type != type_name:
                    self.error(
                        "несоответствие типов",
                        f"Переменной '{var_name}' типа '{type_name}' нельзя присвоить значение типа '{init_type}'."
                    )
 
            self.add_symbol(var_name, type_name, "variable", initialized)
 
            if init_place is not None:
                self.add_triad("=", var_name, init_place)
 
    def analyze_assign(self, node):
        var_name = node.children[0].value
        symbol = self.require_symbol(var_name)
 
        right_type, right_place = self.analyze_expression(node.children[1])
 
        if symbol["type"] != right_type:
            self.error(
                "несоответствие типов",
                f"Переменной '{var_name}' типа '{symbol['type']}' нельзя присвоить значение типа '{right_type}'."
            )
 
        symbol["initialized"] = True
        self.add_triad("=", var_name, right_place)
 
    def analyze_input(self, node):
        for child in node.children:
            symbol = self.require_symbol(child.value)
            symbol["initialized"] = True
            self.add_triad("in", child.value, "-")
 
    def analyze_output(self, node):
        for child in node.children:
            expr_type, expr_place = self.analyze_expression(child)
            self.add_triad("out", expr_place, "-")
 
    def analyze_return(self, node):
        expr_type, expr_place = self.analyze_expression(node.children[0])
 
        if expr_type != self.current_return_type:
            self.error(
                "несоответствие типа return",
                f"Функция '{self.current_scope}' должна возвращать '{self.current_return_type}', но возвращает '{expr_type}'."
            )
 
        self.add_triad("return", expr_place, "-")
 
    def analyze_if(self, node):
        condition = node.children[0].children[0]
        cond_type, cond_place = self.analyze_expression(condition)
 
        if cond_type != "bool":
            self.error(
                "некорректный тип условия",
                "Условие оператора if должно иметь тип bool."
            )
 
        self.add_triad("if", cond_place, "-")
        self.analyze_body(node.children[1])
 
    def analyze_while(self, node):
        condition = node.children[0].children[0]
        cond_type, cond_place = self.analyze_expression(condition)
 
        if cond_type != "bool":
            self.error(
                "некорректный тип условия",
                "Условие цикла while должно иметь тип bool."
            )
 
        self.add_triad("while", cond_place, "-")
        self.analyze_body(node.children[1])
        self.add_triad("endwhile", "-", "-")
 
    def analyze_switch(self, node):
        switch_type, switch_place = self.analyze_expression(node.children[0])
 
        if switch_type != "int":
            self.error(
                "некорректный тип switch",
                "Выражение в switch должно иметь тип int."
            )
 
        self.add_triad("switch", switch_place, "-")
        used_cases = set()
        default_found = False
        for child in node.children[1:]:
            if child.name == "Case":
                case_type, case_place = self.analyze_expression(child.children[0])
 
                if case_type != "int":
                    self.error(
                        "некорректный тип case",
                        "Значение case должно иметь тип int."
                    )
 
                if case_place in used_cases:
                    self.error(
                        "повтор case",
                        f"Значение case '{case_place}' уже использовалось."
                    )
 
                used_cases.add(case_place)
                self.add_triad("case", switch_place, case_place)
                self.analyze_body(child.children[1])
 
            elif child.name == "Default":
                if default_found:
                    self.error(
                        "повтор default",
                        "В одном switch не может быть больше одной ветви default."
                    )
 
                default_found = True
                self.add_triad("default", "-", "-")
                self.analyze_body(child.children[0])
 
    def analyze_call(self, node):
        self.analyze_call_expr(node)
 
    def analyze_expression(self, node):
        if node.name == "ConstInt":
            return "int", node.value
 
        if node.name == "ConstFloat":
            return "float", node.value
 
        if node.name == "StringConst":
            return "string", node.value
 
        if node.name == "BoolConst":
            return "bool", node.value
 
        if node.name == "Identifier":
            if node.value == "endl":
                return "endl", "endl"
            symbol = self.require_symbol(node.value)
 
            if not symbol["initialized"]:
                self.error(
                    "использование неинициализированной переменной",
                    f"Переменная '{node.value}' используется до получения значения."
                )
 
            return symbol["type"], node.value
 
        if node.name == "Keyword" and node.value == "endl":
            return "endl", "endl"
        if node.name == "CallExpr" or node.name == "Call":
            return self.analyze_call_expr(node)
 
        if node.name == "BinaryExpr":
            left_type, left_place = self.analyze_expression(node.children[0])
            operator = node.children[1].value
            right_type, right_place = self.analyze_expression(node.children[2])
 
            if operator in {"+", "-", "*"}:
                if left_type != "int" or right_type != "int":
                    self.error(
                        "некорректные типы операндов",
                        f"Оператор '{operator}' можно применять только к int."
                    )
 
                result = self.add_triad(operator, left_place, right_place)
                return "int", result
 
            if operator == ">":
                if left_type != "int" or right_type != "int":
                    self.error(
                        "некорректные типы операндов",
                        "Оператор '>' можно применять только к int."
                    )
 
                result = self.add_triad(">", left_place, right_place)
                return "bool", result
 
            if operator in {"<", "<=", ">=", "==", "!="}:
                if left_type != "int" or right_type != "int":
                    self.error(
                        "некорректные типы операндов",
                        f"Оператор '{operator}' можно применять только к int."
                    )
 
                result = self.add_triad(operator, left_place, right_place)
                return "bool", result
 
            if operator == "**":
                if left_type != "int" or right_type != "int":
                    self.error(
                        "некорректные типы операндов",
                        "Оператор '**' можно применять только к int."
                    )
 
                result = self.add_triad("**", left_place, right_place)
                return "int", result
 
            if operator in {"&&", "||"}:
                if left_type != "bool" or right_type != "bool":
                    self.error(
                        "некорректные типы операндов",
                        f"Оператор '{operator}' можно применять только к bool."
                    )
 
                result = self.add_triad(operator, left_place, right_place)
                return "bool", result
 
        self.error(
            "неизвестное выражение",
            f"Не удалось определить тип узла '{node.name}'."
        )
 
    def analyze_call_expr(self, node):
        function_name = node.children[0].value
 
        if function_name not in self.functions:
            self.error(
                "вызов необъявленной функции",
                f"Функция '{function_name}' не была объявлена."
            )
 
        expected_params = self.functions[function_name]["params"]
        args_node = node.children[1]
        actual_args = []
 
        for arg in args_node.children:
            arg_type, arg_place = self.analyze_expression(arg)
            actual_args.append((arg_type, arg_place))
 
        if len(actual_args) != len(expected_params):
            self.error(
                "неверное количество аргументов",
                f"Функция '{function_name}' ожидает {len(expected_params)} аргумент(а), получено {len(actual_args)}."
            )
 
        for i in range(len(expected_params)):
            if actual_args[i][0] != expected_params[i]:
                self.error(
                    "несоответствие типов аргументов",
                    f"Аргумент {i + 1} функции '{function_name}' должен иметь тип '{expected_params[i]}', получен '{actual_args[i][0]}'."
                )
 
        if len(actual_args) == 0:
            result = self.add_triad("call " + function_name, "-", "-")
        elif len(actual_args) == 1:
            result = self.add_triad("call " + function_name, actual_args[0][1], "-")
        else:
            result = self.add_triad("call " + function_name, actual_args[0][1], actual_args[1][1])
 
        return self.functions[function_name]["return_type"], result

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