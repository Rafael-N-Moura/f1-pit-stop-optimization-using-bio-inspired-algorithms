# Otimizador de Estratégias de Pit Stop - Fórmula 1

## 📋 Descrição do Projeto

Este projeto implementa um sistema avançado de otimização de estratégias de pit stop para corridas de Fórmula 1 usando algoritmos bio-inspirados. O sistema compara dois algoritmos principais com análise estatística robusta:

1. **Algoritmo Genético (GA)** - Baseado na evolução natural
2. **Otimização por Colônia de Formigas (ACO)** - Baseado no comportamento de formigas

O objetivo é encontrar a estratégia de pit stop que minimize o tempo total da corrida, considerando fatores como degradação de pneus, efeito do combustível, tempo de pit stop e **regras oficiais da F1**.

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios
```
f1_optimizer/
├── main.py                 # Script principal de execução básica
├── optimize_and_analyze.py # Script de otimização e análise estatística robusta
├── test_multiple_drivers.py # Script de teste com múltiplos pilotos
├── visualize_results.py    # Script de visualização básica
├── visualize_statistics.py # Script de visualização estatística avançada
├── requirements.txt        # Dependências do projeto
├── README.md              # Documentação
├── RELATORIO_FINAL_PROJETO.md # Relatório completo do projeto
├── RESUMO_EXECUTIVO.md    # Resumo executivo
├── data/
│   └── cache/            # Cache dos dados do FastF1
├── results/              # Resultados e visualizações
└── src/
    ├── __init__.py
    ├── data_handler.py    # Módulo de carregamento e processamento de dados
    ├── race_simulator.py  # Simulador de corrida com validação F1
    ├── genetic_algorithm.py # Implementação do GA com regras F1
    ├── ant_colony.py      # Implementação do ACO com grafo de decisão
    ├── parameter_optimizer.py # Otimizador sistemático de parâmetros
    └── statistical_analyzer.py # Analisador estatístico robusto
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Conexão com internet (para download de dados via FastF1)
- 4GB+ RAM (para análise estatística robusta)

### Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd f1_optimizer
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

## 📊 Como Usar

### Execução Básica

1. **Execute o otimizador básico:**
```bash
python main.py
```

2. **Visualize os resultados básicos:**
```bash
python visualize_results.py
```

### Otimização de Parâmetros e Análise Estatística Robusta

1. **Execute a otimização completa e análise estatística:**
```bash
python optimize_and_analyze.py
```
*Tempo estimado: 5-8 horas para análise completa*

2. **Para teste rápido (menos execuções):**
```bash
python optimize_and_analyze.py --quick
```

3. **Visualize os resultados estatísticos avançados:**
```bash
python visualize_statistics.py
```

### Teste com Múltiplos Pilotos

```bash
python test_multiple_drivers.py
```

### Configuração de Cenários

Para testar diferentes cenários, edite as variáveis nos scripts:

```python
# Configuração do cenário de teste (padrão)
year = 2024
race_name = "Spain Grand Prix"
driver_code = "HAM"  # Lewis Hamilton
```

## 🔧 Módulos do Sistema

### 1. DataHandler (`src/data_handler.py`)

Responsável por carregar e processar dados das corridas de F1 via FastF1 API.

**Funcionalidades:**
- Carregamento de dados via FastF1 com cache local
- Pré-processamento avançado (filtragem de voltas precisas)
- Correção para efeito do combustível
- Conversão de tempos para segundos
- Validação de integridade dos dados

**Dados Coletados da API:**
- **LapTime**: Tempo de cada volta
- **LapNumber**: Número da volta
- **Compound**: Composto do pneu (SOFT, MEDIUM, HARD, INTERMEDIATE)
- **TyreLife**: Idade do pneu em voltas
- **IsAccurate**: Flag indicando se a volta é precisa
- **DriverCode**: Código do piloto

**Métodos principais:**
- `get_race_data(year, race_name, driver_code)`: Carrega dados de uma corrida específica
- `get_available_compounds(race_data)`: Obtém compostos disponíveis
- `get_race_info(race_data)`: Retorna informações básicas da corrida

### 2. RaceSimulator (`src/race_simulator.py`)

Simulador de corrida com calibração automática e validação de regras F1.

**Funcionalidades:**
- Calibração automática de parâmetros via regressão linear
- Simulação volta a volta com modelo matemático
- Validação de regras F1 (uso de pelo menos 2 compostos)
- Correção automática de parâmetros irrealistas
- Penalização de estratégias inválidas

**Modelo Matemático:**
```
Tempo_Volta = T_base + α_composto + (δ_degradacao × idade_pneu) - (δ_combustivel × volta_atual)
```

**Validações F1 Implementadas:**
- Uso obrigatório de pelo menos 2 compostos diferentes
- Limite realista de 3 pit stops
- Penalização severa para estratégias inválidas

**Métodos principais:**
- `evaluate_strategy(strategy)`: Avalia uma estratégia completa
- `_calculate_model_parameters()`: Calibra parâmetros via ML
- `_validate_and_correct_parameters()`: Corrige parâmetros irrealistas
- `get_model_parameters()`: Retorna parâmetros para análise

### 3. GeneticAlgorithm (`src/genetic_algorithm.py`)

Implementação do Algoritmo Genético com validação de regras F1.

**Características:**
- Representação: Lista de tuplas (volta_parada, composto_novo)
- Seleção: Torneio
- Crossover: Um ponto
- Mutação: Alteração de volta, composto, adição/remoção de parada
- Elitismo: Preserva melhores indivíduos
- **Validação F1**: Penalização severa para violação da regra dos 2 compostos

**Métodos principais:**
- `run()`: Executa o algoritmo
- `calculate_fitness(individual)`: Calcula fitness com validação F1
- `tournament_selection()`: Seleção por torneio
- `crossover()`: Crossover de um ponto
- `mutate()`: Aplica mutações

### 4. AntColonyOptimizer (`src/ant_colony.py`)

Implementação da Otimização por Colônia de Formigas com grafo de decisão.

**Características:**
- **Modelagem como grafo de decisão**: Cada volta é um nó com decisões possíveis
- **Matriz de feromônios**: Para cada volta/decisão
- **Regra de transição probabilística**: Normalizada para garantir probabilidades válidas
- **Informação heurística**: Baseada no simulador de corrida
- **Validação F1**: Força uso de pelo menos 2 compostos
- **Limite realista**: Máximo 3 pit stops

**Representação do Problema:**
```
Grafo de Decisão:
Volta 1: [CONTINUE, SOFT, MEDIUM, HARD] → Probabilidades baseadas em feromônio + heurística
Volta 2: [CONTINUE, SOFT, MEDIUM, HARD] → Probabilidades atualizadas
...
Volta N: [CONTINUE, SOFT, MEDIUM, HARD] → Probabilidades finais
```

**Métodos principais:**
- `run()`: Executa o algoritmo
- `build_solution()`: Constrói solução com uma formiga
- `_calculate_transition_probabilities()`: Calcula probabilidades normalizadas
- `update_pheromones()`: Atualiza matriz de feromônios
- `_calculate_heuristic()`: Calcula informação heurística

### 5. ParameterOptimizer (`src/parameter_optimizer.py`)

Sistema de otimização sistemática de hiperparâmetros dos algoritmos.

**Funcionalidades:**
- **Grid Search**: Busca sistemática em grade de parâmetros
- **Random Search**: Busca aleatória para exploração rápida
- **Avaliação robusta**: Múltiplas execuções por configuração
- **Salvamento automático**: Parâmetros otimizados em JSON

**Parâmetros Otimizados:**

**GA:**
- `population_size`: [30, 50, 70, 100]
- `generations`: [50, 100, 150, 200]
- `mutation_rate`: [0.05, 0.1, 0.15, 0.2]
- `crossover_rate`: [0.6, 0.8, 0.9, 1.0]
- `elitism_size`: [2, 5, 10]

**ACO:**
- `num_ants`: [20, 30, 50, 70]
- `iterations`: [30, 50, 70, 100]
- `evaporation_rate`: [0.05, 0.1, 0.15, 0.2]
- `alpha`: [0.5, 1.0, 1.5, 2.0]
- `beta`: [1.0, 2.0, 3.0, 4.0]

### 6. StatisticalAnalyzer (`src/statistical_analyzer.py`)

Sistema de análise estatística robusta para comparação científica dos algoritmos.

**Funcionalidades:**
- **Múltiplas execuções**: 30 execuções por algoritmo (configurável)
- **Testes estatísticos completos**:
  - **Shapiro-Wilk**: Teste de normalidade
  - **t-Student**: Teste paramétrico para comparação de médias
  - **Wilcoxon**: Teste não-paramétrico para dados pareados
  - **Mann-Whitney U**: Teste não-paramétrico para dados independentes
- **Análise de tamanho do efeito**: Cohen's d
- **Métricas avançadas**: CV, quartis, estatísticas descritivas

**Métricas Coletadas:**
- Tempo total da corrida
- Tempo de execução do algoritmo
- Número de pit stops
- Variabilidade da estratégia
- Taxa de convergência
- Consistência dos resultados

## 📈 Análise de Resultados

### Métricas Comparadas

1. **Qualidade da Solução Final**
   - Tempo total da corrida
   - Estratégia encontrada (voltas de parada e compostos)
   - Validação de regras F1

2. **Performance Estatística**
   - Média, desvio padrão, coeficiente de variação
   - Quartis e valores extremos
   - Testes de significância estatística
   - Tamanho do efeito (Cohen's d)

3. **Velocidade de Convergência**
   - Curvas de fitness por geração/iteração
   - Taxa de convergência
   - Estabilidade dos resultados

4. **Consistência e Robustez**
   - Variabilidade entre execuções
   - Confiabilidade dos resultados
   - Análise de outliers

### Visualizações Geradas

**Básicas:**
- Convergência: Comparação das curvas de fitness
- Estratégias: Comparação das estratégias encontradas
- Performance: Métricas de tempo total e execução

**Estatísticas Avançadas:**
- Boxplots de distribuição de tempos
- Histogramas de frequência
- Gráficos de convergência comparativos
- Análise de estratégias encontradas
- Visualização de testes estatísticos
- Gráficos de tamanho do efeito

## 🔬 Funcionalidades Avançadas Implementadas

### 1. Coleta e Processamento de Dados Avançado

**Dados da FastF1 API:**
- Coleta automática de dados reais de corridas
- Processamento com correção para efeito do combustível
- Filtragem de voltas imprecisas (Safety Car, entrada/saída dos boxes)
- Calibração automática de parâmetros via regressão linear

**Modelo Matemático Calibrado:**
```python
# Regressão linear por composto
X = compound_data['TyreLife'].values  # Idade do pneu
y = compound_data['CorrectedTime'].values  # Tempo corrigido
model = LinearRegression()
model.fit(X, y)
degradation_coeff = model.coef_[0]  # δ_degradation
```

### 2. Validação de Regras F1

**Regras Implementadas:**
- **Uso obrigatório de pelo menos 2 compostos**: Penalização severa (50000s)
- **Limite realista de pit stops**: Máximo 3 paradas
- **Validação de estratégias vazias**: Retorna infinito para estratégias sem paradas

**Implementação:**
```python
# Verificação de compostos únicos
total_compounds = len(set(strategy_compounds) | {initial_compound})
if total_compounds < 2:
    penalty += 50000.0  # Penalização severa
