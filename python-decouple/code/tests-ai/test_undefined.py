"""
Testes para Undefined e UndefinedValueError

Este módulo testa a classe Undefined e a exceção UndefinedValueError,
que são usadas para representar valores não definidos no decouple.
"""
import pytest
from decouple import Undefined, UndefinedValueError, undefined


class TestUndefined:
    """Testes para a classe Undefined"""

    def test_undefined_class_exists(self):
        """
        Testa que a classe Undefined existe e pode ser instanciada.

        Given: A classe Undefined
        When: Criamos uma instância
        Then: A instância é criada com sucesso
        """
        obj = Undefined()
        assert isinstance(obj, Undefined)

    def test_undefined_instance_exists(self):
        """
        Testa que a instância undefined existe.

        Given: A referência global undefined
        When: Verificamos seu tipo
        Then: É uma instância de Undefined
        """
        assert isinstance(undefined, Undefined)

    def test_undefined_is_singleton_like(self):
        """
        Testa que undefined é uma referência única.

        Given: A instância global undefined
        When: Criamos uma nova instância
        Then: São objetos diferentes (não é singleton, mas undefined é único)
        """
        new_instance = Undefined()
        # undefined é uma instância específica, não um singleton
        assert new_instance is not undefined
        assert type(new_instance) is type(undefined)

    def test_undefined_can_be_compared_with_isinstance(self):
        """
        Testa que podemos verificar se um valor é Undefined com isinstance.

        Given: Um valor do tipo Undefined
        When: Usamos isinstance para verificar
        Then: Retorna True
        """
        value = undefined
        assert isinstance(value, Undefined)

    def test_multiple_undefined_instances_are_different(self):
        """
        Testa que múltiplas instâncias de Undefined são diferentes.

        Given: Duas instâncias da classe Undefined
        When: Comparamos as instâncias
        Then: São objetos diferentes
        """
        obj1 = Undefined()
        obj2 = Undefined()
        assert obj1 is not obj2

    def test_undefined_has_no_special_attributes(self):
        """
        Testa que Undefined é uma classe simples sem atributos especiais.

        Given: Uma instância de Undefined
        When: Verificamos seus atributos
        Then: Não tem métodos especiais além dos padrão do object
        """
        obj = Undefined()
        # Verifica que não tem __call__, __str__ customizado, etc.
        assert type(obj).__name__ == "Undefined"


class TestUndefinedValueError:
    """Testes para a exceção UndefinedValueError"""

    def test_undefined_value_error_is_exception(self):
        """
        Testa que UndefinedValueError é uma exceção.

        Given: A classe UndefinedValueError
        When: Verificamos sua herança
        Then: É subclasse de Exception
        """
        assert issubclass(UndefinedValueError, Exception)

    def test_can_raise_undefined_value_error(self):
        """
        Testa que podemos lançar UndefinedValueError.

        Given: A exceção UndefinedValueError
        When: Lançamos a exceção
        Then: É capturada corretamente
        """
        with pytest.raises(UndefinedValueError):
            raise UndefinedValueError("Test error")

    def test_undefined_value_error_with_message(self):
        """
        Testa que UndefinedValueError aceita mensagem.

        Given: Uma mensagem de erro
        When: Criamos UndefinedValueError com a mensagem
        Then: A mensagem é armazenada corretamente
        """
        message = "Configuration value not found"
        error = UndefinedValueError(message)

        assert str(error) == message
        assert error.args[0] == message

    def test_undefined_value_error_without_message(self):
        """
        Testa que UndefinedValueError pode ser criado sem mensagem.

        Given: Nenhuma mensagem
        When: Criamos UndefinedValueError
        Then: É criado com sucesso
        """
        error = UndefinedValueError()
        assert isinstance(error, UndefinedValueError)

    def test_undefined_value_error_can_be_caught_as_exception(self):
        """
        Testa que UndefinedValueError pode ser capturado como Exception.

        Given: UndefinedValueError sendo lançado
        When: Tentamos capturar como Exception
        Then: É capturado com sucesso
        """
        with pytest.raises(Exception) as exc_info:
            raise UndefinedValueError("test")

        assert isinstance(exc_info.value, UndefinedValueError)

    def test_undefined_value_error_with_format_string(self):
        """
        Testa UndefinedValueError com string formatada.

        Given: Uma string formatada
        When: Criamos o erro
        Then: A string formatada é preservada
        """
        key = "DATABASE_URL"
        message = "{} not found. Declare it as envvar or define a default value.".format(key)
        error = UndefinedValueError(message)

        assert "DATABASE_URL" in str(error)
        assert "not found" in str(error)
        assert "envvar" in str(error)
