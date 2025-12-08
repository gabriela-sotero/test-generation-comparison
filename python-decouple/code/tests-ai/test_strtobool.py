"""
Testes para a função strtobool

Este módulo testa a função strtobool que converte strings em valores booleanos,
incluindo tratamento de valores verdadeiros, falsos e inválidos.
"""
import pytest
from decouple import strtobool


class TestStrtobool:
    """Testes para a função strtobool"""

    @pytest.mark.parametrize("value,expected", [
        ("y", True),
        ("yes", True),
        ("t", True),
        ("true", True),
        ("on", True),
        ("1", True),
        ("Y", True),
        ("YES", True),
        ("True", True),
        ("ON", True),
        ("TrUe", True),
    ])
    def test_true_values(self, value, expected):
        """
        Testa que valores verdadeiros são convertidos corretamente.

        Given: Uma string que representa um valor verdadeiro
        When: Chamamos strtobool
        Then: Retorna True
        """
        result = strtobool(value)
        assert result is expected
        assert isinstance(result, bool)

    @pytest.mark.parametrize("value,expected", [
        ("n", False),
        ("no", False),
        ("f", False),
        ("false", False),
        ("off", False),
        ("0", False),
        ("N", False),
        ("NO", False),
        ("False", False),
        ("OFF", False),
        ("FaLsE", False),
    ])
    def test_false_values(self, value, expected):
        """
        Testa que valores falsos são convertidos corretamente.

        Given: Uma string que representa um valor falso
        When: Chamamos strtobool
        Then: Retorna False
        """
        result = strtobool(value)
        assert result is expected
        assert isinstance(result, bool)

    def test_already_boolean_true(self):
        """
        Testa que valores booleanos True são retornados como estão.

        Given: Um valor booleano True
        When: Chamamos strtobool
        Then: Retorna True sem conversão
        """
        result = strtobool(True)
        assert result is True
        assert isinstance(result, bool)

    def test_already_boolean_false(self):
        """
        Testa que valores booleanos False são retornados como estão.

        Given: Um valor booleano False
        When: Chamamos strtobool
        Then: Retorna False sem conversão
        """
        result = strtobool(False)
        assert result is False
        assert isinstance(result, bool)

    @pytest.mark.parametrize("invalid_value", [
        "invalid",
        "2",
        "maybe",
        "sim",
        "nao",
        "",
        " ",
        "truee",
        "falsee",
        "yess",
        "noo",
    ])
    def test_invalid_values_raise_error(self, invalid_value):
        """
        Testa que valores inválidos lançam ValueError.

        Given: Uma string que não representa um valor booleano válido
        When: Chamamos strtobool
        Then: Lança ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            strtobool(invalid_value)

        assert "Invalid truth value" in str(exc_info.value)
        assert invalid_value.lower() in str(exc_info.value).lower()

    def test_whitespace_not_stripped(self):
        """
        Testa que espaços em branco causam erro.

        Given: Um valor válido com espaços em branco
        When: Chamamos strtobool
        Then: Lança ValueError (função não faz strip)
        """
        with pytest.raises(ValueError):
            strtobool(" yes ")

        with pytest.raises(ValueError):
            strtobool("yes ")

        with pytest.raises(ValueError):
            strtobool(" yes")

    def test_case_insensitive(self):
        """
        Testa que a conversão é case-insensitive.

        Given: Strings com diferentes combinações de maiúsculas/minúsculas
        When: Chamamos strtobool
        Then: Todas são convertidas corretamente
        """
        assert strtobool("YES") is True
        assert strtobool("Yes") is True
        assert strtobool("yEs") is True
        assert strtobool("NO") is False
        assert strtobool("No") is False
        assert strtobool("nO") is False

    def test_special_characters_raise_error(self):
        """
        Testa que strings com caracteres especiais lançam erro.

        Given: Strings com caracteres especiais
        When: Chamamos strtobool
        Then: Lança ValueError
        """
        with pytest.raises(ValueError):
            strtobool("yes!")

        with pytest.raises(ValueError):
            strtobool("t@rue")

        with pytest.raises(ValueError):
            strtobool("fal$e")

    def test_numeric_strings(self):
        """
        Testa conversão de strings numéricas.

        Given: Strings "1" e "0"
        When: Chamamos strtobool
        Then: "1" retorna True e "0" retorna False
        """
        assert strtobool("1") is True
        assert strtobool("0") is False

    def test_other_numeric_strings_raise_error(self):
        """
        Testa que outros números lançam erro.

        Given: Strings com outros números
        When: Chamamos strtobool
        Then: Lança ValueError
        """
        for num in ["2", "3", "-1", "10", "01", "00"]:
            with pytest.raises(ValueError):
                strtobool(num)

    def test_empty_string_raises_error(self):
        """
        Testa que string vazia lança erro.

        Given: Uma string vazia
        When: Chamamos strtobool
        Then: Lança ValueError
        """
        with pytest.raises(ValueError) as exc_info:
            strtobool("")

        assert "Invalid truth value" in str(exc_info.value)
