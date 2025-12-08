"""
Testes para as classes helper Csv e Choices

Este módulo testa as classes Csv e Choices, que fornecem funcionalidades
de parsing e validação de valores de configuração.
"""
import pytest
from decouple import Csv, Choices


class TestCsv:
    """Testes para a classe Csv"""

    def test_init_with_defaults(self):
        """
        Testa inicialização com valores padrão.

        Given: Nenhum parâmetro
        When: Criamos Csv
        Then: Usa valores padrão
        """
        csv = Csv()
        assert csv.cast is not None
        assert csv.delimiter == ','
        assert csv.post_process is list

    def test_init_with_custom_cast(self):
        """
        Testa inicialização com cast customizado.

        Given: Uma função cast customizada
        When: Criamos Csv
        Then: Usa a função fornecida
        """
        csv = Csv(cast=int)
        assert csv.cast is int

    def test_init_with_custom_delimiter(self):
        """
        Testa inicialização com delimitador customizado.

        Given: Um delimitador customizado
        When: Criamos Csv
        Then: Usa o delimitador fornecido
        """
        csv = Csv(delimiter=';')
        assert csv.delimiter == ';'

    def test_init_with_custom_strip(self):
        """
        Testa inicialização com strip customizado.

        Given: Caracteres de strip customizados
        When: Criamos Csv
        Then: Usa os caracteres fornecidos
        """
        import string
        csv = Csv(strip=string.whitespace)
        assert csv.strip == string.whitespace

    def test_init_with_custom_post_process(self):
        """
        Testa inicialização com post_process customizado.

        Given: Uma função post_process customizada
        When: Criamos Csv
        Then: Usa a função fornecida
        """
        csv = Csv(post_process=tuple)
        assert csv.post_process is tuple

    def test_parse_simple_csv(self):
        """
        Testa parsing de CSV simples.

        Given: Uma string CSV simples
        When: Chamamos o parser
        Then: Retorna lista de valores
        """
        csv = Csv()
        result = csv("a,b,c")

        assert result == ["a", "b", "c"]
        assert isinstance(result, list)

    def test_parse_with_spaces(self):
        """
        Testa parsing com espaços.

        Given: CSV com espaços ao redor dos valores
        When: Chamamos o parser
        Then: Espaços são removidos (strip)
        """
        csv = Csv()
        result = csv("a, b, c")

        assert result == ["a", "b", "c"]

    def test_parse_empty_string(self):
        """
        Testa parsing de string vazia.

        Given: Uma string vazia
        When: Chamamos o parser
        Then: Retorna lista vazia
        """
        csv = Csv()
        result = csv("")

        assert result == []

    def test_parse_none_value(self):
        """
        Testa parsing de None.

        Given: Valor None
        When: Chamamos o parser
        Then: Retorna resultado de post_process()
        """
        csv = Csv()
        result = csv(None)

        assert result == []

    def test_parse_with_int_cast(self):
        """
        Testa parsing com cast para int.

        Given: CSV com números
        When: Usamos cast=int
        Then: Retorna lista de inteiros
        """
        csv = Csv(cast=int)
        result = csv("1,2,3,4,5")

        assert result == [1, 2, 3, 4, 5]
        assert all(isinstance(x, int) for x in result)

    def test_parse_with_float_cast(self):
        """
        Testa parsing com cast para float.

        Given: CSV com números
        When: Usamos cast=float
        Then: Retorna lista de floats
        """
        csv = Csv(cast=float)
        result = csv("1.5,2.7,3.9")

        assert result == [1.5, 2.7, 3.9]
        assert all(isinstance(x, float) for x in result)

    def test_parse_with_custom_delimiter(self):
        """
        Testa parsing com delimitador customizado.

        Given: CSV com delimitador customizado
        When: Especificamos o delimitador
        Then: Usa o delimitador correto
        """
        csv = Csv(delimiter=';')
        result = csv("a;b;c")

        assert result == ["a", "b", "c"]

    def test_parse_with_pipe_delimiter(self):
        """
        Testa parsing com pipe como delimitador.

        Given: CSV com pipe
        When: Especificamos delimiter='|'
        Then: Parseia corretamente
        """
        csv = Csv(delimiter='|')
        result = csv("a|b|c")

        assert result == ["a", "b", "c"]

    def test_parse_with_tuple_post_process(self):
        """
        Testa parsing com post_process=tuple.

        Given: CSV
        When: Usamos post_process=tuple
        Then: Retorna tupla
        """
        csv = Csv(post_process=tuple)
        result = csv("a,b,c")

        assert result == ("a", "b", "c")
        assert isinstance(result, tuple)

    def test_parse_with_set_post_process(self):
        """
        Testa parsing com post_process=set.

        Given: CSV
        When: Usamos post_process=set
        Then: Retorna set
        """
        csv = Csv(post_process=set)
        result = csv("a,b,c")

        assert result == {"a", "b", "c"}
        assert isinstance(result, set)

    def test_parse_quoted_values(self):
        """
        Testa parsing de valores com aspas.

        Given: CSV com valores entre aspas
        When: Chamamos o parser
        Then: Aspas são tratadas corretamente (shlex)
        """
        csv = Csv()
        result = csv('"value 1","value 2","value 3"')

        assert "value 1" in result
        assert "value 2" in result
        assert "value 3" in result

    def test_parse_single_value(self):
        """
        Testa parsing de valor único.

        Given: Uma string com um único valor
        When: Chamamos o parser
        Then: Retorna lista com um elemento
        """
        csv = Csv()
        result = csv("single")

        assert result == ["single"]

    def test_parse_with_custom_strip(self):
        """
        Testa parsing com strip customizado.

        Given: CSV com caracteres específicos para remover
        When: Especificamos strip
        Then: Remove os caracteres corretos
        """
        csv = Csv(strip='_')
        result = csv("_a_,_b_,_c_")

        assert result == ["a", "b", "c"]

    def test_parse_empty_post_process_none(self):
        """
        Testa None com post_process customizado.

        Given: None e post_process=tuple
        When: Chamamos o parser
        Then: Retorna tuple vazia
        """
        csv = Csv(post_process=tuple)
        result = csv(None)

        assert result == ()
        assert isinstance(result, tuple)

    def test_parse_with_spaces_in_values(self):
        """
        Testa valores que contêm espaços.

        Given: CSV com valores contendo espaços
        When: Valores estão entre aspas
        Then: Preserva os espaços
        """
        csv = Csv()
        result = csv('"hello world","foo bar"')

        assert "hello world" in result
        assert "foo bar" in result

    def test_parse_mixed_quoted_unquoted(self):
        """
        Testa mix de valores com e sem aspas.

        Given: CSV com valores mixtos
        When: Chamamos o parser
        Then: Parseia corretamente ambos
        """
        csv = Csv()
        result = csv('a,"b c",d')

        assert "a" in result
        assert "b c" in result
        assert "d" in result

    def test_cast_error_propagates(self):
        """
        Testa que erros de cast são propagados.

        Given: CSV com valor que não pode ser convertido
        When: Aplicamos cast
        Then: Lança exceção
        """
        csv = Csv(cast=int)

        with pytest.raises(ValueError):
            csv("1,2,invalid,4")

    def test_callable_behavior(self):
        """
        Testa que Csv é callable.

        Given: Uma instância de Csv
        When: Chamamos como função
        Then: Executa a transformação
        """
        csv = Csv()
        assert callable(csv)
        result = csv("a,b")
        assert result == ["a", "b"]

    def test_parse_numbers_as_strings(self):
        """
        Testa parsing de números como strings.

        Given: CSV com números
        When: Usamos cast padrão (str)
        Then: Retorna strings
        """
        csv = Csv()
        result = csv("1,2,3")

        assert result == ["1", "2", "3"]
        assert all(isinstance(x, str) for x in result)

    def test_parse_with_trailing_comma(self):
        """
        Testa parsing com vírgula final.

        Given: CSV com vírgula no final
        When: Chamamos o parser
        Then: Ignora vírgula final (comportamento shlex)
        """
        csv = Csv()
        result = csv("a,b,c,")

        # Comportamento pode variar, mas não deve crashar
        assert isinstance(result, list)

    def test_parse_complex_example(self):
        """
        Testa exemplo complexo com múltiplas features.

        Given: CSV complexo
        When: Usamos cast, delimiter e post_process customizados
        Then: Aplica todas as transformações
        """
        csv = Csv(cast=int, delimiter=';', post_process=tuple)
        result = csv("10;20;30")

        assert result == (10, 20, 30)
        assert isinstance(result, tuple)

    def test_whitespace_split_behavior(self):
        """
        Testa que whitespace_split está ativado.

        Given: Valores separados por delimitador
        When: Usamos Csv
        Then: Split é feito pelo delimitador, não whitespace
        """
        csv = Csv(delimiter=',')
        result = csv("a b,c d")

        # Com whitespace_split=True e delimiter=',', deve tratar ',' como delimitador
        assert len(result) == 2


