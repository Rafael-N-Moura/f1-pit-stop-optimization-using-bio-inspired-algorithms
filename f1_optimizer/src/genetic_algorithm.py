import random
import numpy as np
from typing import List, Tuple, Optional
from .race_simulator import RaceSimulator
import pandas as pd


class Individual:
    """
    Representa um indivíduo (estratégia) no algoritmo genético.
    """
    
    def __init__(self, chromosome: List[Tuple[int, str]], fitness: float = 0.0):
        """
        Inicializa um indivíduo.
        
        Args:
            chromosome: Lista de tuplas (volta_parada, composto_novo)
            fitness: Valor de fitness (inverso do tempo total)
        """
        self.chromosome = chromosome
        self.fitness = fitness
    
    def __str__(self):
        return f"Strategy: {self.chromosome}, Fitness: {self.fitness:.6f}"


class GeneticAlgorithm:
    """
    Implementação do Algoritmo Genético para otimização de estratégias de pit stop.
    """
    
    def __init__(self, simulator: RaceSimulator, 
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elitism_size: int = 5):
        """
        Inicializa o algoritmo genético.
        
        Args:
            simulator: Instância do simulador de corrida
            population_size: Tamanho da população
            generations: Número de gerações
            mutation_rate: Taxa de mutação
            crossover_rate: Taxa de crossover
            elitism_size: Número de melhores indivíduos para elitismo
        """
        self.simulator = simulator
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_size = elitism_size
        
        # Obter compostos disponíveis
        self.available_compounds = list(simulator.race_data['Compound'].unique())
        self.available_compounds = [c for c in self.available_compounds if pd.notna(c)]
        
        # Se não há compostos, usar padrão
        if not self.available_compounds:
            self.available_compounds = ['SOFT', 'MEDIUM', 'HARD']
        
        self.total_laps = simulator.total_laps
        self.best_individual = None
        self.fitness_history = []
    
    def create_initial_population(self) -> List[Individual]:
        """
        Cria a população inicial com estratégias aleatórias válidas.
        
        Returns:
            Lista de indivíduos
        """
        population = []
        
        for _ in range(self.population_size):
            chromosome = self._generate_random_strategy()
            individual = Individual(chromosome)
            population.append(individual)
        
        return population
    
    def _generate_random_strategy(self) -> List[Tuple[int, str]]:
        """
        Gera uma estratégia aleatória válida.
        
        Returns:
            Lista de tuplas (volta_parada, composto_novo)
        """
        strategy = []
        
        # Número de paradas (0 a 3)
        num_pits = random.randint(0, 3)
        
        if num_pits == 0:
            return strategy
        
        # Gerar paradas
        pit_laps = []
        for _ in range(num_pits):
            # Volta entre 5 e total_laps - 5
            lap = random.randint(5, max(6, self.total_laps - 5))
            pit_laps.append(lap)
        
        # Ordenar voltas de parada
        pit_laps.sort()
        
        # Gerar compostos para cada parada
        compounds_used = set()
        for lap in pit_laps:
            compound = random.choice(self.available_compounds)
            compounds_used.add(compound)
            strategy.append((lap, compound))
        
        # Garantir que pelo menos dois compostos diferentes são usados
        if len(compounds_used) < 2 and len(strategy) > 0:
            # Adicionar um composto diferente
            different_compound = random.choice([c for c in self.available_compounds if c not in compounds_used])
            if different_compound:
                strategy.append((random.randint(10, self.total_laps - 5), different_compound))
        
        return strategy
    
    def calculate_fitness(self, individual: Individual) -> float:
        """
        Calcula o fitness de um indivíduo.
        
        Args:
            individual: Indivíduo a ser avaliado
            
        Returns:
            Valor de fitness (inverso do tempo total)
        """
        try:
            total_time = self.simulator.evaluate_strategy(individual.chromosome)
            
            # Penalidade para estratégias inválidas
            penalty = 0.0
            
            # Verificar se usa pelo menos dois compostos diferentes
            compounds_used = set(compound for _, compound in individual.chromosome)
            initial_compound = self.simulator.race_data['Compound'].iloc[0]
            all_compounds_used = compounds_used | {initial_compound}
            
            # REGRA F1: Deve usar pelo menos dois compostos diferentes
            if len(all_compounds_used) < 2:
                penalty = 10000.0  # Penalidade muito alta para violar regra F1
            
            # Verificar se as voltas de parada são válidas
            pit_laps = [lap for lap, _ in individual.chromosome]
            if len(set(pit_laps)) != len(pit_laps):
                penalty = 500.0  # Penalidade para voltas duplicadas
            
            # Fitness é o inverso do tempo total (incluindo penalidades)
            fitness = 1.0 / (total_time + penalty)
            
            return fitness
            
        except Exception as e:
            print(f"Erro ao calcular fitness: {e}")
            return 0.0
    
    def tournament_selection(self, population: List[Individual], tournament_size: int = 3) -> Individual:
        """
        Seleção por torneio.
        
        Args:
            population: População atual
            tournament_size: Tamanho do torneio
            
        Returns:
            Indivíduo selecionado
        """
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Crossover de um ponto.
        
        Args:
            parent1: Primeiro pai
            parent2: Segundo pai
            
        Returns:
            Dois filhos
        """
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        # Crossover de um ponto
        if len(parent1.chromosome) == 0 or len(parent2.chromosome) == 0:
            return parent1, parent2
        
        # Escolher ponto de corte
        max_len = max(len(parent1.chromosome), len(parent2.chromosome))
        if max_len == 0:
            return parent1, parent2
        
        crossover_point = random.randint(0, max_len)
        
        # Criar filhos
        child1_chromosome = parent1.chromosome[:crossover_point] + parent2.chromosome[crossover_point:]
        child2_chromosome = parent2.chromosome[:crossover_point] + parent1.chromosome[crossover_point:]
        
        child1 = Individual(child1_chromosome)
        child2 = Individual(child2_chromosome)
        
        return child1, child2
    
    def mutate(self, individual: Individual):
        """
        Aplica mutação em um indivíduo.
        
        Args:
            individual: Indivíduo a ser mutado
        """
        if random.random() > self.mutation_rate:
            return
        
        mutation_type = random.choice(['change_lap', 'change_compound', 'add_pit', 'remove_pit'])
        
        if mutation_type == 'change_lap' and individual.chromosome:
            # Alterar volta de uma parada
            idx = random.randint(0, len(individual.chromosome) - 1)
            new_lap = random.randint(5, max(6, self.total_laps - 5))
            individual.chromosome[idx] = (new_lap, individual.chromosome[idx][1])
        
        elif mutation_type == 'change_compound' and individual.chromosome:
            # Alterar composto de uma parada
            idx = random.randint(0, len(individual.chromosome) - 1)
            new_compound = random.choice(self.available_compounds)
            individual.chromosome[idx] = (individual.chromosome[idx][0], new_compound)
        
        elif mutation_type == 'add_pit':
            # Adicionar uma parada
            new_lap = random.randint(5, max(6, self.total_laps - 5))
            new_compound = random.choice(self.available_compounds)
            individual.chromosome.append((new_lap, new_compound))
            individual.chromosome.sort(key=lambda x: x[0])
        
        elif mutation_type == 'remove_pit' and individual.chromosome:
            # Remover uma parada
            idx = random.randint(0, len(individual.chromosome) - 1)
            individual.chromosome.pop(idx)
    
    def run(self) -> Individual:
        """
        Executa o algoritmo genético.
        
        Returns:
            Melhor indivíduo encontrado
        """
        # Criar população inicial
        population = self.create_initial_population()
        
        # Calcular fitness inicial
        for individual in population:
            individual.fitness = self.calculate_fitness(individual)
        
        best_fitness = max(individual.fitness for individual in population)
        self.fitness_history.append(best_fitness)
        
        # Loop principal
        for generation in range(self.generations):
            # Ordenar população por fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Atualizar melhor indivíduo
            if self.best_individual is None or population[0].fitness > self.best_individual.fitness:
                self.best_individual = Individual(
                    population[0].chromosome.copy(),
                    population[0].fitness
                )
            
            # Aplicar elitismo
            new_population = population[:self.elitism_size].copy()
            
            # Preencher resto da população
            while len(new_population) < self.population_size:
                # Seleção
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)
                
                # Crossover
                child1, child2 = self.crossover(parent1, parent2)
                
                # Mutação
                self.mutate(child1)
                self.mutate(child2)
                
                # Calcular fitness dos filhos
                child1.fitness = self.calculate_fitness(child1)
                child2.fitness = self.calculate_fitness(child2)
                
                new_population.extend([child1, child2])
            
            # Manter apenas population_size indivíduos
            new_population = new_population[:self.population_size]
            population = new_population
            
            # Registrar melhor fitness da geração
            best_fitness = max(individual.fitness for individual in population)
            self.fitness_history.append(best_fitness)
            
            if generation % 10 == 0:
                print(f"Geração {generation}: Melhor fitness = {best_fitness:.6f}")
        
        return self.best_individual
    
    def get_fitness_history(self) -> List[float]:
        """
        Retorna o histórico de fitness para análise.
        
        Returns:
            Lista com melhor fitness de cada geração
        """
        return self.fitness_history 