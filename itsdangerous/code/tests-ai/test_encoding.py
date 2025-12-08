"""
Testes para o módulo encoding

Este módulo testa as funções de codificação/decodificação base64 URL-safe,
conversão entre bytes e inteiros, e a função want_bytes.
"""
import pytest

from itsdangerous.encoding import (
    want_bytes,
    base64_encode,
    base64_decode,
    int_to_bytes,
    bytes_to_int,
    _base64_alphabet,
)
from itsdangerous.exc import BadData


class TestWantBytes:
    """Testes para a função want_bytes"""

    def test_bytes_input_returns_unchanged(self):
        """
        Testa que entrada bytes retorna sem modificação.

        Given: Uma string de bytes
        When: Chamamos want_bytes
        Then: Os bytes são retornados sem alteração
        """
        input_bytes = b"hello world"
        result = want_bytes(input_bytes)

        assert result == input_bytes
        assert isinstance(result, bytes)

    def test_string_input_converts_to_bytes(self):
        """
        Testa conversão de string para bytes.

        Given: Uma string de texto
        When: Chamamos want_bytes
        Then: É convertida para bytes UTF-8
        """
        input_str = "hello world"
        result = want_bytes(input_str)

        assert result == b"hello world"
        assert isinstance(result, bytes)

    def test_unicode_string_converts_correctly(self):
        """
        Testa conversão de string unicode.

        Given: Uma string com caracteres unicode
        When: Chamamos want_bytes
        Then: É codificada corretamente em UTF-8
        """
        input_str = "São Paulo, Brasil 🇧🇷"
        result = want_bytes(input_str)

        assert isinstance(result, bytes)
        # Pode ser decodificado de volta
        assert result.decode("utf-8") == input_str

    def test_custom_encoding(self):
        """
        Testa conversão com encoding customizado.

        Given: Uma string e um encoding específico
        When: Chamamos want_bytes com encoding
        Then: Usa o encoding especificado
        """
        input_str = "test"
        result = want_bytes(input_str, encoding="ascii")

        assert result == b"test"
        assert isinstance(result, bytes)

    def test_empty_string(self):
        """
        Testa conversão de string vazia.

        Given: Uma string vazia
        When: Chamamos want_bytes
        Then: Retorna bytes vazio
        """
        assert want_bytes("") == b""
        assert want_bytes(b"") == b""

    def test_encoding_errors_parameter(self):
        """
        Testa parâmetro de tratamento de erros.

        Given: String com caracteres inválidos para ASCII
        When: Chamamos want_bytes com errors='ignore'
        Then: Caracteres inválidos são ignorados
        """
        input_str = "São Paulo"
        result = want_bytes(input_str, encoding="ascii", errors="ignore")

        # Caracteres não-ASCII são ignorados
        assert result == b"So Paulo"


class TestBase64Encode:
    """Testes para a função base64_encode"""

    def test_encode_simple_bytes(self):
        """
        Testa codificação base64 de bytes simples.

        Given: Uma string de bytes
        When: Chamamos base64_encode
        Then: Retorna base64 URL-safe sem padding
        """
        result = base64_encode(b"hello")

        assert isinstance(result, bytes)
        # Base64 URL-safe não tem padding '='
        assert b"=" not in result

    def test_encode_string_input(self):
        """
        Testa codificação com string como entrada.

        Given: Uma string de texto
        When: Chamamos base64_encode
        Then: É convertida para bytes e codificada
        """
        result = base64_encode("hello")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_encode_empty_bytes(self):
        """
        Testa codificação de bytes vazio.

        Given: Bytes vazio
        When: Chamamos base64_encode
        Then: Retorna bytes vazio
        """
        result = base64_encode(b"")

        assert result == b""

    def test_encode_removes_padding(self):
        """
        Testa que padding '=' é removido.

        Given: Dados que gerariam padding
        When: Chamamos base64_encode
        Then: O padding é removido
        """
        # Diferentes tamanhos para testar remoção de padding
        test_cases = [b"a", b"ab", b"abc", b"abcd"]

        for data in test_cases:
            result = base64_encode(data)
            assert b"=" not in result

    def test_encode_binary_data(self):
        """
        Testa codificação de dados binários.

        Given: Dados binários (bytes não-ASCII)
        When: Chamamos base64_encode
        Then: São codificados corretamente
        """
        binary_data = b"\x00\x01\x02\xff\xfe"
        result = base64_encode(binary_data)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_encode_uses_urlsafe_alphabet(self):
        """
        Testa que usa alfabeto URL-safe.

        Given: Dados que gerariam '+' ou '/' no base64 padrão
        When: Chamamos base64_encode
        Then: Usa '-' e '_' ao invés de '+' e '/'
        """
        # Este dado específico geraria + ou / em base64 padrão
        data = b"\xfb\xff"
        result = base64_encode(data)

        # Base64 URL-safe usa - e _ ao invés de + e /
        assert b"+" not in result
        assert b"/" not in result


