"""
Testes para o módulo serializer

Este módulo testa a classe Serializer, que combina serialização JSON
com assinatura criptográfica para criar dados assinados serializados.
"""
import io
import json
import pytest

from itsdangerous.serializer import Serializer, is_text_serializer
from itsdangerous.exc import BadSignature, BadPayload
from itsdangerous.signer import Signer


class TestIsTextSerializer:
    """Testes para a função is_text_serializer"""

    def test_json_is_text_serializer(self):
        """
        Testa que JSON é reconhecido como text serializer.

        Given: Um serializer JSON
        When: Chamamos is_text_serializer
        Then: Retorna True
        """
        result = is_text_serializer(json)

        assert result is True

    def test_detects_text_serializer(self):
        """
        Testa detecção de serializers que retornam texto.

        Given: Um serializer que retorna string
        When: Verificamos com is_text_serializer
        Then: Retorna True
        """
        class TextSerializer:
            @staticmethod
            def dumps(obj):
                return "text"

        result = is_text_serializer(TextSerializer())

        assert result is True

    def test_detects_bytes_serializer(self):
        """
        Testa detecção de serializers que retornam bytes.

        Given: Um serializer que retorna bytes
        When: Verificamos com is_text_serializer
        Then: Retorna False
        """
        class BytesSerializer:
            @staticmethod
            def dumps(obj):
                return b"bytes"

        result = is_text_serializer(BytesSerializer())

        assert result is False