```

### 3. Otimização Sistemática de Parâmetros

**Grid Search Completo:**
- 3125 combinações de parâmetros para cada algoritmo
- Avaliação com múltiplas execuções por configuração
- Salvamento automático dos melhores parâmetros

**Exemplo de Parâmetros Otimizados (HAM, Spain 2024):**
```python
# GA Otimizado
{
    "population_size": 70,
    "generations": 150,
    "mutation_rate": 0.15,
    "crossover_rate": 0.9,
    "elitism_size": 5
}

# ACO Otimizado
{
    "num_ants": 50,
    "iterations": 70,
    "evaporation_rate": 0.1,
    "alpha": 1.5,
    "beta": 2.0
}
```

### 4. Análise Estatística Robusta

**Testes Implementados:**
- **Shapiro-Wilk**: Verifica normalidade dos dados
- **t-Student**: Compara médias (quando dados são normais)
- **Wilcoxon**: Teste não-paramétrico robusto
- **Mann-Whitney U**: Comparação independente
- **Cohen's d**: Mede tamanho do efeito

**Resultados Típicos (HAM, Spain 2024):**
```python
# ACO vs GA
ACO_mean = 4858.76s, CV = 0.001%
GA_mean = 4859.44s, CV = 0.034%
Cohen's_d = 0.582 (efeito médio)
p_value = 0.023 (significativo)
```

### 5. Representação Avançada do ACO

**Grafo de Decisão:**
- Cada volta é um nó com decisões possíveis
- Feromônios guiam a exploração
- Heurística considera custo de pit stop
- Normalização garante probabilidades válidas

**Regra de Transição:**
```python
P(decision) = (τ^α × η^β) / Σ(τ^α × η^β)
# Normalização garante ΣP = 1
```

### 6. Visualizações Científicas

**Gráficos Gerados:**
- Boxplots comparativos de performance
- Histogramas de distribuição de tempos
- Curvas de convergência
- Análise de estratégias encontradas
- Visualização de testes estatísticos
- Gráficos de tamanho do efeito

## 📊 Exemplo de Saída Completa

```
============================================================
OTIMIZADOR DE ESTRATÉGIAS DE PIT STOP - FÓRMULA 1
============================================================

