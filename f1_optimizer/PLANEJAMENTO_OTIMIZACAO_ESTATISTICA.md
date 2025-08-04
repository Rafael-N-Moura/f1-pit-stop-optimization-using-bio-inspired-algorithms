# 🎯 Planejamento: Otimização de Parâmetros e Análise Estatística

## 📊 Objetivo
Otimizar os parâmetros dos algoritmos GA e ACO e realizar análise estatística robusta para determinar qual algoritmo é mais adequado para o problema de otimização de estratégias de pit stop em F1.

---

## 🔧 Fase 1: Otimização de Parâmetros

### 🎯 **Algoritmo Genético (GA)**

#### **Parâmetros Atuais**
```python
population_size = 50
generations = 100
mutation_rate = 0.1
crossover_rate = 0.8
elitism_size = 5
```

#### **Parâmetros a Otimizar**
1. **population_size**: [20, 30, 50, 75, 100]
2. **generations**: [50, 75, 100, 150, 200]
3. **mutation_rate**: [0.05, 0.1, 0.15, 0.2, 0.25]
4. **crossover_rate**: [0.6, 0.7, 0.8, 0.9, 0.95]
5. **elitism_size**: [2, 3, 5, 7, 10]

#### **Métricas de Avaliação**
- **Qualidade da solução**: Tempo total da melhor estratégia
- **Velocidade de convergência**: Geração onde melhor fitness é alcançado
- **Consistência**: Desvio padrão do tempo final
- **Tempo de execução**: Duração do algoritmo

### 🎯 **Algoritmo ACO**

#### **Parâmetros Atuais**
```python
num_ants = 30
iterations = 50
evaporation_rate = 0.1
alpha = 1.0  # Peso do feromônio
beta = 2.0   # Peso da heurística
```

#### **Parâmetros a Otimizar**
1. **num_ants**: [15, 25, 30, 40, 50]
2. **iterations**: [30, 50, 75, 100, 150]
3. **evaporation_rate**: [0.05, 0.1, 0.15, 0.2, 0.25]
4. **alpha**: [0.5, 1.0, 1.5, 2.0, 2.5]
5. **beta**: [1.0, 1.5, 2.0, 2.5, 3.0]

#### **Métricas de Avaliação**
- **Qualidade da solução**: Tempo total da melhor estratégia
- **Velocidade de convergência**: Iteração onde melhor tempo é alcançado
- **Consistência**: Desvio padrão do tempo final
- **Tempo de execução**: Duração do algoritmo

---

## 📈 Fase 2: Análise Estatística

### 🎯 **Design Experimental**

#### **Cenários de Teste**
1. **Spain 2024 - HAM** (cenário principal)
2. **Spain 2024 - VER** (comparação de pilotos)
3. **Spain 2024 - ALO** (outro piloto)
4. **Spain 2023 - HAM** (comparação temporal)
5. **Monaco 2024 - HAM** (circuito diferente)

#### **Configurações por Cenário**
- **Execuções por algoritmo**: 30 execuções
- **Sementes aleatórias**: Fixas para reprodutibilidade
- **Tempo limite**: Máximo 5 minutos por execução
- **Métricas coletadas**: Tempo final, estratégia, tempo de execução, convergência

### 🎯 **Métricas Estatísticas**

#### **Métricas de Qualidade**
1. **Tempo médio**: Média aritmética dos tempos finais
2. **Melhor tempo**: Menor tempo encontrado
3. **Desvio padrão**: Variabilidade dos resultados
4. **Coeficiente de variação**: CV = (desvio/média) × 100%

#### **Métricas de Performance**
1. **Tempo de execução médio**: Duração média do algoritmo
2. **Taxa de convergência**: % de execuções que convergiram
3. **Velocidade de convergência**: Geração/iteração média para convergência

#### **Métricas de Estratégia**
1. **Número médio de paradas**: Média de paradas por estratégia
2. **Variabilidade de estratégias**: Diversidade das soluções encontradas
3. **Consistência de compostos**: Frequência de uso de cada composto

### 🎯 **Testes Estatísticos**

#### **Teste t-Student**
- **Objetivo**: Comparar médias entre GA e ACO
- **Hipóteses**:
  - H0: μ_GA = μ_ACO
  - H1: μ_GA ≠ μ_ACO
- **Significância**: α = 0.05

#### **Teste de Wilcoxon**
- **Objetivo**: Comparar distribuições (não paramétrico)
- **Aplicação**: Quando dados não são normais
- **Vantagem**: Mais robusto que t-Student

#### **Análise de Variância (ANOVA)**
- **Objetivo**: Comparar múltiplos cenários
- **Aplicação**: Testar efeito do cenário nos resultados

---

## 🛠️ Implementação

### 📋 **Passo 1: Sistema de Otimização de Parâmetros**

