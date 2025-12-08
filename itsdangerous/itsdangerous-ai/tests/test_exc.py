"""
Testes para o módulo exc

Este módulo testa todas as classes de exceção personalizadas do itsdangerous,
incluindo BadData, BadSignature, BadTimeSignature, SignatureExpired, BadHeader,
e BadPayload.
"""
import pytest
from datetime import datetime

from itsdangerous.exc import (
    BadData,
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    BadHeader,
    BadPayload,
)


class TestBadData:
    """Testes para a classe base BadData"""

    def test_create_with_message(self):
        """
        Testa que BadData pode ser criado com uma mensagem.

        Given: Uma mensagem de erro
        When: Criamos uma exceção BadData
        Then: A mensagem é armazenada corretamente
        """
        message = "Something went wrong"
        exc = BadData(message)

        assert exc.message == message
        assert str(exc) == message

    def test_create_with_unicode_message(self):
        """
        Testa que BadData aceita mensagens unicode.

        Given: Uma mensagem com caracteres unicode
        When: Criamos uma exceção BadData
        Then: A mensagem unicode é preservada
        """
        message = "Erro com acentuação: São Paulo"
        exc = BadData(message)

        assert exc.message == message
        assert str(exc) == message

    def test_create_with_empty_message(self):
        """
        Testa que BadData pode ser criado com mensagem vazia.

        Given: Uma string vazia
        When: Criamos uma exceção BadData
        Then: A exceção é criada sem erros
        """
        exc = BadData("")

        assert exc.message == ""
        assert str(exc) == ""

    def test_is_exception(self):
        """
        Testa que BadData é uma Exception válida.

        Given: Uma instância de BadData
        When: Verificamos sua herança
        Then: É uma subclasse de Exception
        """
        exc = BadData("test")

        assert isinstance(exc, Exception)

    def test_can_be_raised_and_caught(self):
        """
        Testa que BadData pode ser lançado e capturado.

        Given: Uma função que lança BadData
        When: Capturamos a exceção
        Then: Podemos acessar a mensagem
        """
        with pytest.raises(BadData) as exc_info:
            raise BadData("test error")

        assert exc_info.value.message == "test error"


class TestBadSignature:
    """Testes para a classe BadSignature"""

    def test_create_with_message_only(self):
        """
        Testa criação de BadSignature apenas com mensagem.

        Given: Apenas uma mensagem de erro
        When: Criamos BadSignature
        Then: payload deve ser None
        """
        exc = BadSignature("Invalid signature")

        assert exc.message == "Invalid signature"
        assert exc.payload is None

    def test_create_with_payload(self):
        """
        Testa criação de BadSignature com payload.

        Given: Uma mensagem e um payload
        When: Criamos BadSignature
        Then: Ambos são armazenados corretamente
        """
        payload = b"tampered data"
        exc = BadSignature("Invalid signature", payload=payload)

        assert exc.message == "Invalid signature"
        assert exc.payload == payload

    def test_payload_can_be_any_type(self):
        """
        Testa que payload pode ser de qualquer tipo.

        Given: Diferentes tipos de payload
        When: Criamos BadSignature
        Then: O payload é preservado
        """
        payloads = [
            b"bytes",
            "string",
            {"dict": "value"},
            ["list"],
            None,
        ]

        for payload in payloads:
            exc = BadSignature("error", payload=payload)
            assert exc.payload == payload

    def test_inherits_from_bad_data(self):
        """
        Testa que BadSignature herda de BadData.

        Given: Uma instância de BadSignature
        When: Verificamos herança
        Then: É uma subclasse de BadData
        """
        exc = BadSignature("test")

        assert isinstance(exc, BadData)
        assert isinstance(exc, Exception)


