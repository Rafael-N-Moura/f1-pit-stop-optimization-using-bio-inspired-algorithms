# **Guia Técnico Detalhado para Implementação do Otimizador F1**

Este documento serve como um roteiro técnico para a implementação do backend do projeto. Ele descreve, em ordem de execução, as atividades e os detalhes técnicos necessários para construir a solução.

### **Passo 1: Configuração do Ambiente e Estrutura do Projeto**

**Objetivo:** Preparar a base de trabalho para que todos os módulos possam ser desenvolvidos de forma organizada.  
**Atividades:**

1. **Criar a Estrutura de Pastas:** Organize o projeto conforme a estrutura abaixo para separar as responsabilidades:  
   f1\_optimizer/  
   │  
   ├── main.py  
   ├── requirements.txt  
   │  
   ├── data/  
   │   └── cache/  
   │  
   └── src/  
       ├── \_\_init\_\_.py  
       ├── data\_handler.py  
       ├── race\_simulator.py  
       ├── genetic\_algorithm.py  
       └── ant\_colony.py

2. **Configurar o Ambiente Virtual:**  
   * Execute python \-m venv venv para criar o ambiente.  
   * Ative-o com source venv/bin/activate (Linux/macOS) ou venv\\Scripts\\activate (Windows).  
3. **Instalar Dependências:**  
   * Crie o arquivo requirements.txt com as bibliotecas: fastf1, pandas, numpy, matplotlib, seaborn, scikit-learn.  
   * Instale todas com o comando pip install \-r requirements.txt.

### **Passo 2: Implementação do Módulo data\_handler.py**

**Objetivo:** Criar um componente responsável por buscar e preparar os dados de uma corrida para serem utilizados pelo simulador.  
**Atividades:**

1. **Criar a Classe DataHandler:**  
   * No arquivo src/data\_handler.py, defina a classe DataHandler.  
   * No construtor (\_\_init\_\_), inicialize o cache do FastF1 para que os dados das corridas sejam salvos localmente, acelerando execuções futuras.  
2. **Implementar o Método get\_race\_data:**  
   * Este método deve receber como parâmetros year, race\_name e driver\_code.  
   * **Lógica Interna:**  
     1. Utilize fastf1.get\_session() para carregar os dados da sessão da corrida.  
     2. Use o método .load() para baixar os dados.  
     3. Filtre os dados para o piloto específico usando .pick\_driver().  
     4. Realize o pré-processamento essencial no DataFrame do Pandas resultante:  
        * Converta a coluna LapTime para segundos para facilitar cálculos numéricos.  
        * Filtre as voltas para manter apenas aquelas que são "precisas" (usando a coluna booleana IsAccurate do FastF1), removendo assim voltas de entrada/saída dos boxes e aquelas sob Safety Car.  
   * **Retorno:** O método deve retornar o DataFrame do Pandas limpo e processado.

### **Passo 3: Implementação do Módulo race\_simulator.py**

**Objetivo:** Desenvolver o coração do projeto: um simulador que calcula o tempo total de uma corrida para qualquer estratégia fornecida, com parâmetros calibrados a partir de dados reais.  
**Atividades:**

1. **Criar a Classe RaceSimulator:**  
   * No arquivo src/race\_simulator.py, defina a classe RaceSimulator.  
   * O construtor (\_\_init\_\_) deve receber o race\_data (DataFrame gerado pelo DataHandler) e o pit\_stop\_time. Ele deve armazenar esses valores e chamar um método interno, \_calculate\_model\_parameters, para calibrar o simulador.  
