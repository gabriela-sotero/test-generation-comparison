"""
Configuração global do pytest para os testes do itsdangerous

Este arquivo contém fixtures e configurações compartilhadas entre todos os testes.
"""
import pytest


@pytest.fixture(autouse=False)
def reset_time():
    """
    Fixture para garantir que testes com tempo não interfiram entre si.

    Esta fixture não faz nada por padrão, mas pode ser expandida se necessário.
    """
    yield


# Configurações do pytest
def pytest_configure(config):
    """
    Configuração customizada do pytest.

    Adiciona markers customizados para categorização de testes.
    """
    config.addinivalue_line(
        "markers", "slow: marca testes que são lentos para executar"
    )
    config.addinivalue_line(
        "markers", "security: marca testes relacionados a segurança"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
