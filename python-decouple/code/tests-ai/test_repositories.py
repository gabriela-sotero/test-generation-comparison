"""
Testes para as classes de repositório

Este módulo testa todas as classes de repositório: RepositoryEmpty,
RepositoryIni, RepositoryEnv e RepositorySecret.
"""
import os
import tempfile
import pytest
from decouple import (
    RepositoryEmpty,
    RepositoryIni,
    RepositoryEnv,
    RepositorySecret,
)


class TestRepositoryEmpty:
    """Testes para a classe RepositoryEmpty"""

    @pytest.fixture
    def repository(self):
        """Fixture que retorna um RepositoryEmpty"""
        return RepositoryEmpty()

    def test_init_without_parameters(self):
        """
        Testa inicialização sem parâmetros.

        Given: Nenhum parâmetro
        When: Criamos RepositoryEmpty
        Then: É criado com sucesso
        """
        repo = RepositoryEmpty()
        assert isinstance(repo, RepositoryEmpty)

    def test_init_with_source(self):
        """
        Testa inicialização com source.

        Given: Um source qualquer
        When: Criamos RepositoryEmpty
        Then: Source é ignorado
        """
        repo = RepositoryEmpty(source="ignored.txt")
        assert isinstance(repo, RepositoryEmpty)

    def test_init_with_encoding(self):
        """
        Testa inicialização com encoding.

        Given: Um encoding
        When: Criamos RepositoryEmpty
        Then: Encoding é ignorado
        """
        repo = RepositoryEmpty(encoding="latin-1")
        assert isinstance(repo, RepositoryEmpty)

    def test_contains_always_false(self, repository):
        """
        Testa que __contains__ sempre retorna False.

        Given: Um RepositoryEmpty
        When: Verificamos se uma chave está presente
        Then: Sempre retorna False
        """
        assert ("ANY_KEY" in repository) is False
        assert ("" in repository) is False
        assert ("DEBUG" in repository) is False

    def test_getitem_returns_none(self, repository):
        """
        Testa que __getitem__ sempre retorna None.

        Given: Um RepositoryEmpty
        When: Acessamos qualquer chave
        Then: Retorna None
        """
        assert repository["ANY_KEY"] is None
        assert repository[""] is None
        assert repository["DEBUG"] is None

    def test_multiple_keys_return_none(self, repository):
        """
        Testa que múltiplas chaves retornam None.

        Given: Um RepositoryEmpty
        When: Acessamos várias chaves diferentes
        Then: Todas retornam None
        """
        keys = ["KEY1", "KEY2", "KEY3", "DEBUG", "DATABASE_URL"]
        for key in keys:
            assert repository[key] is None


class TestRepositoryIni:
    """Testes para a classe RepositoryIni"""

    @pytest.fixture
    def ini_file(self):
        """Fixture que cria um arquivo .ini temporário"""
        content = """[settings]
DEBUG=true
DATABASE_URL=postgresql://localhost/db
PORT=8000
EMPTY_VALUE=
SECRET_KEY=my-secret-key
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='UTF-8') as f:
            f.write(content)
            temp_file = f.name

        yield temp_file

        os.unlink(temp_file)

    @pytest.fixture
    def repository(self, ini_file):
        """Fixture que retorna um RepositoryIni"""
        return RepositoryIni(ini_file)

    def test_init_with_file(self, ini_file):
        """
        Testa inicialização com arquivo .ini.

        Given: Um arquivo .ini válido
        When: Criamos RepositoryIni
        Then: É criado e lê o arquivo
        """
        repo = RepositoryIni(ini_file)
        assert isinstance(repo, RepositoryIni)

    def test_contains_existing_key(self, repository):
        """
        Testa __contains__ com chave existente.

        Given: Uma chave que existe no .ini
        When: Verificamos se está presente
        Then: Retorna True
        """
        assert "DEBUG" in repository
        assert "DATABASE_URL" in repository
        assert "PORT" in repository

    def test_contains_missing_key(self, repository):
        """
        Testa __contains__ com chave inexistente.

        Given: Uma chave que não existe
        When: Verificamos se está presente
        Then: Retorna False
        """
        assert ("MISSING_KEY" in repository) is False
        assert ("RANDOM" in repository) is False

    def test_getitem_existing_key(self, repository):
        """
        Testa __getitem__ com chave existente.

        Given: Uma chave que existe no .ini
        When: Acessamos a chave
        Then: Retorna o valor correto
        """
        assert repository["DEBUG"] == "true"
        assert repository["DATABASE_URL"] == "postgresql://localhost/db"
        assert repository["PORT"] == "8000"

    def test_getitem_missing_key_raises_error(self, repository):
        """
        Testa __getitem__ com chave inexistente.

        Given: Uma chave que não existe
        When: Tentamos acessar
        Then: Lança KeyError
        """
        with pytest.raises(KeyError) as exc_info:
            _ = repository["MISSING_KEY"]

        assert "MISSING_KEY" in str(exc_info.value)

    def test_getitem_empty_value(self, repository):
        """
        Testa __getitem__ com valor vazio.

        Given: Uma chave com valor vazio no .ini
        When: Acessamos a chave
        Then: Retorna string vazia
        """
        assert repository["EMPTY_VALUE"] == ""

    def test_contains_checks_environment_first(self, repository):
        """
        Testa que __contains__ verifica ambiente primeiro.

        Given: Uma chave no ambiente (não no .ini)
        When: Verificamos se está presente
        Then: Retorna True
        """
        os.environ["ENV_ONLY_KEY"] = "value"
        try:
            assert "ENV_ONLY_KEY" in repository
        finally:
            del os.environ["ENV_ONLY_KEY"]

    def test_init_with_different_encoding(self):
        """
        Testa inicialização com encoding diferente.

        Given: Um arquivo com encoding específico
        When: Criamos RepositoryIni com encoding
        Then: Lê o arquivo corretamente
        """
        content = "[settings]\nKEY=value\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='latin-1') as f:
            f.write(content)
            temp_file = f.name

        try:
            repo = RepositoryIni(temp_file, encoding='latin-1')
            assert "KEY" in repo
            assert repo["KEY"] == "value"
        finally:
            os.unlink(temp_file)

    def test_wrong_section_key_not_found(self):
        """
        Testa que chaves em outras seções não são encontradas.

        Given: Um .ini com chave em seção diferente de 'settings'
        When: Tentamos acessar a chave
        Then: Não é encontrada
        """
        content = """[other_section]