2. **Implementar o Método \_calculate\_model\_parameters:**  
   * Este método privado será responsável por estimar os coeficientes da fórmula de tempo de volta.  
   * **Lógica Interna para Estimação dos Parâmetros:**  
     1. **Efeito do Combustível (fuel\_effect\_coeff):** Defina este coeficiente como um valor fixo e padrão da indústria, por exemplo, 0.035 segundos de ganho por volta. Este valor será usado para normalizar os tempos de volta antes de calcular os outros parâmetros. Para cada volta n, o tempo corrigido para o combustível é: Tempo\_Corrigido \= LapTimeSeconds \+ (fuel\_effect\_coeff \* n).  
     2. **Degradação do Pneu (degradation\_coeffs):**  
        * Crie um dicionário para armazenar os coeficientes de degradação para cada composto.  
        * Para cada composto de pneu (e.g., 'MEDIUM', 'HARD') presente nos dados:  
          * Isole os stints (períodos de uso contínuo) daquele composto.  
          * Para cada stint, use sklearn.linear\_model.LinearRegression para ajustar uma reta onde a variável independente (X) é a idade do pneu (TyreLife) e a variável dependente (y) é o Tempo\_Corrigido para o combustível.  
          * O coeficiente angular (model.coef\_) da regressão é a penalidade de degradação em segundos por volta para aquele composto. Armazene este valor no dicionário.  
     3. **Delta de Performance do Composto (alpha\_coeffs):**  
        * Defina um composto como referência (baseline), por exemplo, o pneu DURO, com alpha\_duro \= 0\.  
        * Para os outros compostos, o delta de performance será a diferença entre os interceptos (model.intercept\_) da regressão linear calculada no passo anterior. Por exemplo: alpha\_medio \= intercepto\_duro \- intercepto\_medio. Isso representa a diferença de tempo base entre os pneus, já removidos os efeitos de combustível e degradação.  
     4. **Tempo de Volta Base (T\_base):** O T\_base será o intercepto do composto de referência. Por exemplo, T\_base \= intercepto\_duro.  
3. **Implementar o Método evaluate\_strategy:**  
   * Este método deve receber uma strategy (lista de tuplas (volta, composto)).  
   * **Lógica Interna:**  
     1. Inicialize as variáveis de estado: total\_time \= 0, current\_lap \= 1, current\_tyre\_compound, current\_tyre\_age.  
     2. Itere sobre os stints definidos pela estratégia. Para cada stint:  
     3. Simule volta a volta, calculando o tempo de cada volta com a fórmula completa:  
        lap\_time \= T\_base \+ alpha\_coeffs\[pneu\] \+ (degradation\_coeffs\[pneu\] \* idade\_pneu) \- (fuel\_effect\_coeff \* volta\_atual)  
     4. Some o lap\_time ao total\_time.  
     5. Ao final de cada stint (exceto o último), adicione o pit\_stop\_time ao total\_time e atualize o estado do pneu (novo composto, idade zerada).  
   * **Retorno:** O método deve retornar o total\_time final.

### **Passo 4: Implementação dos Algoritmos (genetic\_algorithm.py e ant\_colony.py)**

**Objetivo:** Desenvolver as duas lógicas de otimização que utilizarão o simulador.

#### **4.1 Algoritmo Genético (GA)**

1. **Modelagem do Problema:** O problema é modelado como a busca pela melhor "estratégia" (indivíduo) em uma população. Uma estratégia é representada diretamente como um cromossomo.  
2. **Implementar a Classe GeneticAlgorithm:**  
   * O construtor receberá uma instância do RaceSimulator e os hiperparâmetros: population\_size, generations, mutation\_rate, crossover\_rate, elitism\_size.  
3. **Definir a Estrutura do Indivíduo:**  
   * **Cromossomo:** Uma lista de tuplas (volta\_parada, composto\_novo). O comprimento da lista é variável, permitindo que o GA explore diferentes números de paradas.  
   * **Fitness:** O valor de fitness de um indivíduo será 1 / tempo\_total\_corrida, onde o tempo é calculado pelo simulator.evaluate\_strategy(). Uma penalidade será aplicada a estratégias inválidas (e.g., que não usam dois compostos diferentes).  
4. **Implementar os Mecanismos do GA:**  
   * **População Inicial:** Crie um método que gera population\_size indivíduos com estratégias aleatórias, mas válidas.  
   * **Seleção:** Implemente a **Seleção por Torneio**. Um método que seleciona k (e.g., k=3) indivíduos aleatoriamente e retorna o de melhor fitness.  
   * **Recombinação (Crossover):** Implemente o **Crossover de Um Ponto**. Um método que recebe dois cromossomos pais, seleciona um ponto de corte aleatório e troca as "caudas" das listas para criar dois filhos.  
   * **Mutação:** Implemente um método que aplica, com baixa probabilidade (mutation\_rate), uma das seguintes operações a um cromossomo: (1) alterar a volta de uma parada; (2) alterar o composto de uma parada; (3) adicionar ou remover uma parada.  