class TestBadTimeSignature:
    """Testes para a classe BadTimeSignature"""

    def test_create_with_message_only(self):
        """
        Testa criação com apenas mensagem.

        Given: Apenas mensagem
        When: Criamos BadTimeSignature
        Then: payload e date_signed são None
        """
        exc = BadTimeSignature("Time error")

        assert exc.message == "Time error"
        assert exc.payload is None
        assert exc.date_signed is None

    def test_create_with_payload_and_date(self):
        """
        Testa criação com payload e data de assinatura.

        Given: Mensagem, payload e data
        When: Criamos BadTimeSignature
        Then: Todos os campos são preservados
        """
        payload = b"data"
        date = datetime(2024, 1, 1, 12, 0, 0)
        exc = BadTimeSignature("Time error", payload=payload, date_signed=date)

        assert exc.message == "Time error"
        assert exc.payload == payload
        assert exc.date_signed == date

    def test_date_signed_can_be_timestamp(self):
        """
        Testa que date_signed pode ser um timestamp.

        Given: Um timestamp inteiro
        When: Criamos BadTimeSignature
        Then: O timestamp é preservado
        """
        timestamp = 1234567890
        exc = BadTimeSignature("error", date_signed=timestamp)

        assert exc.date_signed == timestamp

    def test_inherits_from_bad_signature(self):
        """
        Testa que BadTimeSignature herda de BadSignature.

        Given: Uma instância de BadTimeSignature
        When: Verificamos herança
        Then: É subclasse de BadSignature e BadData
        """
        exc = BadTimeSignature("test")

        assert isinstance(exc, BadSignature)
        assert isinstance(exc, BadData)
        assert isinstance(exc, Exception)


class TestSignatureExpired:
    """Testes para a classe SignatureExpired"""

    def test_create_signature_expired(self):
        """
        Testa criação de SignatureExpired.

        Given: Mensagem indicando expiração
        When: Criamos SignatureExpired
        Then: A exceção é criada corretamente
        """
        exc = SignatureExpired("Signature expired")

        assert exc.message == "Signature expired"
        assert exc.payload is None
        assert exc.date_signed is None

    def test_with_age_information(self):
        """
        Testa com informações de idade da assinatura.

        Given: Mensagem com detalhes de idade
        When: Criamos SignatureExpired
        Then: A mensagem contém as informações
        """
        message = "Signature age 7200 > 3600 seconds"
        exc = SignatureExpired(message)

        assert message in str(exc)

    def test_with_date_signed(self):
        """
        Testa com data de assinatura.

        Given: Data quando foi assinado
        When: Criamos SignatureExpired
        Then: A data é preservada
        """
        date = datetime(2024, 1, 1)
        exc = SignatureExpired("Expired", date_signed=date)

        assert exc.date_signed == date

    def test_inherits_from_bad_time_signature(self):
        """
        Testa que SignatureExpired herda de BadTimeSignature.

        Given: Uma instância de SignatureExpired
        When: Verificamos herança
        Then: É subclasse de toda a hierarquia
        """
        exc = SignatureExpired("test")

        assert isinstance(exc, BadTimeSignature)
        assert isinstance(exc, BadSignature)
        assert isinstance(exc, BadData)
        assert isinstance(exc, Exception)


class TestBadHeader:
    """Testes para a classe BadHeader"""

    def test_create_with_message_only(self):
        """
        Testa criação com apenas mensagem.

        Given: Apenas mensagem
        When: Criamos BadHeader
        Then: Campos opcionais são None
        """
        exc = BadHeader("Invalid header")

        assert exc.message == "Invalid header"
        assert exc.payload is None
        assert exc.header is None
        assert exc.original_error is None

    def test_create_with_all_fields(self):
        """
        Testa criação com todos os campos.

        Given: Mensagem, payload, header e erro original
        When: Criamos BadHeader
        Then: Todos os campos são preservados
        """
        payload = b"data"
        header = {"alg": "HS256"}
        original_error = ValueError("bad value")

        exc = BadHeader(
            "Header error",
            payload=payload,
            header=header,
            original_error=original_error,
        )

        assert exc.message == "Header error"
        assert exc.payload == payload
        assert exc.header == header
        assert exc.original_error == original_error

    def test_header_can_be_dict(self):
        """
        Testa que header pode ser um dicionário.

        Given: Um dicionário como header
        When: Criamos BadHeader
        Then: O dicionário é preservado
        """
        header = {"alg": "HS512", "typ": "JWT"}
        exc = BadHeader("error", header=header)

        assert exc.header == header
        assert exc.header["alg"] == "HS512"

    def test_original_error_preserves_exception(self):
        """
        Testa que original_error preserva a exceção original.

        Given: Uma exceção original
        When: Criamos BadHeader com ela
        Then: Podemos acessar a exceção
        """
        original = ValueError("original error")
        exc = BadHeader("Header problem", original_error=original)

        assert exc.original_error is original
        assert str(exc.original_error) == "original error"

    def test_inherits_from_bad_signature(self):
        """
        Testa que BadHeader herda de BadSignature.

        Given: Uma instância de BadHeader
        When: Verificamos herança
        Then: É subclasse de BadSignature e BadData
        """
        exc = BadHeader("test")

        assert isinstance(exc, BadSignature)
        assert isinstance(exc, BadData)
        assert isinstance(exc, Exception)


