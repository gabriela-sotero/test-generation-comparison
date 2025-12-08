"""
Testes para o módulo _compat

Este módulo testa as funções e constantes de compatibilidade entre Python 2 e 3,
incluindo constant_time_compare, text_type, e number_types.
"""
import sys
import pytest

from itsdangerous._compat import (
    PY2,
    text_type,
    number_types,
    constant_time_compare,
    _constant_time_compare,
)


class TestPY2Constant:
    """Testes para a constante PY2"""

    def test_py2_is_boolean(self):
        """
        Testa que PY2 é um booleano.

        Given: A constante PY2
        When: Verificamos o tipo
        Then: É um booleano
        """
        assert isinstance(PY2, bool)

    def test_py2_matches_version(self):
        """
        Testa que PY2 corresponde à versão atual.

        Given: A versão atual do Python
        When: Comparamos com PY2
        Then: PY2 é True apenas para Python 2
        """
        expected = sys.version_info[0] == 2
        assert PY2 == expected


class TestTextType:
    """Testes para text_type"""

    def test_text_type_is_str_on_py3(self):
        """
        Testa que text_type é str no Python 3.

        Given: Python 3
        When: Verificamos text_type
        Then: É str
        """
        if not PY2:
            assert text_type is str

    def test_text_type_works_with_unicode(self):
        """
        Testa que text_type funciona com unicode.

        Given: String unicode
        When: Criamos com text_type
        Then: Funciona corretamente
        """
        text = text_type("Hello, 世界")
        assert isinstance(text, text_type)

    def test_text_type_from_bytes(self):
        """
        Testa conversão de bytes para text_type.

        Given: Uma sequência de bytes
        When: Decodificamos para text_type
        Then: Obtemos texto
        """
        bytes_data = b"hello"
        text = text_type(bytes_data.decode("utf-8"))

        assert isinstance(text, text_type)
        assert text == "hello"


class TestNumberTypes:
    """Testes para number_types"""

    def test_number_types_is_tuple(self):
        """
        Testa que number_types é uma tupla.

        Given: A constante number_types
        When: Verificamos o tipo
        Then: É uma tupla de tipos
        """
        assert isinstance(number_types, tuple)
        assert len(number_types) > 0

    def test_int_is_number_type(self):
        """
        Testa que int é reconhecido como number type.

        Given: Um inteiro
        When: Verificamos com isinstance
        Then: É um number_type
        """
        num = 42
        assert isinstance(num, number_types)

    def test_float_is_number_type(self):
        """
        Testa que float é reconhecido como number type.

        Given: Um float
        When: Verificamos com isinstance
        Then: É um number_type
        """
        num = 3.14
        assert isinstance(num, number_types)

    def test_decimal_is_number_type(self):
        """
        Testa que Decimal é reconhecido como number type.

        Given: Um Decimal
        When: Verificamos com isinstance
        Then: É um number_type
        """
        from decimal import Decimal

        num = Decimal("10.5")
        assert isinstance(num, number_types)

    def test_string_is_not_number_type(self):
        """
        Testa que string não é number type.

        Given: Uma string
        When: Verificamos com isinstance
        Then: Não é um number_type
        """
        assert not isinstance("123", number_types)

    def test_complex_is_number_type(self):
        """
        Testa que complex é reconhecido como number type.

        Given: Um número complexo
        When: Verificamos com isinstance
        Then: É um number_type (numbers.Real não inclui complex, mas numbers.Complex sim)
        """
        num = complex(1, 2)
        # complex não é Real, então não deve ser number_type
        # number_types = (numbers.Real, decimal.Decimal)
        assert not isinstance(num, number_types)


