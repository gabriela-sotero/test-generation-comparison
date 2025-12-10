# Requests — Comparação de Testes: IA vs Manuais

Este diretório contém uma análise comparativa entre a suíte de **testes manuais originais**
do projeto **Requests (snapshot de 2019)** e um conjunto de **testes gerados por IA**, com foco em
**cobertura**, **abrangência estrutural**, **profundidade semântica** e **robustez**.

---

## 📊 Resultados Resumidos

| Métrica             | Testes Manuais | Testes IA   | Diferença     |
| ------------------- | -------------- | ----------- | ------------- |
| Total de Testes     | 559            | 72          | −487 (−87%)   |
| Cobertura de Código | 25%            | 45%         | **+20 pp**    |
| Linhas de Código    | ~6.200         | ~1.900      | −4.300 (−70%) |
| Arquivos de Teste   | 1 diretório    | 15 arquivos | +14           |
| Taxa de Aprovação   | 100%           | 100%*       | 0             |

* A suíte IA apresentou 1 falha inicial (persistência de cookies).
Após correção semântica, **todos os testes passaram**.

---

## 📁 Estrutura do Diretório

```text
requests/
├── requests/                  # Código-fonte do Requests
│
├── tests-manual/              # Testes manuais oficiais (559 testes)
│   ├── test_requests.py
│   ├── test_models.py
│   ├── test_sessions.py
│   ├── ...
│
├── tests/                     # Testes gerados por IA
│   ├── test_api.py
│   ├── test_models.py
│   ├── test_cookies.py
│   ├── test_internal_utils.py
│   ├── test_integration.py
│   ├── ... (15 arquivos)
│
├── manual_coverage.html       # Relatório de cobertura (manuais)
├── ai_coverage.html           # Relatório de cobertura (IA)
│
├── comparison_analysis.txt    # Análise comparativa detalhada
└── README.md
```

---

## 🎯 Principais Descobertas

### Cobertura de Código

Os **testes manuais** fornecem uma validação profunda do comportamento real do Requests,
focando em integração, regressões históricas, sessão HTTP, adapters e modelos internos.

Os **testes gerados por IA** atingem **45% de cobertura**, contra **25%** dos manuais,
principalmente porque:

* testam módulos pequenos ignorados pelos mantenedores
* geram testes unitários rasos, porém amplos
* cobrem helpers internos e estruturas
* executam caminhos triviais porém numerosos

**Conclusão:**
A IA atinge **maior cobertura estrutural**, mas **não compreende** nuances do Requests.

---

## 🧪 Abordagens de Teste

### ✅ Testes Manuais

* Testam fluxo HTTP completo
* Alta profundidade semântica
* Abrangem regressões históricas
* Capturam comportamento real das sessões
* Exercitam adapters, hooks, cookies e edge cases reais

**Desvantagens**

* Baixa cobertura por linha de código
* Pouca granularidade unitária
* Estrutura monolítica e difícil de manter

---

### ✅ Testes Gerados por IA

* Modularizados (**15 arquivos**)
* Testes pequenos e concisos
* Exploram muitos módulos ignorados
* Cobertura surpreendentemente alta (45%)
* Estrutura clara e moderna

**Limitações**

* Entendimento superficial da API
* Só um teste integrativo real
* Uma falha semântica inicial (cookies)
* Testes assumem comportamentos inexistentes
* Não testam fluxo real HTTP

---

## 🔍 Cobertura Exclusiva

### Apenas nos Testes Manuais

* Adapters e conexões
* Persistência real de cookies
* Sessões completas
* Comportamento de redirecionamento
* Cenários históricos do Requests
* Fluxos reais de fallback de transportes

### Apenas nos Testes IA

* Compatibilidade interna (compat.py)
* Estruturas auxiliares
* Exceptions (100%)
* status_codes.py (100%)
* helpers nunca testados oficialmente
* Módulos triviais com alta quantidade de linhas

---

## 📈 Distribuição dos Testes

### Testes Manuais (559)

* Estrutura monolítica
* Altíssima profundidade
* ênfase em comportamento e integração
* poucos arquivos, muitos testes grandes

### Testes IA (72)

* 15 arquivos
* Testes curtos, organizados e modulares
* Cobertura sistemática de módulos pequenos
* Abordagem clara por componente

---

## 🏆 Vencedores por Categoria

| Categoria                    | Vencedor               |
| ---------------------------- | ---------------------- |
| Cobertura de Código          | ⚡ IA                   |
| Robustez Semântica           | 👤 Manual              |
| Profundidade Funcional       | 👤 Manual              |
| Organização e Modularidade   | ⚡ IA                   |
| Precisão Comportamental      | 👤 Manual              |
| Eficiência (Cobertura/Teste) | ⚡ IA                   |
| Viabilidade de IA            | ⚡ IA (mas com cautela) |

---

## 💡 Recomendações

### Abordagem Híbrida Ideal

* **Manter** os testes manuais como núcleo do projeto
* **Adicionar** testes IA para:

  * edge cases de módulos auxiliares
  * documentação de comportamento
  * validação estrutural
* Não usar IA para substituir testes integrais
* Evitar assumir comportamentos (como cookies automáticos)

📌 **Meta realista:**
Manuais + **30–60 testes IA** bem direcionados → 55–65% de cobertura sólida.

---

## 📝 Conclusão

Diferentemente de bibliotecas mais simples como python-decouple, o Requests apresenta
interações complexas com a camada de transporte HTTP e dependência profunda entre
seus módulos centrais.

Os testes manuais capturam essa complexidade com precisão, enquanto a IA fornece
apenas uma camada superficial — porém estatisticamente abrangente.

### Resultado Final

* **IA vence em cobertura estrutural**
* **Manual vence em precisão semântica e confiabilidade**
* **A combinação das duas abordagens é a estratégia superior**