class TestBadPayload:
    """Testes para a classe BadPayload"""

    def test_create_with_message_only(self):
        """
        Testa criação com apenas mensagem.

        Given: Apenas mensagem
        When: Criamos BadPayload
        Then: original_error é None
        """
        exc = BadPayload("Invalid payload")

        assert exc.message == "Invalid payload"
        assert exc.original_error is None

    def test_create_with_original_error(self):
        """
        Testa criação com erro original.

        Given: Mensagem e erro original
        When: Criamos BadPayload
        Then: Ambos são preservados
        """
        original = ValueError("json decode error")
        exc = BadPayload("Could not decode", original_error=original)

        assert exc.message == "Could not decode"
        assert exc.original_error is original

    def test_original_error_can_be_any_exception(self):
        """
        Testa que original_error aceita qualquer exceção.

        Given: Diferentes tipos de exceção
        When: Criamos BadPayload
        Then: A exceção é preservada
        """
        exceptions = [
            ValueError("value error"),
            TypeError("type error"),
            KeyError("key error"),
            Exception("generic"),
        ]

        for original in exceptions:
            exc = BadPayload("error", original_error=original)
            assert exc.original_error is original

    def test_inherits_from_bad_data(self):
        """
        Testa que BadPayload herda de BadData.

        Given: Uma instância de BadPayload
        When: Verificamos herança
        Then: É subclasse de BadData
        """
        exc = BadPayload("test")

        assert isinstance(exc, BadData)
        assert isinstance(exc, Exception)

    def test_not_inherits_from_bad_signature(self):
        """
        Testa que BadPayload NÃO herda de BadSignature.

        Given: Uma instância de BadPayload
        When: Verificamos herança
        Then: Não é subclasse de BadSignature
        """
        exc = BadPayload("test")

        assert not isinstance(exc, BadSignature)


class TestExceptionHierarchy:
    """Testa a hierarquia completa de exceções"""

    def test_all_exceptions_inherit_from_bad_data(self):
        """
        Testa que todas as exceções herdam de BadData.

        Given: Todas as classes de exceção
        When: Verificamos herança
        Then: Todas herdam de BadData
        """
        exceptions = [
            BadData("test"),
            BadSignature("test"),
            BadTimeSignature("test"),
            SignatureExpired("test"),
            BadHeader("test"),
            BadPayload("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, BadData)
            assert isinstance(exc, Exception)

    def test_can_catch_all_with_bad_data(self):
        """
        Testa que podemos capturar todas com BadData.

        Given: Diferentes exceções sendo lançadas
        When: Capturamos com BadData
        Then: Todas são capturadas
        """
        exceptions_to_raise = [
            BadSignature("sig"),
            BadPayload("payload"),
            SignatureExpired("expired"),
        ]

        for exc_to_raise in exceptions_to_raise:
            with pytest.raises(BadData):
                raise exc_to_raise

    def test_exception_hierarchy_specificity(self):
        """
        Testa que podemos capturar especificamente cada tipo.

        Given: Exceções específicas
        When: Capturamos com seu tipo específico
        Then: A captura funciona corretamente
        """
        with pytest.raises(SignatureExpired):
            raise SignatureExpired("expired")

        with pytest.raises(BadTimeSignature):
            raise SignatureExpired("expired")

        with pytest.raises(BadSignature):
            raise SignatureExpired("expired")