class TestConstantTimeCompare:
    """Testes para constant_time_compare"""

    def test_equal_bytes_returns_true(self):
        """
        Testa comparação de bytes iguais.

        Given: Dois bytes iguais
        When: Chamamos constant_time_compare
        Then: Retorna True
        """
        val1 = b"hello"
        val2 = b"hello"

        assert constant_time_compare(val1, val2) is True

    def test_different_bytes_returns_false(self):
        """
        Testa comparação de bytes diferentes.

        Given: Dois bytes diferentes
        When: Chamamos constant_time_compare
        Then: Retorna False
        """
        val1 = b"hello"
        val2 = b"world"

        assert constant_time_compare(val1, val2) is False

    def test_different_length_returns_false(self):
        """
        Testa comparação de bytes com tamanhos diferentes.

        Given: Bytes de tamanhos diferentes
        When: Chamamos constant_time_compare
        Then: Retorna False
        """
        val1 = b"short"
        val2 = b"much longer string"

        assert constant_time_compare(val1, val2) is False

    def test_empty_bytes_equal(self):
        """
        Testa comparação de bytes vazios.

        Given: Dois bytes vazios
        When: Chamamos constant_time_compare
        Then: Retorna True
        """
        assert constant_time_compare(b"", b"") is True

    def test_one_byte_difference(self):
        """
        Testa que detecta diferença de um byte.

        Given: Strings quase iguais (1 byte diferente)
        When: Chamamos constant_time_compare
        Then: Retorna False
        """
        val1 = b"hello"
        val2 = b"hallo"

        assert constant_time_compare(val1, val2) is False

    def test_case_sensitive(self):
        """
        Testa que comparação é case-sensitive.

        Given: Mesma string com cases diferentes
        When: Chamamos constant_time_compare
        Then: Retorna False
        """
        val1 = b"Hello"
        val2 = b"hello"

        assert constant_time_compare(val1, val2) is False

    def test_with_null_bytes(self):
        """
        Testa comparação com bytes nulos.

        Given: Bytes contendo \x00
        When: Chamamos constant_time_compare
        Then: Compara corretamente
        """
        val1 = b"\x00\x01\x02"
        val2 = b"\x00\x01\x02"
        val3 = b"\x00\x01\x03"

        assert constant_time_compare(val1, val2) is True
        assert constant_time_compare(val1, val3) is False

    def test_long_strings(self):
        """
        Testa com strings longas.

        Given: Strings longas
        When: Chamamos constant_time_compare
        Then: Compara corretamente
        """
        val1 = b"a" * 1000
        val2 = b"a" * 1000
        val3 = b"a" * 999 + b"b"

        assert constant_time_compare(val1, val2) is True
        assert constant_time_compare(val1, val3) is False

    @pytest.mark.parametrize("val1,val2,expected", [
        (b"test", b"test", True),
        (b"test", b"Test", False),
        (b"abc", b"def", False),
        (b"", b"", True),
        (b"a", b"a", True),
        (b"a", b"b", False),
        (b"long string here", b"long string here", True),
        (b"long string here", b"long string there", False),
    ])
    def test_various_comparisons(self, val1, val2, expected):
        """
        Testa várias comparações com valores conhecidos.

        Given: Pares de valores e resultado esperado
        When: Chamamos constant_time_compare
        Then: Retorna o resultado esperado
        """
        result = constant_time_compare(val1, val2)
        assert result is expected


class TestInternalConstantTimeCompare:
    """Testa a implementação interna _constant_time_compare"""

    def test_implementation_exists(self):
        """
        Testa que a implementação interna existe.

        Given: O módulo _compat
        When: Verificamos _constant_time_compare
        Then: A função existe
        """
        assert callable(_constant_time_compare)

    def test_internal_equal_bytes(self):
        """
        Testa implementação interna com bytes iguais.

        Given: Bytes iguais
        When: Chamamos _constant_time_compare
        Then: Retorna True
        """
        result = _constant_time_compare(b"test", b"test")
        assert result is True

    def test_internal_different_bytes(self):
        """
        Testa implementação interna com bytes diferentes.

        Given: Bytes diferentes
        When: Chamamos _constant_time_compare
        Then: Retorna False
        """
        result = _constant_time_compare(b"test", b"best")
        assert result is False

    def test_internal_different_lengths(self):
        """
        Testa implementação interna com tamanhos diferentes.

        Given: Bytes de tamanhos diferentes
        When: Chamamos _constant_time_compare
        Then: Retorna False
        """
        result = _constant_time_compare(b"short", b"longer string")
        assert result is False

    def test_internal_vs_standard(self):
        """
        Testa que implementação interna dá mesmo resultado.

        Given: Vários pares de valores
        When: Comparamos ambas implementações
        Then: Resultados são idênticos
        """
        test_cases = [
            (b"same", b"same"),
            (b"diff", b"ferent"),
            (b"", b""),
            (b"a", b"b"),
        ]

        for val1, val2 in test_cases:
            internal_result = _constant_time_compare(val1, val2)
            standard_result = constant_time_compare(val1, val2)
            assert internal_result == standard_result


class TestCompatibilityIntegration:
    """Testes de integração das funcionalidades de compatibilidade"""

    def test_text_type_with_number_types(self):
        """
        Testa que text_type e number_types são compatíveis.

        Given: Um número e um texto
        When: Verificamos tipos
        Then: São distinguíveis corretamente
        """
        num = 42
        text = text_type("42")

        assert isinstance(num, number_types)
        assert not isinstance(text, number_types)
        assert isinstance(text, text_type)

    def test_constant_time_on_encoded_data(self):
        """
        Testa constant_time_compare em dados codificados.

        Given: Dados codificados em bytes
        When: Comparamos
        Then: Funciona corretamente
        """
        from itsdangerous.encoding import base64_encode

        data1 = base64_encode(b"secret")
        data2 = base64_encode(b"secret")
        data3 = base64_encode(b"public")

        assert constant_time_compare(data1, data2) is True
        assert constant_time_compare(data1, data3) is False

    def test_all_compat_features_importable(self):
        """
        Testa que todas as features de compatibilidade são importáveis.

        Given: O módulo _compat
        When: Importamos todas as features
        Then: Todas estão disponíveis
        """
        from itsdangerous import _compat

        assert hasattr(_compat, "PY2")
        assert hasattr(_compat, "text_type")
        assert hasattr(_compat, "number_types")
        assert hasattr(_compat, "constant_time_compare")
        assert hasattr(_compat, "_constant_time_compare")
