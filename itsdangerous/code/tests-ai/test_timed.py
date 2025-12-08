"""
Testes para o módulo timed

Este módulo testa TimestampSigner e TimedSerializer, que adicionam
funcionalidade de timestamp e expiração às assinaturas.
"""
import time
import pytest
from datetime import datetime
from freezegun import freeze_time

from itsdangerous.timed import TimestampSigner, TimedSerializer
from itsdangerous.exc import BadSignature, BadTimeSignature, SignatureExpired


class TestTimestampSigner:
    """Testes para a classe TimestampSigner"""

    @pytest.fixture
    def signer(self):
        """Fixture que retorna um TimestampSigner básico"""
        return TimestampSigner(b"secret-key")

    def test_create_with_secret_key(self):
        """
        Testa criação com chave secreta.

        Given: Uma chave secreta
        When: Criamos TimestampSigner
        Then: É criado com sucesso
        """
        signer = TimestampSigner(b"my-secret")

        assert signer.secret_key == b"my-secret"

    def test_get_timestamp_returns_int(self, signer):
        """
        Testa que get_timestamp retorna inteiro.

        Given: TimestampSigner
        When: Chamamos get_timestamp
        Then: Retorna timestamp inteiro
        """
        timestamp = signer.get_timestamp()

        assert isinstance(timestamp, int)
        assert timestamp > 0

    @freeze_time("2024-01-01 12:00:00")
    def test_get_timestamp_returns_current_time(self, signer):
        """
        Testa que get_timestamp retorna tempo atual.

        Given: Tempo congelado
        When: Chamamos get_timestamp
        Then: Retorna timestamp correto
        """
        timestamp = signer.get_timestamp()
        expected = int(time.time())

        assert timestamp == expected

    def test_timestamp_to_datetime(self, signer):
        """
        Testa conversão de timestamp para datetime.

        Given: Um timestamp
        When: Chamamos timestamp_to_datetime
        Then: Retorna datetime correspondente
        """
        timestamp = 1704110400  # 2024-01-01 12:00:00 UTC
        dt = signer.timestamp_to_datetime(timestamp)

        assert isinstance(dt, datetime)
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_sign_includes_timestamp(self, signer):
        """
        Testa que sign inclui timestamp.

        Given: Um valor
        When: Assinamos
        Then: Resultado contém timestamp
        """
        signed = signer.sign(b"value")

        # Formato: value.timestamp.signature
        assert signed.count(b".") >= 2
        assert signed.startswith(b"value.")

    @freeze_time("2024-01-01 12:00:00")
    def test_sign_creates_verifiable_signature(self, signer):
        """
        Testa que assinatura criada pode ser verificada.

        Given: Valor assinado
        When: Desassinamos
        Then: Obtemos valor original
        """
        signed = signer.sign(b"myvalue")
        unsigned = signer.unsign(signed)

        assert unsigned == b"myvalue"

    def test_unsign_valid_signature(self, signer):
        """
        Testa unsign com assinatura válida.

        Given: Valor assinado corretamente
        When: Chamamos unsign
        Then: Retorna valor original
        """
        signed = signer.sign(b"test")
        unsigned = signer.unsign(signed)

        assert unsigned == b"test"

    def test_unsign_invalid_signature_raises(self, signer):
        """
        Testa unsign com assinatura inválida.

        Given: Assinatura adulterada
        When: Chamamos unsign
        Then: Lança BadTimeSignature
        """
        signed = signer.sign(b"value")
        tampered = signed[:-5] + b"XXXXX"

        with pytest.raises(BadTimeSignature):
            signer.unsign(tampered)

    def test_unsign_returns_timestamp_when_requested(self, signer):
        """
        Testa unsign com return_timestamp=True.

        Given: Valor assinado
        When: Chamamos unsign com return_timestamp=True
        Then: Retorna (valor, datetime)
        """
        signed = signer.sign(b"value")
        value, timestamp = signer.unsign(signed, return_timestamp=True)

        assert value == b"value"
        assert isinstance(timestamp, datetime)

    @freeze_time("2024-01-01 12:00:00")
    def test_unsign_with_max_age_valid(self, signer):
        """
        Testa unsign com max_age para assinatura recente.

        Given: Assinatura recente
        When: Chamamos unsign com max_age
        Then: Funciona sem erro
        """
        signed = signer.sign(b"value")

        # max_age de 60 segundos, assinatura acabou de ser criada
        unsigned = signer.unsign(signed, max_age=60)

        assert unsigned == b"value"

    @freeze_time("2024-01-01 12:00:00")
    def test_unsign_with_max_age_expired_raises(self, signer):
        """
        Testa unsign com max_age para assinatura expirada.

        Given: Assinatura antiga
        When: Chamamos unsign com max_age pequeno
        Then: Lança SignatureExpired
        """
        # Assina no tempo congelado
        signed = signer.sign(b"value")

        # Avança o tempo 2 horas (7200 segundos)
        with freeze_time("2024-01-01 14:00:00"):
            with pytest.raises(SignatureExpired) as exc_info:
                signer.unsign(signed, max_age=3600)  # max_age = 1 hora

            # Verifica que a exceção contém informações úteis
            assert exc_info.value.payload == b"value"
            assert exc_info.value.date_signed is not None

    @freeze_time("2024-01-01 12:00:00")
    def test_expired_signature_includes_age_info(self, signer):
        """
        Testa que SignatureExpired inclui informação de idade.

        Given: Assinatura expirada
        When: Tentamos unsign
        Then: Exceção contém idade e max_age
        """
        signed = signer.sign(b"value")

        with freeze_time("2024-01-01 14:00:00"):  # +2 horas
            with pytest.raises(SignatureExpired) as exc_info:
                signer.unsign(signed, max_age=3600)

            error_msg = str(exc_info.value)
            assert "7200" in error_msg  # Idade em segundos
            assert "3600" in error_msg  # max_age

    def test_unsign_missing_timestamp_raises(self, signer):
        """
        Testa unsign com timestamp ausente.

        Given: Valor sem timestamp
        When: Chamamos unsign
        Then: Lança BadTimeSignature
        """
        # Cria assinatura sem timestamp usando Signer normal
        from itsdangerous.signer import Signer
        normal_signer = Signer(b"secret-key")
        signed = normal_signer.sign(b"value")

        with pytest.raises(BadTimeSignature) as exc_info:
            signer.unsign(signed)

        assert "timestamp missing" in str(exc_info.value)

    def test_unsign_malformed_timestamp_raises(self, signer):
        """
        Testa unsign com timestamp malformado.

        Given: Timestamp que não pode ser decodificado
        When: Chamamos unsign
        Then: Lança BadTimeSignature
        """
        # Manualmente cria algo com timestamp inválido
        # Formato esperado: value.timestamp.signature
        # Vamos criar com timestamp inválido mas assinatura válida
        signed = signer.sign(b"value")
        parts = signed.rsplit(b".", 2)
        # Substitui timestamp por algo inválido
        malformed = parts[0] + b".!!!" + b"." + parts[2]

        with pytest.raises(BadTimeSignature):
            signer.unsign(malformed)

    def test_validate_with_valid_signature(self, signer):
        """
        Testa validate com assinatura válida.

        Given: Assinatura válida
        When: Chamamos validate
        Then: Retorna True
        """
        signed = signer.sign(b"value")

        assert signer.validate(signed) is True

    def test_validate_with_invalid_signature(self, signer):
        """
        Testa validate com assinatura inválida.

        Given: Assinatura inválida
        When: Chamamos validate
        Then: Retorna False
        """
        assert signer.validate(b"invalid.signature.here") is False

    @freeze_time("2024-01-01 12:00:00")
    def test_validate_with_max_age_valid(self, signer):
        """
        Testa validate com max_age para assinatura válida.

        Given: Assinatura recente
        When: Chamamos validate com max_age
        Then: Retorna True
        """
        signed = signer.sign(b"value")

        assert signer.validate(signed, max_age=3600) is True

    @freeze_time("2024-01-01 12:00:00")
    def test_validate_with_max_age_expired(self, signer):
        """
        Testa validate com max_age para assinatura expirada.

        Given: Assinatura antiga
        When: Chamamos validate com max_age
        Then: Retorna False
        """
        signed = signer.sign(b"value")

        with freeze_time("2024-01-01 14:00:00"):
            assert signer.validate(signed, max_age=3600) is False

    def test_roundtrip_sign_unsign(self, signer):
        """
        Testa roundtrip completo sign -> unsign.

        Given: Diferentes valores
        When: Assinamos e desassinamos
        Then: Obtemos valores originais
        """
        values = [
            b"simple",
            b"with spaces",
            b"special@chars",
            b"\x00\x01\x02",
        ]

        for value in values:
            signed = signer.sign(value)
            unsigned = signer.unsign(signed)
            assert unsigned == value

    @freeze_time("2024-01-01 12:00:00")
    def test_timestamp_preserved_in_signature(self, signer):
        """
        Testa que timestamp é preservado na assinatura.

        Given: Tempo congelado
        When: Assinamos e desassinamos com return_timestamp
        Then: Timestamp corresponde ao tempo de assinatura
        """
        expected_time = datetime(2024, 1, 1, 12, 0, 0)
        signed = signer.sign(b"value")

        value, timestamp = signer.unsign(signed, return_timestamp=True)

        assert timestamp == expected_time

    def test_different_timestamps_different_signatures(self, signer):
        """
        Testa que timestamps diferentes geram assinaturas diferentes.

        Given: Mesmo valor assinado em momentos diferentes
        When: Comparamos assinaturas
        Then: São diferentes devido ao timestamp
        """
        signed1 = signer.sign(b"value")
        time.sleep(0.01)  # Pequeno delay para mudar timestamp
        signed2 = signer.sign(b"value")

        assert signed1 != signed2


