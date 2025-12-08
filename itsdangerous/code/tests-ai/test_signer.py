"""
Testes para o módulo signer

Este módulo testa as classes de assinatura incluindo SigningAlgorithm,
NoneAlgorithm, HMACAlgorithm, e Signer, que são fundamentais para a
segurança do itsdangerous.
"""
import hashlib
import pytest

from itsdangerous.signer import (
    SigningAlgorithm,
    NoneAlgorithm,
    HMACAlgorithm,
    Signer,
)
from itsdangerous.exc import BadSignature


class TestSigningAlgorithm:
    """Testes para a classe base SigningAlgorithm"""

    def test_is_abstract_base(self):
        """
        Testa que SigningAlgorithm é uma classe base abstrata.

        Given: A classe SigningAlgorithm
        When: Tentamos criar uma instância
        Then: Pode ser instanciada mas get_signature não funciona
        """
        algo = SigningAlgorithm()
        assert isinstance(algo, SigningAlgorithm)

    def test_get_signature_not_implemented(self):
        """
        Testa que get_signature lança NotImplementedError.

        Given: Uma instância de SigningAlgorithm
        When: Chamamos get_signature
        Then: Lança NotImplementedError
        """
        algo = SigningAlgorithm()

        with pytest.raises(NotImplementedError):
            algo.get_signature(b"key", b"value")

    def test_verify_signature_uses_get_signature(self):
        """
        Testa que verify_signature usa get_signature.

        Given: Uma subclasse que implementa get_signature
        When: Chamamos verify_signature
        Then: Usa get_signature para comparar
        """
        # Cria uma implementação simples para testar
        class SimpleAlgorithm(SigningAlgorithm):
            def get_signature(self, key, value):
                return b"fixed_signature"

        algo = SimpleAlgorithm()
        assert algo.verify_signature(b"key", b"value", b"fixed_signature") is True
        assert algo.verify_signature(b"key", b"value", b"wrong") is False


class TestNoneAlgorithm:
    """Testes para a classe NoneAlgorithm"""

    @pytest.fixture
    def none_algo(self):
        """Fixture que retorna uma instância de NoneAlgorithm"""
        return NoneAlgorithm()

    def test_get_signature_returns_empty(self, none_algo):
        """
        Testa que get_signature retorna bytes vazio.

        Given: NoneAlgorithm
        When: Chamamos get_signature
        Then: Retorna bytes vazio
        """
        sig = none_algo.get_signature(b"any_key", b"any_value")

        assert sig == b""
        assert isinstance(sig, bytes)

    def test_get_signature_ignores_parameters(self, none_algo):
        """
        Testa que parâmetros são ignorados.

        Given: Diferentes chaves e valores
        When: Chamamos get_signature
        Then: Sempre retorna bytes vazio
        """
        assert none_algo.get_signature(b"key1", b"val1") == b""
        assert none_algo.get_signature(b"key2", b"val2") == b""
        assert none_algo.get_signature(b"", b"") == b""

    def test_verify_signature_empty_bytes(self, none_algo):
        """
        Testa verificação com bytes vazio.

        Given: NoneAlgorithm
        When: Verificamos assinatura vazia
        Then: Retorna True
        """
        result = none_algo.verify_signature(b"key", b"value", b"")

        assert result is True

    def test_verify_signature_non_empty_fails(self, none_algo):
        """
        Testa que assinatura não-vazia falha.

        Given: NoneAlgorithm
        When: Verificamos assinatura não-vazia
        Then: Retorna False
        """
        result = none_algo.verify_signature(b"key", b"value", b"something")

        assert result is False

    def test_inherits_from_signing_algorithm(self, none_algo):
        """
        Testa herança de SigningAlgorithm.

        Given: NoneAlgorithm
        When: Verificamos tipo
        Then: É uma SigningAlgorithm
        """
        assert isinstance(none_algo, SigningAlgorithm)