class TestBase64Decode:
    """Testes para a função base64_decode"""

    def test_decode_simple_base64(self):
        """
        Testa decodificação de base64 simples.

        Given: String base64 válida
        When: Chamamos base64_decode
        Then: Retorna os bytes originais
        """
        encoded = base64_encode(b"hello")
        decoded = base64_decode(encoded)

        assert decoded == b"hello"

    def test_decode_without_padding(self):
        """
        Testa decodificação sem padding.

        Given: Base64 sem padding '='
        When: Chamamos base64_decode
        Then: Adiciona padding automaticamente e decodifica
        """
        # Codifica e remove padding manualmente para testar
        encoded = base64_encode(b"test")
        # Já não tem padding, mas vamos garantir
        encoded = encoded.rstrip(b"=")

        decoded = base64_decode(encoded)
        assert decoded == b"test"

    def test_decode_adds_correct_padding(self):
        """
        Testa que padding correto é adicionado.

        Given: Base64 com diferentes tamanhos
        When: Chamamos base64_decode
        Then: Padding correto é adicionado
        """
        test_cases = [b"a", b"ab", b"abc", b"abcd", b"abcde"]

        for original in test_cases:
            encoded = base64_encode(original)
            decoded = base64_decode(encoded)
            assert decoded == original

    def test_decode_string_input(self):
        """
        Testa decodificação com string como entrada.

        Given: String base64
        When: Chamamos base64_decode
        Then: É convertida para bytes e decodificada
        """
        encoded = base64_encode(b"test")
        decoded = base64_decode(encoded.decode("ascii"))

        assert decoded == b"test"

    def test_decode_empty_string(self):
        """
        Testa decodificação de string vazia.

        Given: String vazia
        When: Chamamos base64_decode
        Then: Retorna bytes vazio
        """
        result = base64_decode(b"")

        assert result == b""

    def test_decode_invalid_base64_raises_error(self):
        """
        Testa que base64 inválido lança BadData.

        Given: String não-base64
        When: Chamamos base64_decode
        Then: Lança exceção BadData
        """
        with pytest.raises(BadData) as exc_info:
            base64_decode(b"!!!invalid!!!")

        assert "Invalid base64-encoded data" in str(exc_info.value)

    def test_decode_with_invalid_characters(self):
        """
        Testa decodificação com caracteres inválidos.

        Given: String com caracteres não-base64
        When: Chamamos base64_decode
        Then: Lança BadData
        """
        with pytest.raises(BadData):
            base64_decode(b"invalid@#$%characters")

    def test_decode_urlsafe_characters(self):
        """
        Testa decodificação de caracteres URL-safe.

        Given: Base64 URL-safe com - e _
        When: Chamamos base64_decode
        Then: Decodifica corretamente
        """
        # Cria dados que usarão - e _ quando codificados
        original = b"\xfb\xff"
        encoded = base64_encode(original)
        decoded = base64_decode(encoded)

        assert decoded == original

    def test_roundtrip_encoding(self):
        """
        Testa que encode -> decode retorna original.

        Given: Vários dados diferentes
        When: Codificamos e decodificamos
        Then: Obtemos os dados originais
        """
        test_data = [
            b"simple",
            b"with spaces",
            b"\x00\x01\x02",
            b"unicode: \xc3\xa9",
            b"a" * 100,  # Dados longos
        ]

        for data in test_data:
            encoded = base64_encode(data)
            decoded = base64_decode(encoded)
            assert decoded == data