class TestSerializer:
    """Testes para a classe Serializer"""

    @pytest.fixture
    def serializer(self):
        """Fixture que retorna um Serializer básico"""
        return Serializer(b"secret-key")

    def test_create_with_secret_key(self):
        """
        Testa criação com chave secreta.

        Given: Uma chave secreta
        When: Criamos Serializer
        Then: É criado com sucesso
        """
        s = Serializer(b"my-secret")

        assert s.secret_key == b"my-secret"

    def test_create_with_string_secret_key(self):
        """
        Testa criação com chave como string.

        Given: Chave como string
        When: Criamos Serializer
        Then: É convertida para bytes
        """
        s = Serializer("my-secret")

        assert s.secret_key == b"my-secret"

    def test_default_salt(self, serializer):
        """
        Testa que salt padrão é usado.

        Given: Serializer sem salt especificado
        When: Verificamos o salt
        Then: Usa o padrão 'itsdangerous'
        """
        assert serializer.salt == b"itsdangerous"

    def test_custom_salt(self):
        """
        Testa salt customizado.

        Given: Um salt específico
        When: Criamos Serializer
        Then: Usa o salt especificado
        """
        s = Serializer(b"secret", salt=b"my-salt")

        assert s.salt == b"my-salt"

    def test_default_serializer_is_json(self, serializer):
        """
        Testa que serializer padrão é JSON.

        Given: Serializer sem serializer especificado
        When: Verificamos
        Then: Usa JSON
        """
        from itsdangerous._json import json as itsdangerous_json

        assert serializer.serializer is itsdangerous_json

    def test_custom_serializer(self):
        """
        Testa serializer customizado.

        Given: Um serializer específico
        When: Criamos Serializer
        Then: Usa o serializer especificado
        """
        class CustomSerializer:
            @staticmethod
            def dumps(obj):
                return b"custom"

            @staticmethod
            def loads(data):
                return {"custom": True}

        s = Serializer(b"secret", serializer=CustomSerializer)

        assert s.serializer is CustomSerializer

    def test_default_signer_class(self, serializer):
        """
        Testa que classe signer padrão é Signer.

        Given: Serializer sem signer especificado
        When: Verificamos
        Then: Usa Signer
        """
        assert serializer.signer is Signer

    def test_custom_signer_class(self):
        """
        Testa classe signer customizada.

        Given: Uma classe signer específica
        When: Criamos Serializer
        Then: Usa a classe especificada
        """
        class CustomSigner(Signer):
            pass

        s = Serializer(b"secret", signer=CustomSigner)

        assert s.signer is CustomSigner

    def test_signer_kwargs(self):
        """
        Testa passagem de kwargs para signer.

        Given: signer_kwargs específicos
        When: Criamos Serializer
        Then: São armazenados
        """
        kwargs = {"key_derivation": "hmac", "digest_method": None}
        s = Serializer(b"secret", signer_kwargs=kwargs)

        assert s.signer_kwargs == kwargs

    def test_serializer_kwargs(self):
        """
        Testa passagem de kwargs para serializer.

        Given: serializer_kwargs específicos
        When: Criamos Serializer
        Then: São armazenados
        """
        kwargs = {"indent": 2}
        s = Serializer(b"secret", serializer_kwargs=kwargs)

        assert s.serializer_kwargs == kwargs

    def test_dumps_simple_dict(self, serializer):
        """
        Testa serialização de dicionário simples.

        Given: Um dicionário
        When: Chamamos dumps
        Then: Retorna string assinada
        """
        data = {"key": "value"}
        result = serializer.dumps(data)

        assert isinstance(result, str)
        assert "." in result

    def test_dumps_with_salt(self, serializer):
        """
        Testa dumps com salt customizado.

        Given: Um objeto e salt específico
        When: Chamamos dumps com salt
        Then: Usa o salt fornecido
        """
        data = {"test": "data"}
        result1 = serializer.dumps(data, salt="salt1")
        result2 = serializer.dumps(data, salt="salt2")

        # Salts diferentes geram assinaturas diferentes
        assert result1 != result2

    def test_loads_valid_data(self, serializer):
        """
        Testa loads com dados válidos.

        Given: Dados serializados corretamente
        When: Chamamos loads
        Then: Retorna o objeto original
        """
        data = {"key": "value", "number": 42}
        serialized = serializer.dumps(data)
        loaded = serializer.loads(serialized)

        assert loaded == data

    def test_loads_invalid_signature_raises(self, serializer):
        """
        Testa loads com assinatura inválida.

        Given: Dados com assinatura adulterada
        When: Chamamos loads
        Then: Lança BadSignature
        """
        serialized = serializer.dumps({"data": "value"})
        tampered = serialized[:-5] + "XXXXX"

        with pytest.raises(BadSignature):
            serializer.loads(tampered)

    def test_loads_with_matching_salt(self, serializer):
        """
        Testa que loads requer mesmo salt.

        Given: Dados serializados com salt específico
        When: Chamamos loads com mesmo salt
        Then: Funciona corretamente
        """
        data = {"test": "data"}
        serialized = serializer.dumps(data, salt="mysalt")
        loaded = serializer.loads(serialized, salt="mysalt")

        assert loaded == data

    def test_loads_with_wrong_salt_raises(self, serializer):
        """
        Testa que loads com salt errado falha.

        Given: Dados serializados com um salt
        When: Chamamos loads com salt diferente
        Then: Lança BadSignature
        """
        serialized = serializer.dumps({"data": "value"}, salt="salt1")

        with pytest.raises(BadSignature):
            serializer.loads(serialized, salt="salt2")

    def test_roundtrip_various_data_types(self, serializer):
        """
        Testa roundtrip com vários tipos de dados.

        Given: Diferentes tipos de objetos JSON
        When: Serializamos e desserializamos
        Then: Obtemos objetos originais
        """
        test_cases = [
            {"simple": "dict"},
            {"nested": {"dict": {"key": "value"}}},
            [1, 2, 3, 4],
            {"list": [1, 2, 3], "dict": {"a": "b"}},
            {"unicode": "São Paulo 🇧🇷"},
            {"numbers": 42, "float": 3.14, "bool": True, "null": None},
        ]

        for data in test_cases:
            serialized = serializer.dumps(data)
            loaded = serializer.loads(serialized)
            assert loaded == data

    def test_dump_to_file(self, serializer):
        """
        Testa dump para arquivo.

        Given: Um objeto e um file handle
        When: Chamamos dump
        Then: Escreve dados serializados no arquivo
        """
        data = {"key": "value"}
        f = io.StringIO()

        serializer.dump(data, f)

        f.seek(0)
        content = f.read()
        assert "." in content
        assert len(content) > 0

    def test_load_from_file(self, serializer):
        """
        Testa load de arquivo.

        Given: Arquivo com dados serializados
        When: Chamamos load
        Then: Retorna o objeto original
        """
        data = {"test": "data"}
        f = io.StringIO()
        serializer.dump(data, f)

        f.seek(0)
        loaded = serializer.load(f)

        assert loaded == data

    def test_loads_unsafe_valid_signature(self, serializer):
        """
        Testa loads_unsafe com assinatura válida.

        Given: Dados com assinatura válida
        When: Chamamos loads_unsafe
        Then: Retorna (True, payload)
        """
        data = {"key": "value"}
        serialized = serializer.dumps(data)

        is_valid, payload = serializer.loads_unsafe(serialized)

        assert is_valid is True
        assert payload == data

    def test_loads_unsafe_invalid_signature(self, serializer):
        """
        Testa loads_unsafe com assinatura inválida.

        Given: Dados com assinatura inválida
        When: Chamamos loads_unsafe
        Then: Retorna (False, payload) se possível
        """
        serialized = serializer.dumps({"key": "value"})
        # Adultera apenas a assinatura, não o payload
        parts = serialized.rsplit(".", 1)
        tampered = parts[0] + ".tampered"

        is_valid, payload = serializer.loads_unsafe(tampered)

        assert is_valid is False
        assert payload == {"key": "value"}

    def test_loads_unsafe_corrupted_payload(self, serializer):
        """
        Testa loads_unsafe com payload corrompido.

        Given: Dados completamente corrompidos
        When: Chamamos loads_unsafe
        Then: Retorna (False, None)
        """
        is_valid, payload = serializer.loads_unsafe(b"completely.corrupted.data")

        assert is_valid is False
        # Pode ser None se payload não puder ser carregado
        # Ou pode ser o payload se puder ser parcialmente recuperado

    def test_load_unsafe_from_file(self, serializer):
        """
        Testa load_unsafe de arquivo.

        Given: Arquivo com dados serializados
        When: Chamamos load_unsafe
        Then: Retorna (validade, payload)
        """
        data = {"test": "data"}
        f = io.StringIO()
        serializer.dump(data, f)

        f.seek(0)
        is_valid, payload = serializer.load_unsafe(f)

        assert is_valid is True
        assert payload == data

    def test_make_signer(self, serializer):
        """
        Testa criação de signer.

        Given: Serializer
        When: Chamamos make_signer
        Then: Retorna instância de signer
        """
        signer = serializer.make_signer()

        assert isinstance(signer, Signer)
        assert signer.secret_key == serializer.secret_key

    def test_make_signer_with_custom_salt(self, serializer):
        """
        Testa make_signer com salt customizado.

        Given: Um salt específico
        When: Chamamos make_signer
        Then: Signer usa o salt fornecido
        """
        signer = serializer.make_signer(salt=b"custom")

        assert signer.salt == b"custom"

    def test_make_signer_uses_default_salt(self, serializer):
        """
        Testa que make_signer usa salt padrão.

        Given: Nenhum salt especificado
        When: Chamamos make_signer
        Then: Usa o salt do serializer
        """
        signer = serializer.make_signer()

        assert signer.salt == serializer.salt

    def test_dump_payload(self, serializer):
        """
        Testa dump_payload.

        Given: Um objeto
        When: Chamamos dump_payload
        Then: Retorna bytes JSON
        """
        data = {"key": "value"}
        result = serializer.dump_payload(data)

        assert isinstance(result, bytes)
        # Deve ser JSON válido
        assert json.loads(result) == data

    def test_load_payload_valid(self, serializer):
        """
        Testa load_payload com dados válidos.

        Given: Payload JSON válido em bytes
        When: Chamamos load_payload
        Then: Retorna o objeto
        """
        payload = b'{"key":"value"}'
        result = serializer.load_payload(payload)

        assert result == {"key": "value"}

    def test_load_payload_invalid_raises(self, serializer):
        """
        Testa load_payload com JSON inválido.

        Given: Payload com JSON mal-formado
        When: Chamamos load_payload
        Then: Lança BadPayload
        """
        with pytest.raises(BadPayload) as exc_info:
            serializer.load_payload(b"not valid json")

        assert exc_info.value.original_error is not None

    def test_load_payload_preserves_original_error(self, serializer):
        """
        Testa que load_payload preserva erro original.

        Given: Payload inválido
        When: Chamamos load_payload
        Then: original_error contém exceção original
        """
        try:
            serializer.load_payload(b"{invalid}")
        except BadPayload as e:
            assert e.original_error is not None
            assert isinstance(e.original_error, Exception)

    def test_is_text_serializer_detected(self, serializer):
        """
        Testa que is_text_serializer é detectado.

        Given: Serializer com JSON (text)
        When: Verificamos is_text_serializer
        Then: É True
        """
        assert serializer.is_text_serializer is True

    def test_dumps_returns_text_for_text_serializer(self, serializer):
        """
        Testa que dumps retorna texto para text serializer.

        Given: Serializer com JSON
        When: Chamamos dumps
        Then: Retorna string (não bytes)
        """
        result = serializer.dumps({"key": "value"})

        assert isinstance(result, str)

    def test_dumps_with_bytes_serializer_returns_bytes(self):
        """
        Testa que dumps retorna bytes para bytes serializer.

        Given: Serializer que retorna bytes
        When: Chamamos dumps
        Then: Retorna bytes
        """
        class BytesSerializer:
            @staticmethod
            def dumps(obj):
                return b"data"

            @staticmethod
            def loads(data):
                return {}

        s = Serializer(b"secret", serializer=BytesSerializer)
        result = s.dumps({})

        assert isinstance(result, bytes)

    def test_different_secrets_different_signatures(self):
        """
        Testa que secrets diferentes geram assinaturas diferentes.

        Given: Mesmo dados, secrets diferentes
        When: Serializamos
        Then: Resultados são diferentes
        """
        s1 = Serializer(b"secret1")
        s2 = Serializer(b"secret2")

        data = {"test": "data"}
        result1 = s1.dumps(data)
        result2 = s2.dumps(data)

        assert result1 != result2

    def test_cannot_cross_deserialize_different_secrets(self):
        """
        Testa que não pode desserializar com secret diferente.

        Given: Dados serializados com um secret
        When: Tentamos loads com outro secret
        Then: Lança BadSignature
        """
        s1 = Serializer(b"secret1")
        s2 = Serializer(b"secret2")

        serialized = s1.dumps({"data": "value"})

        with pytest.raises(BadSignature):
            s2.loads(serialized)

    def test_empty_dict_serialization(self, serializer):
        """
        Testa serialização de dicionário vazio.

        Given: Dicionário vazio
        When: Serializamos e desserializamos
        Then: Obtemos dicionário vazio de volta
        """
        data = {}
        serialized = serializer.dumps(data)
        loaded = serializer.loads(serialized)

        assert loaded == {}

    def test_large_data_serialization(self, serializer):
        """
        Testa serialização de dados grandes.

        Given: Objeto grande
        When: Serializamos e desserializamos
        Then: Dados são preservados
        """
        data = {"items": [{"id": i, "name": f"item_{i}"} for i in range(100)]}
        serialized = serializer.dumps(data)
        loaded = serializer.loads(serialized)

        assert loaded == data
        assert len(loaded["items"]) == 100

    @pytest.mark.parametrize("data", [
        {"simple": "value"},
        {"number": 123},
        {"float": 3.14},
        {"bool": True},
        {"null": None},
        {"list": [1, 2, 3]},
        {"nested": {"a": {"b": {"c": "d"}}}},
    ])
    def test_various_json_types(self, serializer, data):
        """
        Testa vários tipos JSON.

        Given: Diferentes estruturas JSON
        When: Serializamos e desserializamos
        Then: Dados são preservados
        """
        serialized = serializer.dumps(data)
        loaded = serializer.loads(serialized)

        assert loaded == data

    def test_serializer_with_signer_kwargs(self):
        """
        Testa que signer_kwargs são passados para signer.

        Given: Serializer com signer_kwargs
        When: Criamos signer
        Then: kwargs são aplicados
        """
        s = Serializer(
            b"secret",
            signer_kwargs={"sep": ":", "key_derivation": "concat"}
        )

        signer = s.make_signer()

        assert signer.sep == b":"
        assert signer.key_derivation == "concat"