class TestHMACAlgorithm:
    """Testes para a classe HMACAlgorithm"""

    @pytest.fixture
    def hmac_algo(self):
        """Fixture que retorna uma instância de HMACAlgorithm com SHA256"""
        return HMACAlgorithm(hashlib.sha256)

    def test_default_digest_method(self):
        """
        Testa que o método digest padrão é SHA512.

        Given: HMACAlgorithm sem parâmetros
        When: Criamos instância
        Then: Usa SHA512 como padrão
        """
        algo = HMACAlgorithm()

        assert algo.digest_method == hashlib.sha512

    def test_custom_digest_method(self):
        """
        Testa configuração de digest method customizado.

        Given: Um digest method específico
        When: Criamos HMACAlgorithm
        Then: Usa o método especificado
        """
        algo = HMACAlgorithm(hashlib.sha256)

        assert algo.digest_method == hashlib.sha256

    def test_get_signature_returns_bytes(self, hmac_algo):
        """
        Testa que get_signature retorna bytes.

        Given: HMACAlgorithm
        When: Chamamos get_signature
        Then: Retorna bytes
        """
        sig = hmac_algo.get_signature(b"secret_key", b"value")

        assert isinstance(sig, bytes)
        assert len(sig) > 0

    def test_get_signature_deterministic(self, hmac_algo):
        """
        Testa que assinaturas são determinísticas.

        Given: Mesma chave e valor
        When: Geramos assinatura múltiplas vezes
        Then: Sempre obtemos o mesmo resultado
        """
        sig1 = hmac_algo.get_signature(b"key", b"value")
        sig2 = hmac_algo.get_signature(b"key", b"value")

        assert sig1 == sig2

    def test_different_keys_different_signatures(self, hmac_algo):
        """
        Testa que chaves diferentes geram assinaturas diferentes.

        Given: Mesmo valor, chaves diferentes
        When: Geramos assinaturas
        Then: São diferentes
        """
        sig1 = hmac_algo.get_signature(b"key1", b"value")
        sig2 = hmac_algo.get_signature(b"key2", b"value")

        assert sig1 != sig2

    def test_different_values_different_signatures(self, hmac_algo):
        """
        Testa que valores diferentes geram assinaturas diferentes.

        Given: Mesma chave, valores diferentes
        When: Geramos assinaturas
        Then: São diferentes
        """
        sig1 = hmac_algo.get_signature(b"key", b"value1")
        sig2 = hmac_algo.get_signature(b"key", b"value2")

        assert sig1 != sig2

    def test_verify_signature_correct(self, hmac_algo):
        """
        Testa verificação de assinatura correta.

        Given: Assinatura válida
        When: Verificamos
        Then: Retorna True
        """
        key = b"secret"
        value = b"data"
        sig = hmac_algo.get_signature(key, value)

        assert hmac_algo.verify_signature(key, value, sig) is True

    def test_verify_signature_incorrect(self, hmac_algo):
        """
        Testa verificação de assinatura incorreta.

        Given: Assinatura inválida
        When: Verificamos
        Then: Retorna False
        """
        result = hmac_algo.verify_signature(b"key", b"value", b"wrong_signature")

        assert result is False

    def test_signature_length_matches_digest(self):
        """
        Testa que tamanho da assinatura corresponde ao digest.

        Given: Diferentes digest methods
        When: Geramos assinaturas
        Then: Tamanho corresponde ao digest
        """
        sha256_algo = HMACAlgorithm(hashlib.sha256)
        sha512_algo = HMACAlgorithm(hashlib.sha512)

        sig256 = sha256_algo.get_signature(b"key", b"value")
        sig512 = sha512_algo.get_signature(b"key", b"value")

        # SHA256 = 32 bytes, SHA512 = 64 bytes
        assert len(sig256) == 32
        assert len(sig512) == 64

    def test_inherits_from_signing_algorithm(self, hmac_algo):
        """
        Testa herança de SigningAlgorithm.

        Given: HMACAlgorithm
        When: Verificamos tipo
        Then: É uma SigningAlgorithm
        """
        assert isinstance(hmac_algo, SigningAlgorithm)