class TestIntToBytes:
    """Testes para a função int_to_bytes"""

    def test_convert_small_integer(self):
        """
        Testa conversão de inteiro pequeno.

        Given: Um inteiro pequeno
        When: Chamamos int_to_bytes
        Then: Retorna representação em bytes
        """
        result = int_to_bytes(1)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_convert_zero(self):
        """
        Testa conversão de zero.

        Given: O número 0
        When: Chamamos int_to_bytes
        Then: Retorna representação válida
        """
        result = int_to_bytes(0)

        assert isinstance(result, bytes)

    def test_convert_large_integer(self):
        """
        Testa conversão de inteiro grande.

        Given: Um inteiro grande (mas < 2^64)
        When: Chamamos int_to_bytes
        Then: Retorna representação em bytes
        """
        large_num = 2**32
        result = int_to_bytes(large_num)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_removes_leading_null_bytes(self):
        """
        Testa que remove zeros à esquerda.

        Given: Um inteiro que geraria zeros à esquerda
        When: Chamamos int_to_bytes
        Then: Zeros à esquerda são removidos
        """
        result = int_to_bytes(255)  # 0x000000FF em 64 bits

        # Não deve ter zeros desnecessários no início
        assert result[0:1] != b"\x00"

    def test_maximum_64bit_value(self):
        """
        Testa conversão do valor máximo de 64 bits.

        Given: 2^64 - 1
        When: Chamamos int_to_bytes
        Then: Converte sem erros
        """
        max_val = 2**64 - 1
        result = int_to_bytes(max_val)

        assert isinstance(result, bytes)
        assert len(result) == 8  # 64 bits = 8 bytes

    @pytest.mark.parametrize("num", [
        1,
        255,
        256,
        65535,
        65536,
        2**32,
        2**63,
    ])
    def test_various_integers(self, num):
        """
        Testa conversão de vários inteiros diferentes.

        Given: Diferentes valores inteiros
        When: Chamamos int_to_bytes
        Then: Todos são convertidos corretamente
        """
        result = int_to_bytes(num)

        assert isinstance(result, bytes)
        assert len(result) > 0


class TestBytesToInt:
    """Testes para a função bytes_to_int"""

    def test_convert_simple_bytes(self):
        """
        Testa conversão de bytes simples.

        Given: Uma sequência de bytes
        When: Chamamos bytes_to_int
        Then: Retorna o inteiro correspondente
        """
        result = bytes_to_int(b"\x01")

        assert isinstance(result, int)
        assert result > 0

    def test_convert_empty_bytes(self):
        """
        Testa conversão de bytes vazio.

        Given: Bytes vazio
        When: Chamamos bytes_to_int
        Then: Retorna 0
        """
        result = bytes_to_int(b"")

        assert result == 0

    def test_convert_multi_byte(self):
        """
        Testa conversão de múltiplos bytes.

        Given: Sequência de vários bytes
        When: Chamamos bytes_to_int
        Then: Retorna inteiro correto
        """
        # 4 bytes
        result = bytes_to_int(b"\x00\x00\x01\x00")

        assert isinstance(result, int)
        assert result == 256

    def test_handles_short_input(self):
        """
        Testa que aceita entrada menor que 8 bytes.

        Given: Menos de 8 bytes
        When: Chamamos bytes_to_int
        Then: Adiciona padding e converte
        """
        # Apenas 1 byte, função deve adicionar padding
        result = bytes_to_int(b"\xff")

        assert isinstance(result, int)
        assert result == 255

    def test_handles_8_byte_input(self):
        """
        Testa entrada de exatamente 8 bytes.

        Given: Exatamente 8 bytes
        When: Chamamos bytes_to_int
        Then: Converte diretamente
        """
        eight_bytes = b"\x00\x00\x00\x00\x00\x00\x01\x00"
        result = bytes_to_int(eight_bytes)

        assert isinstance(result, int)
        assert result == 256

    @pytest.mark.parametrize("data,expected", [
        (b"\x00", 0),
        (b"\x01", 1),
        (b"\xff", 255),
        (b"\x01\x00", 256),
    ])
    def test_known_conversions(self, data, expected):
        """
        Testa conversões com valores conhecidos.

        Given: Bytes com valores conhecidos
        When: Chamamos bytes_to_int
        Then: Retorna o inteiro esperado
        """
        result = bytes_to_int(data)

        assert result == expected


