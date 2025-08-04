# Otimizador de Estratégias de Pit Stop - Fórmula 1

## 📋 Descrição do Projeto

Este projeto implementa um sistema de otimização de estratégias de pit stop para corridas de Fórmula 1 usando algoritmos bio-inspirados. O sistema compara dois algoritmos principais:

1. **Algoritmo Genético (GA)** - Baseado na evolução natural
2. **Otimização por Colônia de Formigas (ACO)** - Baseado no comportamento de formigas

O objetivo é encontrar a estratégia de pit stop que minimize o tempo total da corrida, considerando fatores como degradação de pneus, efeito do combustível e tempo de pit stop.

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios
```
f1_optimizer/
├── main.py                 # Script principal de execução
├── optimize_and_analyze.py # Script de otimização e análise estatística
├── visualize_results.py    # Script de visualização básica
├── visualize_statistics.py # Script de visualização estatística
├── requirements.txt        # Dependências do projeto
├── README.md              # Documentação
├── data/
│   └── cache/            # Cache dos dados do FastF1
├── results/              # Resultados e visualizações
└── src/
    ├── __init__.py
    ├── data_handler.py    # Módulo de carregamento de dados
    ├── race_simulator.py  # Simulador de corrida
    ├── genetic_algorithm.py # Implementação do GA
    ├── ant_colony.py      # Implementação do ACO
    ├── parameter_optimizer.py # Otimizador de parâmetros
    └── statistical_analyzer.py # Analisador estatístico
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Conexão com internet (para download de dados)

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

1. **Execute o otimizador:**
```bash
python main.py
```

2. **Visualize os resultados:**
```bash
python visualize_results.py
```

### Otimização de Parâmetros e Análise Estatística

1. **Execute a otimização e análise estatística:**
```bash
python optimize_and_analyze.py
```

2. **Para teste rápido (menos execuções):**
```bash
python optimize_and_analyze.py --quick
```

3. **Visualize os resultados estatísticos:**
```bash
python visualize_statistics.py
```

### Configuração de Cenários

Para testar diferentes cenários, edite as variáveis no início do `main.py`:

```python
# Configuração do cenário de teste
year = 2024
race_name = "Spain Grand Prix"
driver_code = "HAM"  # Lewis Hamilton
```

### Parâmetros dos Algoritmos

#### Algoritmo Genético
- `population_size`: Tamanho da população (padrão: 50)
- `generations`: Número de gerações (padrão: 100)
- `mutation_rate`: Taxa de mutação (padrão: 0.1)
- `crossover_rate`: Taxa de crossover (padrão: 0.8)
- `elitism_size`: Número de melhores indivíduos para elitismo (padrão: 5)

#### Algoritmo ACO
- `num_ants`: Número de formigas (padrão: 30)
- `iterations`: Número de iterações (padrão: 50)
- `evaporation_rate`: Taxa de evaporação do feromônio (padrão: 0.1)
- `alpha`: Peso do feromônio (padrão: 1.0)
- `beta`: Peso da heurística (padrão: 2.0)

## 🔧 Módulos do Sistema

### 1. DataHandler (`src/data_handler.py`)

Responsável por carregar e processar dados das corridas de F1.

**Funcionalidades:**
- Carregamento de dados via FastF1
- Cache local para otimização
- Pré-processamento de dados (filtragem de voltas precisas)
- Conversão de tempos para segundos

**Métodos principais:**
- `get_race_data(year, race_name, driver_code)`: Carrega dados de uma corrida específica
- `get_available_compounds(race_data)`: Obtém compostos disponíveis
- `get_race_info(race_data)`: Retorna informações básicas da corrida

### 2. RaceSimulator (`src/race_simulator.py`)

Simulador de corrida que calcula tempos baseado em estratégias.

**Funcionalidades:**
- Calibração automática de parâmetros do modelo
- Simulação volta a volta
- Cálculo de tempo total para qualquer estratégia

**Modelo Matemático:**
```
Tempo_Volta = T_base + α_composto + (δ_degradacao × idade_pneu) - (δ_combustivel × volta_atual)
```

**Métodos principais:**
- `evaluate_strategy(strategy)`: Avalia uma estratégia completa
- `_calculate_model_parameters()`: Calibra parâmetros do modelo
- `get_model_parameters()`: Retorna parâmetros para análise

### 3. GeneticAlgorithm (`src/genetic_algorithm.py`)

Implementação do Algoritmo Genético.

**Características:**
- Representação: Lista de tuplas (volta_parada, composto_novo)
- Seleção: Torneio
- Crossover: Um ponto
- Mutação: Alteração de volta, composto, adição/remoção de parada
- Elitismo: Preserva melhores indivíduos

**Métodos principais:**
- `run()`: Executa o algoritmo
- `calculate_fitness(individual)`: Calcula fitness (inverso do tempo)
- `tournament_selection()`: Seleção por torneio
- `crossover()`: Crossover de um ponto
- `mutate()`: Aplica mutações

### 4. AntColonyOptimizer (`src/ant_colony.py`)

Implementação da Otimização por Colônia de Formigas.

**Características:**
- Modelagem como grafo de decisão
- Matriz de feromônios para cada volta/decisão
- Regra de transição probabilística
- Informação heurística baseada no simulador

**Métodos principais:**
- `run()`: Executa o algoritmo
- `build_solution()`: Constrói solução com uma formiga
- `_calculate_transition_probabilities()`: Calcula probabilidades
- `update_pheromones()`: Atualiza matriz de feromônios

## 📈 Análise de Resultados

### Métricas Comparadas

1. **Qualidade da Solução Final**
   - Tempo total da corrida
   - Estratégia encontrada (voltas de parada e compostos)

2. **Velocidade de Convergência**
   - Curvas de fitness por geração/iteração
   - Comparação de padrões de convergência

3. **Consistência**
   - Múltiplas execuções para análise estatística
   - Desvio padrão dos resultados

### Visualizações Geradas

- **Convergência**: Comparação das curvas de fitness
- **Estratégias**: Comparação das estratégias encontradas
- **Performance**: Métricas de tempo total e execução

## 🔬 Melhorias Implementadas

### Além da Metodologia Original

1. **Robustez de Dados**
   - Tratamento de dados insuficientes
   - Valores padrão para compostos não encontrados
   - Verificação de integridade dos dados

2. **Validação de Estratégias**
   - Penalização de estratégias inválidas
   - Verificação de uso de múltiplos compostos
   - Prevenção de voltas duplicadas

3. **Análise Avançada**
   - Script de visualização independente
   - Salvamento de resultados em JSON
   - Relatórios detalhados

4. **Flexibilidade**
   - Configuração fácil de cenários
   - Parâmetros ajustáveis
   - Suporte a diferentes corridas e pilotos

### Novas Funcionalidades (Otimização e Estatística)

5. **Otimização de Parâmetros**
   - Busca em grade para encontrar melhores parâmetros
   - Busca aleatória para exploração rápida
   - Otimização bayesiana (planejada)
   - Salvamento automático de parâmetros otimizados

6. **Análise Estatística Robusta**
   - Múltiplas execuções (30 por algoritmo)
   - Testes estatísticos (t-Student, Wilcoxon, Mann-Whitney)
   - Análise de tamanho do efeito (Cohen's d)
   - Testes de normalidade (Shapiro-Wilk)

7. **Visualizações Estatísticas**
   - Boxplots de distribuição
   - Histogramas de frequência
   - Gráficos de convergência
   - Análise de estratégias encontradas

8. **Relatórios Científicos**
   - Relatórios estatísticos detalhados
   - Recomendações baseadas em evidências
   - Métricas de qualidade e consistência
   - Documentação de metodologia estatística

## 📊 Exemplo de Saída

```
============================================================
OTIMIZADOR DE ESTRATÉGIAS DE PIT STOP - FÓRMULA 1
============================================================