class TestSigner:
    """Testes para a classe Signer"""

    @pytest.fixture
    def signer(self):
        """Fixture que retorna um Signer básico"""
        return Signer(b"secret-key")

    def test_create_with_secret_key(self):
        """
        Testa criação com chave secreta.

        Given: Uma chave secreta
        When: Criamos Signer
        Then: É criado com sucesso
        """
        signer = Signer(b"my-secret")

        assert signer.secret_key == b"my-secret"

    def test_create_with_string_secret_key(self):
        """
        Testa criação com chave como string.

        Given: Chave como string
        When: Criamos Signer
        Then: É convertida para bytes
        """
        signer = Signer("my-secret")

        assert signer.secret_key == b"my-secret"

    def test_default_separator(self, signer):
        """
        Testa que separador padrão é '.'.

        Given: Signer sem sep especificado
        When: Verificamos o separador
        Then: É '.'
        """
        assert signer.sep == b"."

    def test_custom_separator(self):
        """
        Testa separador customizado.

        Given: Um separador específico
        When: Criamos Signer
        Then: Usa o separador especificado
        """
        signer = Signer(b"secret", sep=":")

        assert signer.sep == b":"

    def test_separator_cannot_be_in_base64_alphabet(self):
        """
        Testa que separador não pode estar no alfabeto base64.

        Given: Separador inválido (a-z, A-Z, 0-9, -, _, =)
        When: Criamos Signer
        Then: Lança ValueError
        """
        invalid_seps = ["a", "Z", "0", "-", "_", "="]

        for sep in invalid_seps:
            with pytest.raises(ValueError) as exc_info:
                Signer(b"secret", sep=sep)

            assert "cannot be used" in str(exc_info.value)

    def test_valid_separators(self):
        """
        Testa separadores válidos.

        Given: Separadores que não estão no alfabeto base64
        When: Criamos Signer
        Then: São aceitos
        """
        valid_seps = [".", ":", "|", "$", "#"]

        for sep in valid_seps:
            signer = Signer(b"secret", sep=sep)
            assert signer.sep == sep.encode()

    def test_default_salt(self, signer):
        """
        Testa que salt padrão é usado.

        Given: Signer sem salt especificado
        When: Verificamos o salt
        Then: Usa o padrão
        """
        assert signer.salt == "itsdangerous.Signer"

    def test_custom_salt(self):
        """
        Testa salt customizado.

        Given: Um salt específico
        When: Criamos Signer
        Then: Usa o salt especificado
        """
        signer = Signer(b"secret", salt="my-namespace")

        assert signer.salt == "my-namespace"

    def test_default_key_derivation(self, signer):
        """
        Testa que key derivation padrão é django-concat.

        Given: Signer sem key_derivation especificado
        When: Verificamos
        Then: É 'django-concat'
        """
        assert signer.key_derivation == "django-concat"

    def test_custom_key_derivation(self):
        """
        Testa key derivation customizada.

        Given: Um método de derivação específico
        When: Criamos Signer
        Then: Usa o método especificado
        """
        for method in ["concat", "hmac", "none"]:
            signer = Signer(b"secret", key_derivation=method)
            assert signer.key_derivation == method

    def test_default_algorithm_is_hmac(self, signer):
        """
        Testa que algoritmo padrão é HMAC.

        Given: Signer sem algorithm especificado
        When: Verificamos o algoritmo
        Then: É HMACAlgorithm
        """
        assert isinstance(signer.algorithm, HMACAlgorithm)

    def test_custom_algorithm(self):
        """
        Testa algoritmo customizado.

        Given: Um algoritmo específico
        When: Criamos Signer
        Then: Usa o algoritmo especificado
        """
        algo = NoneAlgorithm()
        signer = Signer(b"secret", algorithm=algo)

        assert signer.algorithm is algo

    def test_sign_returns_signed_value(self, signer):
        """
        Testa que sign retorna valor assinado.

        Given: Um valor
        When: Assinamos
        Then: Retorna valor + separador + assinatura
        """
        signed = signer.sign(b"value")

        assert isinstance(signed, bytes)
        assert b"." in signed
        assert signed.startswith(b"value.")

    def test_sign_with_string_input(self, signer):
        """
        Testa assinatura com string.

        Given: Uma string
        When: Assinamos
        Then: É convertida e assinada
        """
        signed = signer.sign("value")

        assert isinstance(signed, bytes)
        assert signed.startswith(b"value.")

    def test_unsign_valid_signature(self, signer):
        """
        Testa unsign com assinatura válida.

        Given: Valor assinado corretamente
        When: Chamamos unsign
        Then: Retorna o valor original
        """
        signed = signer.sign(b"myvalue")
        unsigned = signer.unsign(signed)

        assert unsigned == b"myvalue"

    def test_unsign_invalid_signature_raises(self, signer):
        """
        Testa unsign com assinatura inválida.

        Given: Assinatura adulterada
        When: Chamamos unsign
        Then: Lança BadSignature
        """
        signed = signer.sign(b"value")
        tampered = signed[:-1] + b"X"  # Adultera último byte

        with pytest.raises(BadSignature) as exc_info:
            signer.unsign(tampered)

        assert "does not match" in str(exc_info.value)

    def test_unsign_no_separator_raises(self, signer):
        """
        Testa unsign sem separador.

        Given: Valor sem separador
        When: Chamamos unsign
        Then: Lança BadSignature
        """
        with pytest.raises(BadSignature) as exc_info:
            signer.unsign(b"noseparator")

        assert "No" in str(exc_info.value)
        assert "found" in str(exc_info.value)

    def test_unsign_preserves_payload_on_error(self, signer):
        """
        Testa que payload é preservado em erro.

        Given: Assinatura inválida
        When: Chamamos unsign e capturamos exceção
        Then: payload está disponível na exceção
        """
        with pytest.raises(BadSignature) as exc_info:
            signer.unsign(b"value.invalidsig")

        assert exc_info.value.payload == b"value"

    def test_validate_returns_true_for_valid(self, signer):
        """
        Testa validate com assinatura válida.

        Given: Valor assinado corretamente
        When: Chamamos validate
        Then: Retorna True
        """
        signed = signer.sign(b"value")

        assert signer.validate(signed) is True

    def test_validate_returns_false_for_invalid(self, signer):
        """
        Testa validate com assinatura inválida.

        Given: Assinatura inválida
        When: Chamamos validate
        Then: Retorna False
        """
        assert signer.validate(b"value.badsig") is False

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
            b"special@#$%chars",
            b"\x00\x01\x02",
            b"a" * 100,
        ]

        for value in values:
            signed = signer.sign(value)
            unsigned = signer.unsign(signed)
            assert unsigned == value

    def test_different_salts_different_signatures(self):
        """
        Testa que salts diferentes geram assinaturas diferentes.

        Given: Mesmo secret e valor, salts diferentes
        When: Assinamos
        Then: Assinaturas são diferentes
        """
        signer1 = Signer(b"secret", salt="salt1")
        signer2 = Signer(b"secret", salt="salt2")

        sig1 = signer1.sign(b"value")
        sig2 = signer2.sign(b"value")

        assert sig1 != sig2

    def test_salt_namespaces_signatures(self):
        """
        Testa que salt cria namespaces.

        Given: Signers com salts diferentes
        When: Um assina e outro tenta desassinar
        Then: Falha a verificação
        """
        signer1 = Signer(b"secret", salt="namespace1")
        signer2 = Signer(b"secret", salt="namespace2")

        signed = signer1.sign(b"value")

        with pytest.raises(BadSignature):
            signer2.unsign(signed)

    def test_derive_key_concat(self):
        """
        Testa derivação de chave com método 'concat'.

        Given: Signer com key_derivation='concat'
        When: Derivamos chave
        Then: Usa hash(salt + secret_key)
        """
        signer = Signer(b"secret", salt="mysalt", key_derivation="concat")
        key = signer.derive_key()

        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_derive_key_django_concat(self):
        """
        Testa derivação de chave com método 'django-concat'.

        Given: Signer com key_derivation='django-concat'
        When: Derivamos chave
        Then: Usa hash(salt + 'signer' + secret_key)
        """
        signer = Signer(b"secret", salt="mysalt", key_derivation="django-concat")
        key = signer.derive_key()

        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_derive_key_hmac(self):
        """
        Testa derivação de chave com método 'hmac'.

        Given: Signer com key_derivation='hmac'
        When: Derivamos chave
        Then: Usa HMAC(secret_key, salt)
        """
        signer = Signer(b"secret", salt="mysalt", key_derivation="hmac")
        key = signer.derive_key()

        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_derive_key_none(self):
        """
        Testa derivação de chave com método 'none'.

        Given: Signer com key_derivation='none'
        When: Derivamos chave
        Then: Retorna secret_key diretamente
        """
        signer = Signer(b"secret", key_derivation="none")
        key = signer.derive_key()

        assert key == b"secret"

    def test_derive_key_unknown_method_raises(self):
        """
        Testa que método desconhecido lança erro.

        Given: Signer com key_derivation inválida
        When: Derivamos chave
        Then: Lança TypeError
        """
        signer = Signer(b"secret", key_derivation="invalid")

        with pytest.raises(TypeError) as exc_info:
            signer.derive_key()

        assert "Unknown key derivation method" in str(exc_info.value)

    def test_get_signature_returns_base64(self, signer):
        """
        Testa que get_signature retorna base64.

        Given: Um valor
        When: Chamamos get_signature
        Then: Retorna assinatura em base64
        """
        sig = signer.get_signature(b"value")

        assert isinstance(sig, bytes)
        # Base64 não tem caracteres especiais além de alfabeto
        assert all(c in b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in sig)

    def test_verify_signature_valid(self, signer):
        """
        Testa verificação de assinatura válida.

        Given: Valor e assinatura corretos
        When: Chamamos verify_signature
        Then: Retorna True
        """
        value = b"testvalue"
        sig = signer.get_signature(value)

        assert signer.verify_signature(value, sig) is True

    def test_verify_signature_invalid(self, signer):
        """
        Testa verificação de assinatura inválida.

        Given: Assinatura incorreta
        When: Chamamos verify_signature
        Then: Retorna False
        """
        assert signer.verify_signature(b"value", b"badsignature") is False

    def test_verify_signature_handles_decode_error(self, signer):
        """
        Testa que erros de decodificação retornam False.

        Given: Assinatura que não é base64 válido
        When: Chamamos verify_signature
        Then: Retorna False (não lança exceção)
        """
        result = signer.verify_signature(b"value", b"!!!")

        assert result is False

    @pytest.mark.parametrize("secret,value", [
        (b"secret1", b"value1"),
        (b"another-secret", b"another-value"),
        ("string-secret", "string-value"),
        (b"", b"empty-secret-value"),
    ])
    def test_various_sign_unsign_combinations(self, secret, value):
        """
        Testa várias combinações de chave e valor.

        Given: Diferentes chaves e valores
        When: Assinamos e desassinamos
        Then: Processo funciona corretamente
        """
        signer = Signer(secret)
        signed = signer.sign(value)
        unsigned = signer.unsign(signed)

        # Converte para bytes para comparação
        from itsdangerous.encoding import want_bytes
        assert unsigned == want_bytes(value)