Cenário de teste:
Ano: 2024
Corrida: Spain Grand Prix
Piloto: HAM (Lewis Hamilton)
Composto inicial: MEDIUM
----------------------------------------

1. Carregando dados da corrida...
Dados carregados com sucesso!
Total de voltas: 66
Compostos utilizados: ['SOFT', 'MEDIUM', 'HARD']
Tempo médio de volta: 85.23s

2. Inicializando simulador de corrida...
Parâmetros do modelo (calibrados via ML):
  Tempo base (T_base): 82.45s
  Efeito combustível: 0.035s/volta
  Coeficientes de degradação: {'SOFT': 0.12, 'MEDIUM': 0.08, 'HARD': 0.05}
  Deltas de performance: {'SOFT': -2.1, 'MEDIUM': 0.0, 'HARD': 1.5}

3. Executando Algoritmo Genético (parâmetros otimizados)...
----------------------------------------
Geração 0: Melhor fitness = 0.011234
Geração 10: Melhor fitness = 0.011456
...
Geração 150: Melhor fitness = 0.011789

Resultados do Algoritmo Genético:
  Melhor estratégia: [(25, 'MEDIUM'), (52, 'HARD')]
  Tempo total: 4859.44s
  Tempo de execução: 12.45s
  Validação F1: ✅ 2 compostos utilizados

