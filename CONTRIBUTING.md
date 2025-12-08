# Guia de Contribuição

Obrigado por considerar contribuir com este projeto! 🎉

## Como Contribuir

### 🐛 Reportar Bugs

Abra uma [issue](../../issues/new) descrevendo:
- **O problema** encontrado
- **Como reproduzir** (passos detalhados)
- **Ambiente**: Python version, OS, dependências instaladas
- **Comportamento esperado** vs. observado

### ✨ Adicionar Novas Comparações

Para adicionar um novo projeto à análise:

1. **Escolha um repositório Python** com:
   - Testes escritos antes de 2020 (pré-LLM)
   - ~500-2000 linhas de código
   - Domínio bem definido

2. **Prepare os dois cenários**:
   - Testes manuais (commit baseline histórico)
   - Testes gerados por IA (usando o prompt fornecido)

3. **Execute análise completa**:
```bash
   # Cobertura
   PYTHONPATH=src pytest tests/ --cov --cov-report=html
   
   # Mutation testing
   PYTHONPATH=src mutmut run
   mutmut results
```

4. **Documente os resultados**:
   - Adicione ao README
   - Atualize tabela comparativa
   - Inclua análise qualitativa

### 📚 Melhorar Documentação

Correções, clarificações e melhorias são sempre bem-vindas!

## 🔄 Processo de Contribuição

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/test-generation-comparison.git`
3. **Crie uma branch**: `git checkout -b feature/nome-descritivo`
4. **Faça suas alterações**
5. **Commit**: `git commit -m "feat: adiciona análise do projeto X"`
6. **Push**: `git push origin feature/nome-descritivo`
7. **Abra um Pull Request** com descrição clara das mudanças

### 📝 Convenção de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nova funcionalidade ou análise
- `fix:` correção de bug ou erro de análise
- `docs:` mudanças na documentação
- `refactor:` refatoração de código
- `test:` adicionar ou modificar testes
- `chore:` mudanças em scripts, build, etc.

**Exemplos**:
```
feat: adiciona análise do projeto requests
fix: corrige cálculo de mutation score
docs: atualiza README com resultados finais
```

## ✅ Checklist antes do PR

- [ ] Código segue os padrões do projeto
- [ ] Testes passam (se aplicável)
- [ ] Documentação atualizada
- [ ] Commits seguem convenções
- [ ] README atualizado com novos resultados

## 🤝 Código de Conduta

Ao participar deste projeto, você concorda em seguir nosso [Código de Conduta](CODE_OF_CONDUCT.md).

## 💬 Dúvidas?

Abra uma [issue](../../issues/new) com a tag `question` ou entre em contato.

---

Obrigado pela sua contribuição! 🚀