5. **Implementar o Ciclo Principal (run):**  
   * Crie a população inicial.  
   * Inicie um loop que executa por generations vezes.  
   * Em cada geração:  
     1. Calcule o fitness de todos os indivíduos.  
     2. Aplique **Elitismo**, copiando os elitism\_size melhores indivíduos para a nova população.  
     3. Preencha o resto da nova população aplicando Seleção, Crossover e Mutação.  
   * Retorne a melhor estratégia encontrada durante todo o processo.

#### **4.2 Otimização por Colônia de Formigas (ACO)**

1. **Modelagem do Problema:** O problema é modelado como um **Grafo de Decisão Direcionado**.  
   * **Nós:** Cada volta da corrida, de 1 a N.  
   * **Arestas:** De cada nó/volta i, existem arestas que levam ao nó i+1. Cada aresta representa uma decisão possível: "continuar com o pneu atual" ou "parar para trocar pelo composto X". O objetivo é encontrar o caminho de menor custo (tempo) do nó 1 ao N.  
2. **Implementar a Classe AntColonyOptimizer:**  
   * O construtor receberá uma instância do RaceSimulator e os hiperparâmetros: num\_ants, iterations, evaporation\_rate, alpha (peso do feromônio), beta (peso da heurística).  
3. **Definir as Estruturas de Dados do ACO:**  
   * **Matriz de Feromônios (τ):** Uma matriz NumPy onde T\[i\]\[j\] armazena a intensidade do feromônio na volta i para a decisão j.  
4. **Implementar os Mecanismos do ACO:**  
   * **Construção da Solução (Caminho da Formiga):** Crie um método onde uma "formiga" constrói uma estratégia completa, movendo-se de volta em volta.  
   * **Regra de Transição Probabilística:** Em cada volta i, a formiga escolhe a próxima decisão j com uma probabilidade baseada na fórmula: P(i,j) \= (τ(i,j)^α \* η(i,j)^β) / Σ(τ(i,k)^α \* η(i,k)^β).  
   * **Informação Heurística (η):** Esta é a "atratividade" de uma decisão. Implemente uma função que calcula o inverso do tempo da *próxima* volta para cada decisão possível. A decisão que leva a um tempo de volta menor é heuristicamente melhor.  
   * **Atualização de Feromônios:** Crie um método que, após todas as formigas completarem seus caminhos:  
     1. **Evaporação:** Reduz todos os valores de feromônio por um fator (1 \- evaporation\_rate).  
     2. **Depósito:** As melhores formigas depositam feromônio nas arestas (decisões) que utilizaram. A quantidade depositada é inversamente proporcional ao tempo total da corrida (calculado pelo simulator.evaluate\_strategy()).  
5. **Implementar o Ciclo Principal (run):**  
   * Inicialize a matriz de feromônios.  
   * Inicie um loop que executa por iterations vezes.  
   * Em cada iteração:  
     1. Faça com que todas as num\_ants construam suas soluções.  
     2. Avalie todas as soluções com o simulador.  
     3. Atualize a matriz de feromônios.  
   * Retorne a melhor estratégia encontrada durante todo o processo.

### **Passo 5: Orquestração e Execução (main.py)**

**Objetivo:** Criar o script que une todos os módulos e executa o fluxo completo do projeto.  
**Atividades:**

1. **Definir o Cenário de Teste:** No topo do arquivo, defina as variáveis para o cenário a ser analisado (ano, nome da corrida, piloto).  
2. **Instanciar os Módulos:**  
   * Crie uma instância do DataHandler.  
   * Chame get\_race\_data para obter os dados do cenário.  
   * Crie uma instância do RaceSimulator com os dados obtidos.  
3. **Executar os Otimizadores:**  
   * Crie uma instância do GeneticAlgorithm e chame seu método run. Imprima os resultados.  
   * Crie uma instância do AntColonyOptimizer e chame seu método run. Imprima os resultados.  
4. **Análise (Futuro):** Adicione seções para salvar os resultados em arquivos e chamar scripts de visualização para análise comparativa.