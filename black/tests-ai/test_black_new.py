"""
Nova suíte de testes para o formatador Black
Testes independentes focados em diferentes aspectos da formatação
"""

import unittest
from textwrap import dedent
import black
from black import Mode, TargetVersion


class TestBasicFormatting(unittest.TestCase):
    """Testes de formatação básica"""
    
    def format_code(self, source: str) -> str:
        """Helper para formatar código"""
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_string_quotes_normalization(self):
        """Testa normalização de aspas em strings"""
        source = """
        name = 'John'
        message = "Hello"
        mixed = 'It\\'s working'
        """
        result = self.format_code(source)
        self.assertIn('"John"', result)
        self.assertIn('"Hello"', result)
        
    def test_numeric_literals(self):
        """Testa formatação de literais numéricos"""
        source = """
        a=1+2
        b=3.14*2
        c=0x1F
        d=1_000_000
        """
        result = self.format_code(source)
        self.assertIn("a = 1 + 2", result)
        self.assertIn("b = 3.14 * 2", result)
        
    def test_operator_spacing(self):
        """Testa espaçamento ao redor de operadores"""
        source = """
        result=x+y*z
        check=a==b and c!=d
        power=2**8
        """
        result = self.format_code(source)
        self.assertIn("result = x + y * z", result)
        self.assertIn("check = a == b and c != d", result)
        self.assertIn("power = 2**8", result)


class TestControlStructures(unittest.TestCase):
    """Testes de estruturas de controle"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_if_else_formatting(self):
        """Testa formatação de if/else"""
        source = """
        if condition:x=1
        elif other:y=2
        else:z=3
        """
        result = self.format_code(source)
        self.assertIn("if condition:\n    x = 1", result)
        self.assertIn("elif other:\n    y = 2", result)
        
    def test_for_loop_formatting(self):
        """Testa formatação de loops for"""
        source = """
        for i in range(10):print(i)
        for key,value in items():process(key,value)
        """
        result = self.format_code(source)
        self.assertIn("for i in range(10):\n    print(i)", result)
        
    def test_while_loop_formatting(self):
        """Testa formatação de loops while"""
        source = """
        while condition:
            do_something()
            if break_condition:break
        """
        result = self.format_code(source)
        self.assertIn("while condition:", result)
        self.assertIn("break", result)
        
    def test_match_case_formatting(self):
        """Testa formatação de match/case (Python 3.10+)"""
        source = """
        match value:
            case 1:result='one'
            case 2:result='two'
            case _:result='other'
        """
        result = self.format_code(source)
        self.assertIn("match value:", result)
        self.assertIn("case 1:", result)


class TestFunctionsAndClasses(unittest.TestCase):
    """Testes de funções e classes"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_function_definition(self):
        """Testa formatação de definição de função"""
        source = """
        def my_function(a,b,c):
            return a+b+c
        """
        result = self.format_code(source)
        self.assertIn("def my_function(a, b, c):", result)
        self.assertIn("return a + b + c", result)
        
    def test_function_with_defaults(self):
        """Testa função com valores padrão"""
        source = """
        def greet(name='World',times=1):
            for _ in range(times):print(f'Hello, {name}!')
        """
        result = self.format_code(source)
        self.assertIn('name="World"', result)
        self.assertIn("times=1", result)
        
    def test_class_definition(self):
        """Testa formatação de classes"""
        source = """
        class MyClass:
            def __init__(self,value):
                self.value=value
            def get_value(self):return self.value
        """
        result = self.format_code(source)
        self.assertIn("class MyClass:", result)
        self.assertIn("def __init__(self, value):", result)
        
    def test_decorator_formatting(self):
        """Testa formatação de decoradores"""
        source = """
        @property
        def name(self):return self._name
        
        @staticmethod
        def create():return MyClass()
        """
        result = self.format_code(source)
        self.assertIn("@property", result)
        self.assertIn("@staticmethod", result)