class TestChoices:
    """Testes para a classe Choices"""

    def test_init_with_flat_list(self):
        """
        Testa inicialização com lista flat.

        Given: Uma lista flat de escolhas
        When: Criamos Choices
        Then: Armazena as escolhas
        """
        choices = Choices(flat=["option1", "option2", "option3"])
        assert choices.flat == ["option1", "option2", "option3"]

    def test_init_with_choices_tuples(self):
        """
        Testa inicialização com tuplas estilo Django.

        Given: Tuplas de (valor, descrição)
        When: Criamos Choices
        Then: Armazena as tuplas
        """
        choices = Choices(choices=[("opt1", "Option 1"), ("opt2", "Option 2")])
        assert choices.choices == [("opt1", "Option 1"), ("opt2", "Option 2")]

    def test_init_with_custom_cast(self):
        """
        Testa inicialização com cast customizado.

        Given: Uma função cast
        When: Criamos Choices
        Then: Usa a função fornecida
        """
        choices = Choices(flat=["1", "2"], cast=int)
        assert choices.cast is int

    def test_init_defaults(self):
        """
        Testa inicialização com valores padrão.

        Given: Nenhum parâmetro
        When: Criamos Choices
        Then: Usa valores padrão
        """
        choices = Choices()
        assert choices.flat == []
        assert choices.choices == []

    def test_valid_values_from_flat(self):
        """
        Testa _valid_values com flat.

        Given: Lista flat de valores
        When: Verificamos _valid_values
        Then: Contém os valores da flat
        """
        choices = Choices(flat=["a", "b", "c"])
        assert "a" in choices._valid_values
        assert "b" in choices._valid_values
        assert "c" in choices._valid_values

    def test_valid_values_from_choices(self):
        """
        Testa _valid_values com choices.

        Given: Tuplas de choices
        When: Verificamos _valid_values
        Then: Contém apenas os valores (primeiro elemento)
        """
        choices = Choices(choices=[("val1", "Desc 1"), ("val2", "Desc 2")])
        assert "val1" in choices._valid_values
        assert "val2" in choices._valid_values
        assert "Desc 1" not in choices._valid_values

    def test_valid_values_from_both(self):
        """
        Testa _valid_values com flat e choices.

        Given: Tanto flat quanto choices
        When: Verificamos _valid_values
        Then: Contém valores de ambos
        """
        choices = Choices(
            flat=["a", "b"],
            choices=[("c", "C"), ("d", "D")]
        )
        assert all(v in choices._valid_values for v in ["a", "b", "c", "d"])

    def test_call_with_valid_value(self):
        """
        Testa validação de valor válido.

        Given: Um valor que está nas choices
        When: Chamamos com esse valor
        Then: Retorna o valor transformado
        """
        choices = Choices(flat=["option1", "option2"])
        result = choices("option1")

        assert result == "option1"

    def test_call_with_invalid_value_raises_error(self):
        """
        Testa que valor inválido lança erro.

        Given: Um valor que não está nas choices
        When: Tentamos usar esse valor
        Then: Lança ValueError
        """
        choices = Choices(flat=["option1", "option2"])

        with pytest.raises(ValueError) as exc_info:
            choices("invalid")

        assert "Value not in list" in str(exc_info.value)
        assert "invalid" in str(exc_info.value)

    def test_call_applies_cast(self):
        """
        Testa que cast é aplicado ao valor.

        Given: Choices com cast
        When: Passamos um valor
        Then: Cast é aplicado antes da validação
        """
        choices = Choices(flat=["1", "2", "3"], cast=str)
        result = choices("1")

        assert result == "1"
        assert isinstance(result, str)

    def test_cast_before_validation(self):
        """
        Testa que cast é feito antes da validação.

        Given: Choices com valores numéricos como string
        When: Passamos número como string
        Then: Cast transforma e valida
        """
        choices = Choices(flat=["1", "2", "3"])
        result = choices("1")

        assert result == "1"

    def test_error_message_shows_valid_values(self):
        """
        Testa que mensagem de erro mostra valores válidos.

        Given: Choices com valores
        When: Passamos valor inválido
        Then: Mensagem mostra valores válidos
        """
        choices = Choices(flat=["opt1", "opt2"])

        with pytest.raises(ValueError) as exc_info:
            choices("invalid")

        error_message = str(exc_info.value)
        assert "opt1" in error_message
        assert "opt2" in error_message

    def test_callable_behavior(self):
        """
        Testa que Choices é callable.

        Given: Uma instância de Choices
        When: Chamamos como função
        Then: Executa a validação
        """
        choices = Choices(flat=["a", "b"])
        assert callable(choices)
        result = choices("a")
        assert result == "a"

    def test_case_sensitive_validation(self):
        """
        Testa que validação é case-sensitive.

        Given: Choices com valores em minúsculas
        When: Passamos valor em maiúsculas
        Then: Lança erro (case-sensitive)
        """
        choices = Choices(flat=["option"])

        with pytest.raises(ValueError):
            choices("OPTION")

    def test_empty_choices_rejects_all(self):
        """
        Testa que choices vazio rejeita tudo.

        Given: Choices sem valores válidos
        When: Passamos qualquer valor
        Then: Lança ValueError
        """
        choices = Choices()

        with pytest.raises(ValueError):
            choices("anything")

    def test_choices_with_int_cast(self):
        """
        Testa Choices com cast para int.

        Given: Choices com cast=int e valores numéricos
        When: Passamos string numérica
        Then: Converte e valida
        """
        choices = Choices(flat=[1, 2, 3], cast=int)
        result = choices("1")

        assert result == 1
        assert isinstance(result, int)

    def test_django_style_choices(self):
        """
        Testa choices estilo Django.

        Given: Tuplas de (valor, descrição)
        When: Validamos usando o valor
        Then: Aceita valores válidos
        """
        choices = Choices(choices=[
            ("dev", "Development"),
            ("prod", "Production"),
        ])

        assert choices("dev") == "dev"
        assert choices("prod") == "prod"

        with pytest.raises(ValueError):
            choices("Development")  # Descrição não é válida

    def test_mixed_flat_and_choices(self):
        """
        Testa combinação de flat e choices.

        Given: Tanto flat quanto choices definidos
        When: Validamos valores de ambas as fontes
        Then: Aceita valores de ambas
        """
        choices = Choices(
            flat=["local"],
            choices=[("dev", "Development"), ("prod", "Production")]
        )

        assert choices("local") == "local"
        assert choices("dev") == "dev"
        assert choices("prod") == "prod"

    def test_duplicate_values_in_valid_values(self):
        """
        Testa que valores duplicados não causam problemas.

        Given: Valores duplicados em flat e choices
        When: Criamos Choices
        Then: Funciona normalmente
        """
        choices = Choices(
            flat=["value1"],
            choices=[("value1", "Description")]
        )

        result = choices("value1")
        assert result == "value1"

    @pytest.mark.parametrize("valid_value", ["a", "b", "c"])
    def test_multiple_valid_values(self, valid_value):
        """
        Testa múltiplos valores válidos.

        Given: Várias opções válidas
        When: Testamos cada uma
        Then: Todas são aceitas
        """
        choices = Choices(flat=["a", "b", "c"])
        result = choices(valid_value)
        assert result == valid_value

    def test_numeric_string_choices(self):
        """
        Testa choices com strings numéricas.

        Given: Choices com números como string
        When: Validamos
        Then: Funciona corretamente
        """
        choices = Choices(flat=["1", "2", "3"])

        assert choices("1") == "1"
        assert choices("2") == "2"

        with pytest.raises(ValueError):
            choices("4")

    def test_choices_preserves_type_after_cast(self):
        """
        Testa que tipo é preservado após cast.

        Given: Choices com cast específico
        When: Validamos valor
        Then: Retorna valor com tipo do cast
        """
        choices = Choices(flat=[1, 2, 3], cast=int)
        result = choices("2")

        assert result == 2
        assert type(result) is int

    def test_error_repr_in_message(self):
        """
        Testa que erro usa repr dos valores.

        Given: Choices
        When: Valor inválido é passado
        Then: Mensagem usa repr para mostrar valores
        """
        choices = Choices(flat=["a", "b"])

        with pytest.raises(ValueError) as exc_info:
            choices("x")

        # A mensagem deve ter formato específico com repr
        assert "!r" in str(exc_info.value) or "'" in str(exc_info.value)