class TestRoundtripIntBytes:
    """Testa conversão bidirecional entre int e bytes"""

    def test_roundtrip_small_numbers(self):
        """
        Testa roundtrip com números pequenos.

        Given: Números pequenos
        When: Convertemos para bytes e de volta
        Then: Obtemos o número original
        """
        numbers = [0, 1, 10, 100, 255, 256, 1000]

        for num in numbers:
            bytes_form = int_to_bytes(num)
            back_to_int = bytes_to_int(bytes_form)
            assert back_to_int == num

    def test_roundtrip_large_numbers(self):
        """
        Testa roundtrip com números grandes.

        Given: Números grandes (< 2^64)
        When: Convertemos para bytes e de volta
        Then: Obtemos o número original
        """
        numbers = [
            2**16,
            2**32,
            2**48,
            2**63,
            2**64 - 1,
        ]

        for num in numbers:
            bytes_form = int_to_bytes(num)
            back_to_int = bytes_to_int(bytes_form)
            assert back_to_int == num

    def test_roundtrip_preserves_value(self):
        """
        Testa que valores são preservados no roundtrip.

        Given: Um timestamp típico
        When: Convertemos ida e volta
        Then: O valor é preservado exatamente
        """
        timestamp = 1234567890  # Timestamp comum

        bytes_form = int_to_bytes(timestamp)
        recovered = bytes_to_int(bytes_form)

        assert recovered == timestamp


class TestBase64Alphabet:
    """Testa a constante _base64_alphabet"""

    def test_alphabet_is_bytes(self):
        """
        Testa que _base64_alphabet é bytes.

        Given: A constante _base64_alphabet
        When: Verificamos o tipo
        Then: É do tipo bytes
        """
        assert isinstance(_base64_alphabet, bytes)

    def test_alphabet_contains_expected_characters(self):
        """
        Testa que contém os caracteres esperados.

        Given: A constante _base64_alphabet
        When: Verificamos o conteúdo
        Then: Contém caracteres base64 URL-safe
        """
        # Deve conter letras, dígitos e caracteres URL-safe
        assert b"A" in _base64_alphabet
        assert b"Z" in _base64_alphabet
        assert b"a" in _base64_alphabet
        assert b"z" in _base64_alphabet
        assert b"0" in _base64_alphabet
        assert b"9" in _base64_alphabet
        assert b"-" in _base64_alphabet
        assert b"_" in _base64_alphabet
        assert b"=" in _base64_alphabet

    def test_alphabet_does_not_contain_urlsafe_forbidden(self):
        """
        Testa que não contém caracteres proibidos em URLs.

        Given: A constante _base64_alphabet
        When: Verificamos caracteres problemáticos
        Then: Não contém + ou /
        """
        # Base64 URL-safe não usa + e /
        assert b"+" not in _base64_alphabet
        assert b"/" not in _base64_alphabet