#### **1.1 Criar Classe ParameterOptimizer**
```python
class ParameterOptimizer:
    def __init__(self, algorithm_type, base_params, param_ranges):
        self.algorithm_type = algorithm_type  # 'GA' ou 'ACO'
        self.base_params = base_params
        self.param_ranges = param_ranges
        self.results = []
    
    def grid_search(self, scenario):
        """Busca em grade para encontrar melhores parâmetros"""
        pass
    
    def random_search(self, scenario, n_trials=100):
        """Busca aleatória para exploração rápida"""
        pass
    
    def bayesian_optimization(self, scenario, n_trials=50):
        """Otimização bayesiana para eficiência"""
        pass
```

#### **1.2 Criar Classe StatisticalAnalyzer**
```python
class StatisticalAnalyzer:
    def __init__(self):
        self.results = {}
    
    def run_multiple_executions(self, algorithm, params, scenario, n_executions=30):
        """Executa algoritmo múltiplas vezes"""
        pass
    
    def calculate_statistics(self, results):
        """Calcula métricas estatísticas"""
        pass
    
    def perform_statistical_tests(self, ga_results, aco_results):
        """Realiza testes estatísticos"""
        pass
    
    def generate_report(self, results):
        """Gera relatório estatístico"""
        pass
```

### 📋 **Passo 2: Scripts de Execução**

#### **2.1 Script de Otimização**
```python
# optimize_parameters.py
def optimize_ga_parameters():
    """Otimiza parâmetros do GA"""
    pass

def optimize_aco_parameters():
    """Otimiza parâmetros do ACO"""
    pass

def compare_optimized_algorithms():
    """Compara algoritmos com parâmetros otimizados"""
    pass
```

#### **2.2 Script de Análise Estatística**
```python
# statistical_analysis.py
def run_statistical_study():
    """Executa estudo estatístico completo"""
    pass

def generate_statistical_report():
    """Gera relatório estatístico detalhado"""
    pass

def create_visualizations():
    """Cria visualizações estatísticas"""
    pass
```

---

## 📊 Cronograma de Implementação

### **Semana 1: Otimização de Parâmetros**
- **Dia 1-2**: Implementar ParameterOptimizer
- **Dia 3-4**: Otimizar parâmetros do GA
- **Dia 5**: Otimizar parâmetros do ACO

### **Semana 2: Análise Estatística**
- **Dia 1-2**: Implementar StatisticalAnalyzer
- **Dia 3-4**: Executar múltiplas execuções
- **Dia 5**: Realizar testes estatísticos

### **Semana 3: Relatórios e Visualizações**
- **Dia 1-2**: Gerar relatórios estatísticos
- **Dia 3-4**: Criar visualizações avançadas
- **Dia 5**: Documentar resultados

---

## 📈 Métricas de Sucesso

### **Otimização de Parâmetros**
- ✅ **Melhoria de 10%+** no tempo final
- ✅ **Redução de 20%+** no tempo de execução
- ✅ **Aumento de 15%+** na consistência

### **Análise Estatística**
- ✅ **Significância estatística** (p < 0.05)
- ✅ **Poder estatístico** > 0.8
- ✅ **Resultados reprodutíveis** (CV < 10%)

### **Comparação de Algoritmos**
- ✅ **Algoritmo vencedor** claramente identificado
- ✅ **Diferenças significativas** documentadas
- ✅ **Recomendações práticas** baseadas em evidências

---

## 🎯 Resultados Esperados

### **Relatórios Gerados**
1. **Relatório de Otimização**: Melhores parâmetros encontrados
2. **Relatório Estatístico**: Análise completa dos resultados
3. **Relatório Comparativo**: GA vs ACO com evidências
4. **Visualizações**: Gráficos e tabelas informativas

### **Arquivos de Configuração**
1. **best_ga_params.json**: Parâmetros otimizados do GA
2. **best_aco_params.json**: Parâmetros otimizados do ACO
3. **statistical_results.json**: Resultados estatísticos completos

### **Documentação**
1. **Metodologia Estatística**: Detalhes dos testes realizados
2. **Interpretação dos Resultados**: Análise dos achados
3. **Recomendações Práticas**: Orientações para uso

---

## 🔬 Validação e Verificação

### **Validação Interna**
- ✅ **Reprodutibilidade**: Mesmos resultados com mesmas sementes
- ✅ **Consistência**: Resultados similares em execuções múltiplas
- ✅ **Robustez**: Resultados estáveis em diferentes cenários

### **Validação Externa**
- ✅ **Comparação com literatura**: Resultados condizentes com estudos similares
- ✅ **Validação prática**: Estratégias encontradas são viáveis
- ✅ **Validação de especialistas**: Análise por conhecedores de F1

---

**Status**: 🚧 **Planejamento Criado - Pronto para Implementação** 