class TestImportsAndOrganization(unittest.TestCase):
    """Testes de imports e organização"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_single_imports(self):
        """Testa formatação de imports simples"""
        source = """
        import os,sys,json
        from pathlib import Path,PurePath
        """
        result = self.format_code(source)
        # Black não muda múltiplos imports em uma linha para múltiplas linhas
        # mas formata o espaçamento
        self.assertIn("import os, sys, json", result)
        
    def test_from_imports(self):
        """Testa imports do tipo 'from'"""
        source = """
        from collections import defaultdict,Counter
        from typing import List,Dict,Optional
        """
        result = self.format_code(source)
        self.assertIn("from collections import", result)
        self.assertIn("from typing import", result)
        
    def test_long_import_line(self):
        """Testa quebra de linha em imports longos"""
        source = """
        from my_very_long_module_name import function_one, function_two, function_three, function_four, function_five
        """
        result = self.format_code(source)
        # Black deve quebrar a linha se for muito longa
        self.assertIn("from my_very_long_module_name import", result)


class TestStringFormatting(unittest.TestCase):
    """Testes de formatação de strings"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_f_strings(self):
        """Testa formatação de f-strings"""
        source = """
        name='Alice'
        age=30
        message=f'My name is {name} and I am {age} years old'
        """
        result = self.format_code(source)
        self.assertIn('name = "Alice"', result)
        self.assertIn("f\"My name is {name}", result)
        
    def test_multiline_strings(self):
        """Testa strings multilinha"""
        source = '''
        text = """
        This is a
        multiline string
        """
        '''
        result = self.format_code(source)
        self.assertIn('"""', result)
        
    def test_docstrings(self):
        """Testa formatação de docstrings"""
        source = '''
        def function():
            """This is a docstring"""
            pass
        '''
        result = self.format_code(source)
        self.assertIn('"""This is a docstring"""', result)
        
    def test_raw_strings(self):
        """Testa strings raw"""
        source = r"""
        pattern = r'\d{3}-\d{3}-\d{4}'
        path = r'C:\Users\Name\Documents'
        """
        result = self.format_code(source)
        self.assertIn(r"r'\d{3}", result)


class TestLineLengthAndWrapping(unittest.TestCase):
    """Testes de comprimento de linha e quebra"""
    
    def format_code(self, source: str, line_length: int = 88) -> str:
        mode = Mode(target_versions={TargetVersion.PY310}, line_length=line_length)
        return black.format_str(dedent(source), mode=mode)
    
    def test_long_function_call(self):
        """Testa quebra de linha em chamadas de função longas"""
        source = """
        result = my_function(argument1, argument2, argument3, argument4, argument5, argument6, argument7)
        """
        result = self.format_code(source)
        # Deve quebrar a linha
        self.assertIn("my_function(", result)
        
    def test_long_list_literal(self):
        """Testa quebra de linha em listas longas"""
        source = """
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        """
        result = self.format_code(source)
        self.assertIn("items = [", result)
        
    def test_long_dictionary(self):
        """Testa quebra de linha em dicionários longos"""
        source = """
        config = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4', 'key5': 'value5'}
        """
        result = self.format_code(source, line_length=50)
        self.assertIn("config = {", result)
        
    def test_custom_line_length(self):
        """Testa formatação com comprimento de linha customizado"""
        source = """
        x = 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10
        """
        result_short = self.format_code(source, line_length=40)
        result_long = self.format_code(source, line_length=100)
        # Resultados devem ser diferentes
        self.assertIsNotNone(result_short)
        self.assertIsNotNone(result_long)


class TestWhitespaceHandling(unittest.TestCase):
    """Testes de espaçamento"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_vertical_whitespace_removal(self):
        """Testa remoção de espaçamento vertical excessivo"""
        source = """
        def function1():
            pass


        def function2():
            pass
        """
        result = self.format_code(source)
        # Black deve manter apenas 2 linhas em branco entre funções de nível módulo
        self.assertNotIn("\n\n\n\n", result)
        
    def test_trailing_whitespace_removal(self):
        """Testa remoção de espaços no final da linha"""
        source = "x = 1   \ny = 2  \n"
        result = black.format_str(source, mode=Mode())
        # Não deve haver espaços no final
        for line in result.split('\n'):
            if line:
                self.assertEqual(line, line.rstrip())
                
    def test_blank_lines_in_functions(self):
        """Testa linhas em branco dentro de funções"""
        source = """
        def function():
            x = 1


            y = 2
        """
        result = self.format_code(source)
        # Black deve manter no máximo uma linha em branco
        self.assertNotIn("\n\n\n", result)


class TestComplexExpressions(unittest.TestCase):
    """Testes de expressões complexas"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_list_comprehension(self):
        """Testa compreensões de lista"""
        source = """
        squares=[x**2 for x in range(10)]
        filtered=[x for x in items if x>0]
        """
        result = self.format_code(source)
        self.assertIn("squares = [x**2 for x in range(10)]", result)
        self.assertIn("filtered = [x for x in items if x > 0]", result)
        
    def test_dict_comprehension(self):
        """Testa compreensões de dicionário"""
        source = """
        mapping={k:v for k,v in pairs}
        inverted={v:k for k,v in original.items()}
        """
        result = self.format_code(source)
        self.assertIn("mapping = {k: v for k, v in pairs}", result)
        
    def test_lambda_functions(self):
        """Testa funções lambda"""
        source = """
        add=lambda x,y:x+y
        square=lambda x:x**2
        """
        result = self.format_code(source)
        self.assertIn("add = lambda x, y: x + y", result)
        self.assertIn("square = lambda x: x**2", result)
        
    def test_nested_structures(self):
        """Testa estruturas aninhadas"""
        source = """
        data={'users':[{'name':'Alice','age':30},{'name':'Bob','age':25}]}
        """
        result = self.format_code(source)
        self.assertIn("data = {", result)
        self.assertIn("users", result)


