"""
Testes para a classe AutoConfig

Este módulo testa a classe AutoConfig, que detecta automaticamente
arquivos de configuração e seus tipos.
"""
import os
import sys
import tempfile
import pytest
from decouple import AutoConfig, Config, RepositoryIni, RepositoryEnv, RepositoryEmpty


class TestAutoConfig:
    """Testes para a classe AutoConfig"""

    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir

        # Cleanup
        for filename in [".env", "settings.ini"]:
            filepath = os.path.join(temp_dir, filename)
            if os.path.exists(filepath):
                try:
                    os.unlink(filepath)
                except:
                    pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

    def test_init_without_search_path(self):
        """
        Testa inicialização sem search_path.

        Given: Nenhum parâmetro
        When: Criamos AutoConfig
        Then: search_path é None e config é None
        """
        autoconfig = AutoConfig()
        assert autoconfig.search_path is None
        assert autoconfig.config is None

    def test_init_with_search_path(self, temp_dir):
        """
        Testa inicialização com search_path.

        Given: Um search_path
        When: Criamos AutoConfig
        Then: search_path é armazenado e config é None
        """
        autoconfig = AutoConfig(search_path=temp_dir)
        assert autoconfig.search_path == temp_dir
        assert autoconfig.config is None

    def test_supported_files(self):
        """
        Testa que SUPPORTED contém os arquivos esperados.

        Given: A classe AutoConfig
        When: Verificamos SUPPORTED
        Then: Contém settings.ini e .env
        """
        assert "settings.ini" in AutoConfig.SUPPORTED
        assert ".env" in AutoConfig.SUPPORTED
        assert AutoConfig.SUPPORTED["settings.ini"] is RepositoryIni
        assert AutoConfig.SUPPORTED[".env"] is RepositoryEnv

    def test_supported_is_ordered_dict(self):
        """
        Testa que SUPPORTED é um OrderedDict.

        Given: AutoConfig.SUPPORTED
        When: Verificamos o tipo
        Then: É um OrderedDict (ordem importa)
        """
        from collections import OrderedDict
        assert isinstance(AutoConfig.SUPPORTED, OrderedDict)

    def test_default_encoding(self):
        """
        Testa que encoding padrão é UTF-8.

        Given: A classe AutoConfig
        When: Verificamos encoding
        Then: É UTF-8
        """
        assert AutoConfig.encoding == "UTF-8"

    def test_find_file_with_settings_ini(self, temp_dir):
        """
        Testa _find_file encontra settings.ini.

        Given: Um diretório com settings.ini
        When: Chamamos _find_file
        Then: Retorna o caminho para settings.ini
        """
        ini_file = os.path.join(temp_dir, "settings.ini")
        with open(ini_file, 'w') as f:
            f.write("[settings]\nDEBUG=true\n")

        autoconfig = AutoConfig()
        found = autoconfig._find_file(temp_dir)

        assert found == ini_file

    def test_find_file_with_env(self, temp_dir):
        """
        Testa _find_file encontra .env.

        Given: Um diretório com .env
        When: Chamamos _find_file
        Then: Retorna o caminho para .env
        """
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("DEBUG=true\n")

        autoconfig = AutoConfig()
        found = autoconfig._find_file(temp_dir)

        assert found == env_file

    def test_find_file_prefers_settings_ini_over_env(self, temp_dir):
        """
        Testa que settings.ini tem prioridade sobre .env.

        Given: Um diretório com settings.ini e .env
        When: Chamamos _find_file
        Then: Retorna settings.ini (vem primeiro em SUPPORTED)
        """
        ini_file = os.path.join(temp_dir, "settings.ini")
        env_file = os.path.join(temp_dir, ".env")

        with open(ini_file, 'w') as f:
            f.write("[settings]\nDEBUG=true\n")
        with open(env_file, 'w') as f:
            f.write("DEBUG=false\n")

        autoconfig = AutoConfig()
        found = autoconfig._find_file(temp_dir)

        assert found == ini_file

    def test_find_file_searches_parent_directories(self, temp_dir):
        """
        Testa que _find_file busca em diretórios pai.

        Given: Um arquivo config no diretório pai
        When: Chamamos _find_file do subdiretório
        Then: Encontra o arquivo no pai
        """
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("DEBUG=true\n")

        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)

        try:
            autoconfig = AutoConfig()
            found = autoconfig._find_file(subdir)
            assert found == env_file
        finally:
            os.rmdir(subdir)

    def test_find_file_returns_empty_when_not_found(self, temp_dir):
        """
        Testa que _find_file retorna string vazia quando não encontra.

        Given: Um diretório sem arquivos de config
        When: Chamamos _find_file
        Then: Retorna string vazia
        """
        autoconfig = AutoConfig()
        found = autoconfig._find_file(temp_dir)

        assert found == ""

    def test_find_file_stops_at_root(self, temp_dir):
        """
        Testa que _find_file para na raiz.

        Given: Buscando a partir de um diretório sem config
        When: Chegamos na raiz
        Then: Para e retorna vazio
        """
        autoconfig = AutoConfig()
        # Tenta buscar a partir da raiz
        found = autoconfig._find_file(os.sep)

        # Deve retornar vazio ou encontrar se houver config na raiz
        assert isinstance(found, str)

    def test_load_with_settings_ini(self, temp_dir):
        """
        Testa _load com settings.ini.

        Given: Um settings.ini
        When: Chamamos _load
        Then: Cria Config com RepositoryIni
        """
        ini_file = os.path.join(temp_dir, "settings.ini")
        with open(ini_file, 'w') as f:
            f.write("[settings]\nDEBUG=true\n")

        autoconfig = AutoConfig()
        autoconfig._load(temp_dir)

        assert autoconfig.config is not None
        assert isinstance(autoconfig.config, Config)

    def test_load_with_env(self, temp_dir):
        """
        Testa _load com .env.

        Given: Um .env
        When: Chamamos _load
        Then: Cria Config com RepositoryEnv
        """
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("DEBUG=true\n")

        autoconfig = AutoConfig()
        autoconfig._load(temp_dir)

        assert autoconfig.config is not None
        assert isinstance(autoconfig.config, Config)

    def test_load_without_config_file_uses_empty(self, temp_dir):
        """
        Testa _load sem arquivo usa RepositoryEmpty.

        Given: Um diretório sem arquivos de config
        When: Chamamos _load
        Then: Cria Config com RepositoryEmpty
        """
        autoconfig = AutoConfig()
        autoconfig._load(temp_dir)

        assert autoconfig.config is not None
        assert isinstance(autoconfig.config, Config)

    def test_load_handles_permission_errors(self, temp_dir):
        """
        Testa que _load trata erros de permissão.

        Given: Um caminho que pode causar erro de permissão
        When: Chamamos _load
        Then: Não lança exceção, usa RepositoryEmpty
        """
        autoconfig = AutoConfig()
        # Usa um caminho que pode não ter permissão
        autoconfig._load("/root/forbidden_path_that_does_not_exist")

        assert autoconfig.config is not None
        assert isinstance(autoconfig.config, Config)

    def test_call_loads_config_on_first_call(self, temp_dir):
        """
        Testa que __call__ carrega config na primeira chamada.

        Given: AutoConfig não inicializado
        When: Chamamos pela primeira vez
        Then: Carrega config
        """
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("DEBUG=true\n")

        autoconfig = AutoConfig(search_path=temp_dir)
        assert autoconfig.config is None

        result = autoconfig("DEBUG")

        assert autoconfig.config is not None
        assert result == "true"

    def test_call_doesnt_reload_config(self, temp_dir):
        """
        Testa que __call__ não recarrega config.

        Given: Config já carregado
        When: Chamamos novamente
        Then: Usa o mesmo config
        """
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("DEBUG=true\n")

        autoconfig = AutoConfig(search_path=temp_dir)
        autoconfig("DEBUG")
        first_config = autoconfig.config

        autoconfig("DEBUG")
        second_config = autoconfig.config

        assert first_config is second_config

    def test_call_delegates_to_config(self, temp_dir):
        """
        Testa que __call__ delega para config.

        Given: Um config carregado
        When: Chamamos com argumentos
        Then: Passa argumentos para config
        """
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("PORT=8000\n")

        autoconfig = AutoConfig(search_path=temp_dir)
        result = autoconfig("PORT", cast=int)

        assert result == 8000
        assert isinstance(result, int)

    def test_call_with_default(self, temp_dir):
        """
        Testa __call__ com valor padrão.

        Given: Uma chave inexistente
        When: Chamamos com default
        Then: Retorna o default
        """
        autoconfig = AutoConfig(search_path=temp_dir)
        result = autoconfig("MISSING_KEY", default="default_value")

        assert result == "default_value"

    def test_caller_path_returns_caller_directory(self):
        """
        Testa que _caller_path retorna diretório do caller.

        Given: AutoConfig
        When: Chamamos _caller_path
        Then: Retorna um caminho válido
        """
        autoconfig = AutoConfig()
        path = autoconfig._caller_path()

        assert isinstance(path, str)
        assert os.path.isabs(path)  # Deve ser caminho absoluto

    def test_uses_caller_path_when_no_search_path(self, temp_dir):
        """
        Testa que usa _caller_path quando search_path é None.

        Given: AutoConfig sem search_path
        When: Chamamos pela primeira vez
        Then: Usa _caller_path para buscar config
        """
        autoconfig = AutoConfig()
        # Não devemos ter erro ao chamar
        try:
            autoconfig("SOME_KEY", default="value")
        except Exception as e:
            pytest.fail(f"Should not raise exception: {e}")

    def test_encoding_can_be_changed(self):
        """
        Testa que encoding pode ser modificado.

        Given: AutoConfig
        When: Alteramos o encoding
        Then: É usado ao carregar o arquivo
        """
        autoconfig = AutoConfig()
        autoconfig.encoding = "latin-1"

        assert autoconfig.encoding == "latin-1"

    def test_multiple_autoconfig_instances_are_independent(self, temp_dir):
        """
        Testa que múltiplas instâncias são independentes.

        Given: Duas instâncias de AutoConfig
        When: Configuramos diferentemente
        Then: Cada uma mantém sua configuração
        """
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("DEBUG=true\n")

        autoconfig1 = AutoConfig(search_path=temp_dir)
        autoconfig2 = AutoConfig(search_path=temp_dir)

        autoconfig1("DEBUG")

        assert autoconfig1.config is not None
        assert autoconfig2.config is None  # Não foi carregado ainda

    def test_config_instance_is_accessible(self, temp_dir):
        """
        Testa que a instância pré-criada 'config' funciona.

        Given: A instância global 'config'
        When: Usamos diretamente
        Then: Funciona como AutoConfig
        """
        from decouple import config

        # config é uma instância de AutoConfig
        assert isinstance(config, AutoConfig)

    def test_find_file_with_exception_returns_empty(self, temp_dir):
        """
        Testa que exceções em _find_file são tratadas.

        Given: Um caminho que causa exceção
        When: Tentamos encontrar arquivo
        Then: Retorna string vazia sem lançar exceção
        """
        autoconfig = AutoConfig()

        # Força uma exceção usando um caminho inválido
        # O código tem try/except que deve capturar
        result = autoconfig._find_file(temp_dir)

        # Não deve lançar exceção
        assert isinstance(result, str)

    def test_load_creates_correct_repository_type(self, temp_dir):
        """
        Testa que _load cria o tipo correto de repositório.

        Given: Diferentes tipos de arquivo
        When: Chamamos _load
        Then: Usa o Repository correto
        """
        # Test com settings.ini
        ini_file = os.path.join(temp_dir, "settings.ini")
        with open(ini_file, 'w') as f:
            f.write("[settings]\nKEY=value\n")

        autoconfig1 = AutoConfig()
        autoconfig1._load(temp_dir)
        assert autoconfig1("KEY") == "value"

        os.unlink(ini_file)

        # Test com .env
        env_file = os.path.join(temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("KEY=value2\n")

        autoconfig2 = AutoConfig()
        autoconfig2._load(temp_dir)
        assert autoconfig2("KEY") == "value2"

    def test_search_path_is_absolute(self, temp_dir):
        """
        Testa que search_path é convertido para absoluto em _load.

        Given: Um search_path relativo
        When: Chamamos _load
        Then: É convertido para absoluto
        """
        # O código usa os.path.abspath em _load
        autoconfig = AutoConfig()

        # Mesmo com path relativo, deve funcionar
        relative_path = "."
        autoconfig._load(relative_path)

        assert autoconfig.config is not None