4. Executando Algoritmo de Colônia de Formigas (parâmetros otimizados)...
----------------------------------------
Iteração 0: Melhor tempo = 4865.45s
Iteração 10: Melhor tempo = 4862.23s
...
Iteração 70: Melhor tempo = 4858.76s

Resultados do Algoritmo ACO:
  Melhor estratégia: [(23, 'MEDIUM'), (50, 'HARD')]
  Tempo total: 4858.76s
  Tempo de execução: 8.92s
  Validação F1: ✅ 2 compostos utilizados

5. Análise Estatística Robusta
========================================
Execuções: 30 por algoritmo
Testes realizados: Shapiro-Wilk, t-Student, Wilcoxon, Mann-Whitney U

Resultados Estatísticos:
  ACO - Média: 4858.76s, CV: 0.001%, Desvio: 0.05s
  GA  - Média: 4859.44s, CV: 0.034%, Desvio: 1.65s
  
Testes de Significância:
  t-Student: p = 0.023 (significativo)
  Wilcoxon: p = 0.018 (significativo)
  Mann-Whitney U: p = 0.021 (significativo)
  
Tamanho do Efeito:
  Cohen's d = 0.582 (efeito médio)

🏆 RECOMENDAÇÃO FINAL:
  Algoritmo: ACO (Otimização por Colônia de Formigas)
  Justificativa: Superioridade estatística significativa, maior consistência (CV menor)
  Parâmetros otimizados: num_ants=50, iterations=70, alpha=1.5, beta=2.0

✅ Análise concluída! Resultados salvos em 'results/'
============================================================
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Erro ao carregar dados:**
   - Verifique a conexão com a internet
   - Confirme se o ano, corrida e piloto estão corretos
   - Verifique se o FastF1 está atualizado
   - Limpe o cache: `rm -rf data/cache/*`

2. **Dados insuficientes:**
   - O sistema usa valores padrão quando não há dados suficientes
   - Verifique se o piloto completou a corrida
   - Tente outro piloto ou corrida

3. **Tempo de execução alto:**
   - Use `--quick` para análise rápida
   - Reduza o número de execuções no `statistical_analyzer.py`
   - Diminua os parâmetros de otimização

4. **Erro de memória:**
   - Reduza o número de execuções simultâneas
   - Use análise rápida com `--quick`
   - Feche outros programas durante a execução

5. **Resultados inconsistentes:**
   - Execute múltiplas vezes para verificar consistência
   - Verifique se os dados da corrida são adequados
   - Use análise estatística robusta

## 📚 Referências e Documentação

### Documentação do Projeto
- **RELATORIO_FINAL_PROJETO.md**: Relatório completo com metodologia e resultados
- **RESUMO_EXECUTIVO.md**: Resumo executivo do projeto
- **PLANEJAMENTO_OTIMIZACAO_ESTATISTICA.md**: Planejamento da otimização

### Bibliotecas Utilizadas
- **FastF1**: Coleta de dados oficiais da F1
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica
- **Matplotlib/Seaborn**: Visualizações
- **Scikit-learn**: Machine Learning (regressão linear)
- **SciPy**: Testes estatísticos

### Referências Científicas
- **Algoritmos Genéticos**: Goldberg, D. E. (1989). Genetic algorithms in search, optimization, and machine learning.
- **Otimização por Colônia de Formigas**: Dorigo, M., & Stützle, T. (2004). Ant colony optimization.
- **Análise Estatística**: Cohen, J. (1988). Statistical power analysis for the behavioral sciences.

## 🤝 Contribuições

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Adicione testes se necessário
5. Submeta um pull request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---