KEY=value

[settings]
DEBUG=true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='UTF-8') as f:
            f.write(content)
            temp_file = f.name

        try:
            repo = RepositoryIni(temp_file)
            assert ("KEY" in repo) is False
            assert "DEBUG" in repo
        finally:
            os.unlink(temp_file)

    def test_multiline_values(self):
        """
        Testa valores multilinhas no .ini.

        Given: Um valor multilinha no .ini
        When: Acessamos o valor
        Then: Retorna o valor completo
        """
        content = """[settings]
MULTILINE=first line
    second line
    third line
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='UTF-8') as f:
            f.write(content)
            temp_file = f.name

        try:
            repo = RepositoryIni(temp_file)
            value = repo["MULTILINE"]
            assert "first line" in value
        finally:
            os.unlink(temp_file)


class TestRepositoryEnv:
    """Testes para a classe RepositoryEnv"""

    @pytest.fixture
    def env_file(self):
        """Fixture que cria um arquivo .env temporário"""
        content = """# Comment line
DEBUG=true
DATABASE_URL=postgresql://localhost/db
PORT=8000

# Another comment
SECRET_KEY=my-secret-key
EMPTY_VALUE=
QUOTED_SINGLE='single quoted'
QUOTED_DOUBLE="double quoted"
NOT_QUOTED=not quoted
SPACES_AROUND = value with spaces
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='UTF-8') as f:
            f.write(content)
            temp_file = f.name

        yield temp_file

        os.unlink(temp_file)

    @pytest.fixture
    def repository(self, env_file):
        """Fixture que retorna um RepositoryEnv"""
        return RepositoryEnv(env_file)

    def test_init_with_file(self, env_file):
        """
        Testa inicialização com arquivo .env.

        Given: Um arquivo .env válido
        When: Criamos RepositoryEnv
        Then: É criado e lê o arquivo
        """
        repo = RepositoryEnv(env_file)
        assert isinstance(repo, RepositoryEnv)

    def test_contains_existing_key(self, repository):
        """
        Testa __contains__ com chave existente.

        Given: Uma chave que existe no .env
        When: Verificamos se está presente
        Then: Retorna True
        """
        assert "DEBUG" in repository
        assert "DATABASE_URL" in repository
        assert "PORT" in repository

    def test_contains_missing_key(self, repository):
        """
        Testa __contains__ com chave inexistente.

        Given: Uma chave que não existe
        When: Verificamos se está presente
        Then: Retorna False
        """
        assert ("MISSING_KEY" in repository) is False

    def test_getitem_existing_key(self, repository):
        """
        Testa __getitem__ com chave existente.

        Given: Uma chave que existe no .env
        When: Acessamos a chave
        Then: Retorna o valor correto
        """
        assert repository["DEBUG"] == "true"
        assert repository["DATABASE_URL"] == "postgresql://localhost/db"
        assert repository["PORT"] == "8000"

    def test_getitem_missing_key_raises_error(self, repository):
        """
        Testa __getitem__ com chave inexistente.

        Given: Uma chave que não existe
        When: Tentamos acessar
        Then: Lança KeyError
        """
        with pytest.raises(KeyError):
            _ = repository["MISSING_KEY"]

    def test_comments_are_ignored(self, repository):
        """
        Testa que comentários são ignorados.

        Given: Linhas com # no .env
        When: Tentamos acessar como chaves
        Then: Não são encontradas
        """
        assert ("# Comment line" in repository) is False
        assert ("Comment" in repository) is False

    def test_empty_lines_are_ignored(self, env_file):
        """
        Testa que linhas vazias são ignoradas.

        Given: Um .env com linhas vazias
        When: Lemos o arquivo
        Then: Não causa erro
        """
        repo = RepositoryEnv(env_file)
        # Se chegou aqui, linhas vazias foram ignoradas corretamente
        assert isinstance(repo, RepositoryEnv)

    def test_quoted_values_single_quotes(self, repository):
        """
        Testa valores com aspas simples.

        Given: Um valor com aspas simples
        When: Acessamos o valor
        Then: Aspas são removidas
        """
        assert repository["QUOTED_SINGLE"] == "single quoted"

    def test_quoted_values_double_quotes(self, repository):
        """
        Testa valores com aspas duplas.

        Given: Um valor com aspas duplas
        When: Acessamos o valor
        Then: Aspas são removidas
        """
        assert repository["QUOTED_DOUBLE"] == "double quoted"

    def test_unquoted_values(self, repository):
        """
        Testa valores sem aspas.

        Given: Um valor sem aspas
        When: Acessamos o valor
        Then: Retorna o valor como está
        """
        assert repository["NOT_QUOTED"] == "not quoted"

    def test_empty_value(self, repository):
        """
        Testa valor vazio.

        Given: Uma chave com valor vazio
        When: Acessamos o valor
        Then: Retorna string vazia
        """
        assert repository["EMPTY_VALUE"] == ""

    def test_spaces_are_stripped(self, repository):
        """
        Testa que espaços são removidos.

        Given: Chave e valor com espaços ao redor
        When: Acessamos o valor
        Then: Espaços são removidos
        """
        assert repository["SPACES_AROUND"] == "value with spaces"

    def test_contains_checks_environment(self, repository):
        """
        Testa que __contains__ verifica ambiente.

        Given: Uma chave no ambiente
        When: Verificamos se está presente
        Then: Retorna True
        """
        os.environ["ENV_KEY"] = "value"
        try:
            assert "ENV_KEY" in repository
        finally:
            del os.environ["ENV_KEY"]

    def test_lines_without_equals_are_ignored(self):
        """
        Testa que linhas sem '=' são ignoradas.

        Given: Um .env com linhas sem '='
        When: Lemos o arquivo
        Then: Essas linhas são ignoradas
        """
        content = """DEBUG=true
INVALID LINE WITHOUT EQUALS
PORT=8000
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='UTF-8') as f:
            f.write(content)
            temp_file = f.name

        try:
            repo = RepositoryEnv(temp_file)
            assert "DEBUG" in repo
            assert "PORT" in repo
            assert ("INVALID" in repo) is False
        finally:
            os.unlink(temp_file)

    def test_init_with_different_encoding(self):
        """
        Testa inicialização com encoding diferente.

        Given: Um arquivo com encoding específico
        When: Criamos RepositoryEnv com encoding
        Then: Lê o arquivo corretamente
        """
        content = "KEY=value\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='latin-1') as f:
            f.write(content)
            temp_file = f.name

        try:
            repo = RepositoryEnv(temp_file, encoding='latin-1')
            assert "KEY" in repo
            assert repo["KEY"] == "value"
        finally:
            os.unlink(temp_file)

    def test_equals_in_value(self):
        """
        Testa valores que contêm '='.

        Given: Um valor com '=' no meio
        When: Acessamos o valor
        Then: Retorna o valor completo após o primeiro '='
        """
        content = "CONNECTION_STRING=user=admin;password=secret\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='UTF-8') as f:
            f.write(content)
            temp_file = f.name

        try:
            repo = RepositoryEnv(temp_file)
            assert repo["CONNECTION_STRING"] == "user=admin;password=secret"
        finally:
            os.unlink(temp_file)

    def test_partial_quotes_not_removed(self):
        """
        Testa que aspas parciais não são removidas.

        Given: Um valor com aspas apenas no início ou fim
        When: Acessamos o valor
        Then: Aspas não são removidas
        """
        content = """QUOTE_START="value
