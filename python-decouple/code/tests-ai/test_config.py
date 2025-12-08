"""
Testes para a classe Config

Este módulo testa a classe Config, que é responsável por obter valores de
configuração de diferentes repositórios com suporte a valores padrão e casting.
"""
import os
import pytest
from decouple import Config, UndefinedValueError, undefined


class MockRepository:
    """Mock de repositório para testes"""

    def __init__(self, data=None):
        self.data = data or {}

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]


class TestConfig:
    """Testes para a classe Config"""

    @pytest.fixture
    def repository(self):
        """Fixture que retorna um repositório mock"""
        return MockRepository({
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://localhost/db",
            "PORT": "8000",
            "EMPTY_VALUE": "",
            "ZERO": "0",
        })

    @pytest.fixture
    def config(self, repository):
        """Fixture que retorna uma instância de Config"""
        return Config(repository)

    @pytest.fixture
    def empty_config(self):
        """Fixture que retorna Config com repositório vazio"""
        return Config(MockRepository())

    @pytest.fixture(autouse=True)
    def clean_env(self):
        """Limpa variáveis de ambiente antes de cada teste"""
        test_vars = ["DEBUG", "DATABASE_URL", "PORT", "EMPTY_VALUE", "ZERO", "TEST_VAR"]
        original_values = {}

        # Salva valores originais
        for var in test_vars:
            if var in os.environ:
                original_values[var] = os.environ[var]
                del os.environ[var]

        yield

        # Restaura valores originais
        for var in test_vars:
            if var in os.environ:
                del os.environ[var]
            if var in original_values:
                os.environ[var] = original_values[var]

    def test_config_init(self, repository):
        """
        Testa inicialização do Config.

        Given: Um repositório
        When: Criamos uma instância de Config
        Then: O repositório é armazenado corretamente
        """
        config = Config(repository)
        assert config.repository is repository

    def test_get_from_repository(self, config):
        """
        Testa obtenção de valor do repositório.

        Given: Um valor armazenado no repositório
        When: Chamamos get
        Then: Retorna o valor do repositório
        """
        result = config.get("DATABASE_URL")
        assert result == "postgresql://localhost/db"

    def test_get_from_environment_overrides_repository(self, config):
        """
        Testa que variável de ambiente tem prioridade sobre repositório.

        Given: Um valor no repositório e no ambiente
        When: Chamamos get
        Then: Retorna o valor do ambiente
        """
        os.environ["DATABASE_URL"] = "postgresql://prod/db"
        result = config.get("DATABASE_URL")
        assert result == "postgresql://prod/db"

    def test_get_with_default(self, empty_config):
        """
        Testa obtenção com valor padrão.

        Given: Uma chave que não existe
        When: Chamamos get com default
        Then: Retorna o valor padrão
        """
        result = empty_config.get("MISSING_KEY", default="default_value")
        assert result == "default_value"

    def test_get_without_default_raises_error(self, empty_config):
        """
        Testa que get sem default lança erro quando chave não existe.

        Given: Uma chave que não existe e sem default
        When: Chamamos get
        Then: Lança UndefinedValueError
        """
        with pytest.raises(UndefinedValueError) as exc_info:
            empty_config.get("MISSING_KEY")

        assert "MISSING_KEY" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_get_with_cast_int(self, config):
        """
        Testa casting para int.

        Given: Um valor string numérico
        When: Chamamos get com cast=int
        Then: Retorna um inteiro
        """
        result = config.get("PORT", cast=int)
        assert result == 8000
        assert isinstance(result, int)

    def test_get_with_cast_bool(self, config):
        """
        Testa casting para bool.

        Given: Um valor string booleano
        When: Chamamos get com cast=bool
        Then: Usa _cast_boolean
        """
        result = config.get("DEBUG", cast=bool)
        assert result is True
        assert isinstance(result, bool)

    def test_get_with_cast_str(self, config):
        """
        Testa casting para str.

        Given: Um valor
        When: Chamamos get com cast=str
        Then: Retorna string
        """
        result = config.get("PORT", cast=str)
        assert result == "8000"
        assert isinstance(result, str)

    def test_get_with_custom_cast(self, config):
        """
        Testa casting com função customizada.

        Given: Uma função de casting customizada
        When: Chamamos get com essa função
        Then: O valor é transformado pela função
        """
        def custom_cast(value):
            return f"custom_{value}"

        result = config.get("DATABASE_URL", cast=custom_cast)
        assert result == "custom_postgresql://localhost/db"

    def test_get_without_cast(self, config):
        """
        Testa get sem casting.

        Given: Um valor sem especificar cast
        When: Chamamos get
        Then: Retorna o valor sem transformação
        """
        result = config.get("DATABASE_URL")
        assert result == "postgresql://localhost/db"

    def test_call_method_delegates_to_get(self, config):
        """
        Testa que __call__ delega para get.

        Given: Um config
        When: Chamamos config como função
        Then: Comporta-se como get
        """
        result = config("DATABASE_URL")
        assert result == "postgresql://localhost/db"

    def test_call_with_default(self, empty_config):
        """
        Testa __call__ com default.

        Given: Uma chave inexistente
        When: Chamamos config como função com default
        Then: Retorna o default
        """
        result = empty_config("MISSING", default="default")
        assert result == "default"

    def test_call_with_cast(self, config):
        """
        Testa __call__ com cast.

        Given: Um valor
        When: Chamamos config como função com cast
        Then: Aplica o cast
        """
        result = config("PORT", cast=int)
        assert result == 8000

    def test_cast_boolean_with_true_string(self, config):
        """
        Testa _cast_boolean com string "true".

        Given: Uma string "true"
        When: Chamamos get com cast=bool
        Then: Retorna True
        """
        result = config.get("DEBUG", cast=bool)
        assert result is True

    def test_cast_boolean_with_false_string(self, config):
        """
        Testa _cast_boolean com string "false" (0).

        Given: Uma string "0"
        When: Chamamos get com cast=bool
        Then: Retorna False
        """
        result = config.get("ZERO", cast=bool)
        assert result is False

    def test_cast_boolean_with_empty_string(self, config):
        """
        Testa _cast_boolean com string vazia.

        Given: Uma string vazia
        When: Chamamos get com cast=bool
        Then: Retorna False (bool('') é False)
        """
        result = config.get("EMPTY_VALUE", cast=bool)
        assert result is False

    def test_cast_do_nothing(self, config):
        """
        Testa _cast_do_nothing.

        Given: Um valor
        When: Usamos cast=undefined (não especificado)
        Then: Retorna o valor sem modificação
        """
        result = config.get("DATABASE_URL", cast=config._cast_do_nothing)
        assert result == "postgresql://localhost/db"

    def test_default_none_is_valid(self, empty_config):
        """
        Testa que None é um default válido.

        Given: default=None
        When: Chamamos get
        Then: Retorna None (não lança erro)
        """
        result = empty_config.get("MISSING", default=None)
        assert result is None

    def test_default_empty_string_is_valid(self, empty_config):
        """
        Testa que string vazia é um default válido.

        Given: default=""
        When: Chamamos get
        Then: Retorna string vazia
        """
        result = empty_config.get("MISSING", default="")
        assert result == ""

    def test_default_zero_is_valid(self, empty_config):
        """
        Testa que 0 é um default válido.

        Given: default=0
        When: Chamamos get
        Then: Retorna 0
        """
        result = empty_config.get("MISSING", default=0)
        assert result == 0

    def test_cast_with_default(self, empty_config):
        """
        Testa que cast é aplicado ao default.

        Given: Um default e um cast
        When: Chamamos get
        Then: O cast é aplicado ao default
        """
        result = empty_config.get("MISSING", default="123", cast=int)
        assert result == 123
        assert isinstance(result, int)

    @pytest.mark.parametrize("bool_value,expected", [
        ("true", True),
        ("false", False),
        ("yes", True),
        ("no", False),
        ("1", True),
        ("0", False),
    ])
    def test_cast_boolean_various_values(self, bool_value, expected, empty_config):
        """
        Testa _cast_boolean com vários valores.

        Given: Diferentes valores booleanos como string
        When: Aplicamos cast=bool
        Then: Converte corretamente
        """
        os.environ["TEST_VAR"] = bool_value
        result = empty_config.get("TEST_VAR", cast=bool)
        assert result is expected

    def test_environment_variable_priority(self, config):
        """
        Testa ordem de prioridade: ambiente > repositório.

        Given: Mesmo valor em ambiente e repositório
        When: Chamamos get
        Then: Prioriza ambiente
        """
        # Valor no repositório: "8000"
        result_repo = config.get("PORT")
        assert result_repo == "8000"

        # Define no ambiente
        os.environ["PORT"] = "9000"
        result_env = config.get("PORT")
        assert result_env == "9000"

    def test_get_with_cast_error_propagates(self, config):
        """
        Testa que erros de casting são propagados.

        Given: Um valor que não pode ser convertido
        When: Aplicamos cast
        Then: Lança a exceção do cast
        """
        with pytest.raises(ValueError):
            config.get("DATABASE_URL", cast=int)

    def test_repository_empty_value(self, config):
        """
        Testa obtenção de valor vazio do repositório.

        Given: Um valor vazio no repositório
        When: Chamamos get
        Then: Retorna string vazia (não usa default)
        """
        result = config.get("EMPTY_VALUE", default="should_not_use")
        assert result == ""

    def test_undefined_as_default_raises_error(self, empty_config):
        """
        Testa que undefined como default lança erro.

        Given: default=undefined
        When: Chave não existe
        Then: Lança UndefinedValueError
        """
        with pytest.raises(UndefinedValueError):
            empty_config.get("MISSING", default=undefined)

    def test_multiple_gets_same_value(self, config):
        """
        Testa múltiplas chamadas get retornam mesmo valor.

        Given: Um config
        When: Chamamos get múltiplas vezes
        Then: Retorna o mesmo valor
        """
        result1 = config.get("DATABASE_URL")
        result2 = config.get("DATABASE_URL")
        result3 = config.get("DATABASE_URL")

        assert result1 == result2 == result3
