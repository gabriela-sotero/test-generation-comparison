"""
Testes para o pacote itsdangerous

Este pacote contém testes unitários abrangentes para todas as funcionalidades
do itsdangerous, incluindo:

- exc: Testes de exceções personalizadas
- encoding: Testes de codificação/decodificação base64 e conversões
- compat: Testes de compatibilidade Python 2/3
- signer: Testes de assinatura criptográfica
- serializer: Testes de serialização com assinatura
- timed: Testes de assinaturas com timestamp
- jws: Testes de JSON Web Signature
- url_safe: Testes de serialização URL-safe com compressão

Para executar todos os testes:
    pytest tests/

Para executar testes de um módulo específico:
    pytest tests/test_signer.py

Para executar com cobertura:
    pytest --cov=itsdangerous --cov-report=html tests/
"""