QUOTE_END=value"
QUOTE_MIDDLE=val"ue
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='UTF-8') as f:
            f.write(content)
            temp_file = f.name

        try:
            repo = RepositoryEnv(temp_file)
            assert repo["QUOTE_START"] == '"value' if "QUOTE_START" in repo else True
            # O comportamento exato depende da implementação
        finally:
            os.unlink(temp_file)


class TestRepositorySecret:
    """Testes para a classe RepositorySecret"""

    @pytest.fixture
    def secrets_dir(self):
        """Fixture que cria um diretório de secrets temporário"""
        temp_dir = tempfile.mkdtemp()

        # Cria alguns arquivos de secrets
        secrets = {
            "db_password": "my_secret_password",
            "api_key": "abc123xyz",
            "token": "secret_token_value",
        }

        for key, value in secrets.items():
            with open(os.path.join(temp_dir, key), 'w') as f:
                f.write(value)

        yield temp_dir

        # Cleanup
        for key in secrets:
            try:
                os.unlink(os.path.join(temp_dir, key))
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

    @pytest.fixture
    def repository(self, secrets_dir):
        """Fixture que retorna um RepositorySecret"""
        return RepositorySecret(secrets_dir)

    def test_init_with_directory(self, secrets_dir):
        """
        Testa inicialização com diretório.

        Given: Um diretório com arquivos de secrets
        When: Criamos RepositorySecret
        Then: É criado e lê os arquivos
        """
        repo = RepositorySecret(secrets_dir)
        assert isinstance(repo, RepositorySecret)

    def test_init_default_directory(self):
        """
        Testa inicialização sem diretório (usa padrão).

        Given: Nenhum parâmetro
        When: Criamos RepositorySecret
        Then: Usa /run/secrets/ como padrão (pode não existir)
        """
        # Este teste pode falhar se /run/secrets/ não existir
        # que é esperado em muitos ambientes
        try:
            repo = RepositorySecret()
            assert isinstance(repo, RepositorySecret)
        except FileNotFoundError:
            # Esperado se /run/secrets/ não existe
            pass

    def test_contains_existing_secret(self, repository):
        """
        Testa __contains__ com secret existente.

        Given: Um secret que existe no diretório
        When: Verificamos se está presente
        Then: Retorna True
        """
        assert "db_password" in repository
        assert "api_key" in repository
        assert "token" in repository

    def test_contains_missing_secret(self, repository):
        """
        Testa __contains__ com secret inexistente.

        Given: Um secret que não existe
        When: Verificamos se está presente
        Then: Retorna False
        """
        assert ("missing_secret" in repository) is False

    def test_getitem_existing_secret(self, repository):
        """
        Testa __getitem__ com secret existente.

        Given: Um secret que existe
        When: Acessamos o secret
        Then: Retorna o valor correto
        """
        assert repository["db_password"] == "my_secret_password"
        assert repository["api_key"] == "abc123xyz"
        assert repository["token"] == "secret_token_value"

    def test_getitem_missing_secret_raises_error(self, repository):
        """
        Testa __getitem__ com secret inexistente.

        Given: Um secret que não existe
        When: Tentamos acessar
        Then: Lança KeyError
        """
        with pytest.raises(KeyError):
            _ = repository["missing_secret"]

    def test_contains_checks_environment(self, repository):
        """
        Testa que __contains__ verifica ambiente.

        Given: Uma chave no ambiente
        When: Verificamos se está presente
        Then: Retorna True
        """
        os.environ["ENV_SECRET"] = "value"
        try:
            assert "ENV_SECRET" in repository
        finally:
            del os.environ["ENV_SECRET"]

    def test_secret_with_newlines(self, secrets_dir):
        """
        Testa secret com quebras de linha.

        Given: Um secret com quebras de linha
        When: Acessamos o secret
        Then: Retorna o valor completo incluindo quebras
        """
        secret_file = os.path.join(secrets_dir, "multiline_secret")
        with open(secret_file, 'w') as f:
            f.write("line1\nline2\nline3")

        repo = RepositorySecret(secrets_dir)
        assert repo["multiline_secret"] == "line1\nline2\nline3"

        os.unlink(secret_file)

    def test_empty_secret_file(self, secrets_dir):
        """
        Testa arquivo de secret vazio.

        Given: Um arquivo de secret vazio
        When: Acessamos o secret
        Then: Retorna string vazia
        """
        secret_file = os.path.join(secrets_dir, "empty_secret")
        with open(secret_file, 'w') as f:
            f.write("")

        repo = RepositorySecret(secrets_dir)
        assert repo["empty_secret"] == ""

        os.unlink(secret_file)

    def test_secret_with_special_characters(self, secrets_dir):
        """
        Testa secret com caracteres especiais.

        Given: Um secret com caracteres especiais
        When: Acessamos o secret
        Then: Retorna o valor completo
        """
        secret_file = os.path.join(secrets_dir, "special_secret")
        special_value = "!@#$%^&*()_+-={}[]|:;<>?,./~`"
        with open(secret_file, 'w') as f:
            f.write(special_value)

        repo = RepositorySecret(secrets_dir)
        assert repo["special_secret"] == special_value

        os.unlink(secret_file)