Cenário de teste:
Ano: 2024
Corrida: Spain Grand Prix
Piloto: HAM
----------------------------------------

1. Carregando dados da corrida...
Dados carregados com sucesso!
Total de voltas: 78
Compostos utilizados: ['SOFT', 'MEDIUM', 'HARD']
Tempo médio de volta: 85.23s

2. Inicializando simulador de corrida...
Parâmetros do modelo:
  Tempo base (T_base): 82.45s
  Efeito combustível: 0.035s/volta
  Coeficientes de degradação: {'SOFT': 0.12, 'MEDIUM': 0.08, 'HARD': 0.05}
  Deltas de performance: {'SOFT': -2.1, 'MEDIUM': 0.0, 'HARD': 1.5}

3. Executando Algoritmo Genético...
----------------------------------------
Geração 0: Melhor fitness = 0.011234
Geração 10: Melhor fitness = 0.011456
...
Geração 90: Melhor fitness = 0.011789

Resultados do Algoritmo Genético:
  Melhor estratégia: [(25, 'MEDIUM'), (52, 'HARD')]
  Tempo total: 6654.32s
  Tempo de execução: 12.45s

4. Executando Algoritmo de Colônia de Formigas...
----------------------------------------
Iteração 0: Melhor tempo = 6689.45s
Iteração 10: Melhor tempo = 6667.23s
...
Iteração 40: Melhor tempo = 6651.78s

Resultados do Algoritmo ACO:
  Melhor estratégia: [(23, 'MEDIUM'), (50, 'HARD')]
  Tempo total: 6651.78s
  Tempo de execução: 8.92s

5. Análise Comparativa
========================================
Algoritmo Genético:
  Tempo total: 6654.32s
  Estratégia: [(25, 'MEDIUM'), (52, 'HARD')]
  Tempo de execução: 12.45s

Algoritmo ACO:
  Tempo total: 6651.78s
  Estratégia: [(23, 'MEDIUM'), (50, 'HARD')]
  Tempo de execução: 8.92s

🏆 MELHOR RESULTADO:
  Algoritmo: Algoritmo ACO
  Tempo total: 6651.78s
  Estratégia: [(23, 'MEDIUM'), (50, 'HARD')]

✅ Análise concluída! Resultados salvos em 'results/'
============================================================
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Erro ao carregar dados:**
   - Verifique a conexão com a internet
   - Confirme se o ano, corrida e piloto estão corretos
   - Verifique se o FastF1 está atualizado

2. **Dados insuficientes:**
   - O sistema usa valores padrão quando não há dados suficientes
   - Verifique se o piloto completou a corrida

3. **Tempo de execução alto:**
   - Reduza o número de gerações/iterações
   - Diminua o tamanho da população/número de formigas

## 📚 Referências

- FastF1 Documentation: https://docs.theoehrly.com/fastf1/
- Algoritmos Genéticos: Goldberg, D. E. (1989). Genetic algorithms in search, optimization, and machine learning.
- Otimização por Colônia de Formigas: Dorigo, M., & Stützle, T. (2004). Ant colony optimization.

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

**Desenvolvido com ❤️ para otimização de estratégias de F1** 