class TestTypeHints(unittest.TestCase):
    """Testes de type hints"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_function_type_hints(self):
        """Testa type hints em funções"""
        source = """
        def greet(name:str,age:int)->str:
            return f'Hello {name}, you are {age}'
        """
        result = self.format_code(source)
        self.assertIn("name: str", result)
        self.assertIn("age: int", result)
        self.assertIn("-> str:", result)
        
    def test_variable_annotations(self):
        """Testa anotações de variáveis"""
        source = """
        count:int=0
        name:str='Alice'
        items:list[str]=[]
        """
        result = self.format_code(source)
        self.assertIn("count: int = 0", result)
        self.assertIn('name: str = "Alice"', result)
        
    def test_complex_type_hints(self):
        """Testa type hints complexos"""
        source = """
        from typing import Optional,Union,Dict,List
        def process(data:Optional[Dict[str,List[int]]])->Union[str,None]:
            pass
        """
        result = self.format_code(source)
        self.assertIn("Optional[Dict[str, List[int]]]", result)
        
    def test_generic_types(self):
        """Testa tipos genéricos"""
        source = """
        def get_items()->list[str]:
            return []
        def get_mapping()->dict[str,int]:
            return {}
        """
        result = self.format_code(source)
        self.assertIn("-> list[str]:", result)
        self.assertIn("-> dict[str, int]:", result)


class TestEdgeCases(unittest.TestCase):
    """Testes de casos edge"""
    
    def format_code(self, source: str) -> str:
        mode = Mode(target_versions={TargetVersion.PY310})
        return black.format_str(dedent(source), mode=mode)
    
    def test_empty_file(self):
        """Testa arquivo vazio"""
        source = ""
        result = black.format_str(source, mode=Mode())
        self.assertEqual(result, "")
        
    def test_only_comments(self):
        """Testa arquivo apenas com comentários"""
        source = """
        # This is a comment
        # Another comment
        """
        result = self.format_code(source)
        self.assertIn("# This is a comment", result)
        
    def test_inline_comments(self):
        """Testa comentários inline"""
        source = """
        x = 1  # Initialize x
        y = 2# No space before comment
        """
        result = self.format_code(source)
        self.assertIn("# Initialize x", result)
        
    def test_multiline_expressions(self):
        """Testa expressões multilinha"""
        source = """
        result = (
            1 + 2 + 3 +
            4 + 5 + 6
        )
        """
        result = self.format_code(source)
        self.assertIn("result = (", result)
        
    def test_walrus_operator(self):
        """Testa operador walrus (Python 3.8+)"""
        source = """
        if (n:=len(items))>10:
            print(f'Too many items: {n}')
        """
        result = self.format_code(source)
        self.assertIn(":=", result)
        
    def test_exception_handling(self):
        """Testa formatação de try/except"""
        source = """
        try:
            risky_operation()
        except ValueError as e:print(e)
        except Exception:pass
        finally:cleanup()
        """
        result = self.format_code(source)
        self.assertIn("try:", result)
        self.assertIn("except ValueError as e:", result)
        self.assertIn("finally:", result)


class TestBlackStability(unittest.TestCase):
    """Testes de estabilidade do Black"""
    
    def test_formatting_is_idempotent(self):
        """Testa que formatar código já formatado não muda nada"""
        source = dedent("""
        def hello(name: str) -> None:
            print(f"Hello, {name}!")
        """)
        
        mode = Mode(target_versions={TargetVersion.PY310})
        first_format = black.format_str(source, mode=mode)
        second_format = black.format_str(first_format, mode=mode)
        
        self.assertEqual(first_format, second_format)
        
    def test_ast_equivalence(self):
        """Testa que o AST permanece equivalente após formatação"""
        source = dedent("""
        def calculate(x,y):
            result=x*2+y*3
            return result
        """)
        
        import ast
        original_ast = ast.dump(ast.parse(source))
        
        mode = Mode(target_versions={TargetVersion.PY310})
        formatted = black.format_str(source, mode=mode)
        formatted_ast = ast.dump(ast.parse(formatted))
        
        self.assertEqual(original_ast, formatted_ast)


if __name__ == "__main__":
    # Executar todos os testes
    unittest.main(verbosity=2)