class TestTimedSerializer:
    """Testes para a classe TimedSerializer"""

    @pytest.fixture
    def serializer(self):
        """Fixture que retorna um TimedSerializer básico"""
        return TimedSerializer(b"secret-key")

    def test_create_with_secret_key(self):
        """
        Testa criação com chave secreta.

        Given: Uma chave secreta
        When: Criamos TimedSerializer
        Then: É criado com sucesso
        """
        s = TimedSerializer(b"my-secret")

        assert s.secret_key == b"my-secret"

    def test_default_signer_is_timestamp_signer(self, serializer):
        """
        Testa que signer padrão é TimestampSigner.

        Given: TimedSerializer
        When: Verificamos default_signer
        Then: É TimestampSigner
        """
        assert serializer.default_signer is TimestampSigner

    def test_dumps_creates_timestamped_signature(self, serializer):
        """
        Testa que dumps cria assinatura com timestamp.

        Given: Um objeto
        When: Chamamos dumps
        Then: Resultado contém timestamp
        """
        data = {"key": "value"}
        result = serializer.dumps(data)

        # Deve ter múltiplos pontos (valor.timestamp.signature)
        assert result.count(".") >= 2

    def test_loads_valid_data(self, serializer):
        """
        Testa loads com dados válidos.

        Given: Dados serializados corretamente
        When: Chamamos loads
        Then: Retorna objeto original
        """
        data = {"key": "value", "number": 42}
        serialized = serializer.dumps(data)
        loaded = serializer.loads(serialized)

        assert loaded == data

    def test_loads_returns_timestamp_when_requested(self, serializer):
        """
        Testa loads com return_timestamp=True.

        Given: Dados serializados
        When: Chamamos loads com return_timestamp=True
        Then: Retorna (payload, timestamp)
        """
        data = {"key": "value"}
        serialized = serializer.dumps(data)

        payload, timestamp = serializer.loads(serialized, return_timestamp=True)

        assert payload == data
        assert isinstance(timestamp, datetime)

    @freeze_time("2024-01-01 12:00:00")
    def test_loads_with_max_age_valid(self, serializer):
        """
        Testa loads com max_age para dados recentes.

        Given: Dados serializados recentemente
        When: Chamamos loads com max_age
        Then: Funciona sem erro
        """
        data = {"test": "data"}
        serialized = serializer.dumps(data)

        loaded = serializer.loads(serialized, max_age=3600)

        assert loaded == data

    @freeze_time("2024-01-01 12:00:00")
    def test_loads_with_max_age_expired_raises(self, serializer):
        """
        Testa loads com max_age para dados expirados.

        Given: Dados antigos
        When: Chamamos loads com max_age pequeno
        Then: Lança SignatureExpired
        """
        data = {"test": "data"}
        serialized = serializer.dumps(data)

        with freeze_time("2024-01-01 14:00:00"):  # +2 horas
            with pytest.raises(SignatureExpired):
                serializer.loads(serialized, max_age=3600)

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

    def test_loads_with_salt(self, serializer):
        """
        Testa loads com salt específico.

        Given: Dados serializados com salt
        When: Chamamos loads com mesmo salt
        Then: Funciona corretamente
        """
        data = {"test": "data"}
        serialized = serializer.dumps(data, salt="mysalt")
        loaded = serializer.loads(serialized, salt="mysalt")

        assert loaded == data

    def test_loads_with_wrong_salt_raises(self, serializer):
        """
        Testa loads com salt errado.

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

        Given: Diferentes tipos de objetos
        When: Serializamos e desserializamos
        Then: Obtemos objetos originais
        """
        test_cases = [
            {"simple": "dict"},
            {"nested": {"dict": {"key": "value"}}},
            [1, 2, 3, 4],
            {"unicode": "São Paulo 🇧🇷"},
        ]

        for data in test_cases:
            serialized = serializer.dumps(data)
            loaded = serializer.loads(serialized)
            assert loaded == data

    @freeze_time("2024-01-01 12:00:00")
    def test_timestamp_corresponds_to_serialization_time(self, serializer):
        """
        Testa que timestamp corresponde ao tempo de serialização.

        Given: Tempo congelado
        When: Serializamos e desserializamos com return_timestamp
        Then: Timestamp corresponde ao tempo correto
        """
        expected_time = datetime(2024, 1, 1, 12, 0, 0)
        data = {"key": "value"}
        serialized = serializer.dumps(data)

        payload, timestamp = serializer.loads(serialized, return_timestamp=True)

        assert timestamp == expected_time

    def test_loads_unsafe_valid_signature(self, serializer):
        """
        Testa loads_unsafe com assinatura válida.

        Given: Dados válidos
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

        Given: Assinatura adulterada
        When: Chamamos loads_unsafe
        Then: Retorna (False, payload) se possível
        """
        serialized = serializer.dumps({"key": "value"})
        parts = serialized.rsplit(".", 1)
        tampered = parts[0] + ".tampered"

        is_valid, payload = serializer.loads_unsafe(tampered)

        assert is_valid is False

    @freeze_time("2024-01-01 12:00:00")
    def test_loads_unsafe_with_max_age(self, serializer):
        """
        Testa loads_unsafe com max_age.

        Given: Dados antigos
        When: Chamamos loads_unsafe com max_age
        Then: Retorna (False, payload) se expirado
        """
        data = {"test": "data"}
        serialized = serializer.dumps(data)

        with freeze_time("2024-01-01 14:00:00"):  # +2 horas
            is_valid, payload = serializer.loads_unsafe(serialized, max_age=3600)

            assert is_valid is False

    def test_different_secrets_different_signatures(self):
        """
        Testa que secrets diferentes geram assinaturas diferentes.

        Given: Mesmo dados, secrets diferentes
        When: Serializamos
        Then: Resultados são diferentes
        """
        s1 = TimedSerializer(b"secret1")
        s2 = TimedSerializer(b"secret2")

        data = {"test": "data"}
        result1 = s1.dumps(data)
        result2 = s2.dumps(data)

        assert result1 != result2

    @freeze_time("2024-01-01 12:00:00")
    def test_max_age_zero_requires_instant_use(self, serializer):
        """
        Testa que max_age=0 requer uso instantâneo.

        Given: Assinatura criada
        When: Mesmo sem delay, max_age=0
        Then: Pode falhar dependendo da precisão
        """
        # max_age=0 significa que deve ser usado no mesmo segundo
        data = {"test": "data"}
        serialized = serializer.dumps(data)

        # No mesmo tempo congelado, deve funcionar
        loaded = serializer.loads(serialized, max_age=0)
        assert loaded == data

        # Após 1 segundo, deve falhar
        with freeze_time("2024-01-01 12:00:01"):
            with pytest.raises(SignatureExpired):
                serializer.loads(serialized, max_age=0)

    @freeze_time("2024-01-01 12:00:00")
    def test_max_age_boundary(self, serializer):
        """
        Testa limite exato de max_age.

        Given: Assinatura com idade exata de max_age
        When: Chamamos loads
        Then: Pode funcionar ou falhar dependendo da implementação
        """
        data = {"test": "data"}
        serialized = serializer.dumps(data)

        # Exatamente max_age segundos depois
        with freeze_time("2024-01-01 13:00:00"):  # +1 hora = 3600s
            # age = 3600, max_age = 3600
            # Implementação usa age > max_age, então deve funcionar
            loaded = serializer.loads(serialized, max_age=3600)
            assert loaded == data

        # Um segundo a mais deve falhar
        with freeze_time("2024-01-01 13:00:01"):  # +3601s
            with pytest.raises(SignatureExpired):
                serializer.loads(serialized, max_age=3600)
