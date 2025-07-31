import random
import numpy as np
from typing import List, Tuple, Dict, Optional
from .race_simulator import RaceSimulator
import pandas as pd


class Ant:
    """
    Representa uma formiga no algoritmo ACO.
    """
    
    def __init__(self):
        """
        Inicializa uma formiga.
        """
        self.strategy = []
        self.total_time = float('inf')
    
    def __str__(self):
        return f"Strategy: {self.strategy}, Time: {self.total_time:.2f}s"


class AntColonyOptimizer:
    """
    Implementação da Otimização por Colônia de Formigas para estratégias de pit stop.
    """
    
    def __init__(self, simulator: RaceSimulator,
                 num_ants: int = 30,
                 iterations: int = 50,
                 evaporation_rate: float = 0.1,
                 alpha: float = 1.0,  # Peso do feromônio
                 beta: float = 2.0):  # Peso da heurística
        """
        Inicializa o otimizador ACO.
        
        Args:
            simulator: Instância do simulador de corrida
            num_ants: Número de formigas
            iterations: Número de iterações
            evaporation_rate: Taxa de evaporação do feromônio
            alpha: Peso do feromônio na regra de transição
            beta: Peso da heurística na regra de transição
        """
        self.simulator = simulator
        self.num_ants = num_ants
        self.iterations = iterations
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        
        # Obter compostos disponíveis
        self.available_compounds = list(simulator.race_data['Compound'].unique())
        self.available_compounds = [c for c in self.available_compounds if pd.notna(c)]
        
        # Se não há compostos, usar padrão
        if not self.available_compounds:
            self.available_compounds = ['SOFT', 'MEDIUM', 'HARD']
        
        self.total_laps = simulator.total_laps
        
        # Definir decisões possíveis
        self.decisions = ['CONTINUE'] + self.available_compounds
        self.num_decisions = len(self.decisions)
        
        # Inicializar matriz de feromônios com bias para estratégias realistas
        self.pheromone_matrix = np.ones((self.total_laps, self.num_decisions)) * 0.1
        
        # Bias para CONTINUE (menos paradas) - estratégias mais realistas
        self.pheromone_matrix[:, 0] = 1.0  # CONTINUE tem mais feromônio inicial
        
        # Melhor solução encontrada
        self.best_ant = None
        self.best_time = float('inf')
        self.fitness_history = []
    
    def build_solution(self) -> Ant:
        """
        Constrói uma solução (estratégia) usando uma formiga.
        
        Returns:
            Formiga com estratégia construída
        """
        ant = Ant()
        current_lap = 1
        current_compound = self.simulator.race_data['Compound'].iloc[0]
        current_tyre_age = 0
        pit_stops_count = 0
        max_pit_stops = 3  # Limite realista de paradas
        
        while current_lap <= self.total_laps:
            # Verificar se ainda pode parar
            if pit_stops_count >= max_pit_stops:
                decision = 'CONTINUE'
            else:
                # Calcular probabilidades para cada decisão
                probabilities = self._calculate_transition_probabilities(
                    current_lap, current_compound, current_tyre_age
                )
                
                # Escolher decisão baseada em probabilidades
                decision_idx = self._choose_decision(probabilities)
                decision = self.decisions[decision_idx]
            
            if decision == 'CONTINUE':
                # Continuar com o pneu atual
                current_lap += 1
                current_tyre_age += 1
            else:
                # Parar para trocar pneu
                ant.strategy.append((current_lap, decision))
                current_compound = decision
                current_tyre_age = 0
                current_lap += 1
                pit_stops_count += 1
        
        # Avaliar estratégia
        ant.total_time = self.simulator.evaluate_strategy(ant.strategy)
        
        return ant
    
    def _calculate_transition_probabilities(self, lap: int, current_compound: str, tyre_age: int) -> np.ndarray:
        """
        Calcula as probabilidades de transição para cada decisão.
        
        Args:
            lap: Volta atual
            current_compound: Composto atual
            tyre_age: Idade do pneu atual
            
        Returns:
            Array com probabilidades para cada decisão
        """
        probabilities = np.zeros(self.num_decisions)
        
        for i, decision in enumerate(self.decisions):
            # Feromônio
            pheromone = self.pheromone_matrix[lap - 1, i]
            
            # Heurística (inverso do tempo da próxima volta)
            heuristic = self._calculate_heuristic(lap, decision, current_compound, tyre_age)
            
            # Regra de transição
            probabilities[i] = (pheromone ** self.alpha) * (heuristic ** self.beta)
        
        # Normalizar probabilidades
        total = np.sum(probabilities)
        if total > 0:
            probabilities = probabilities / total
        else:
            # Se todas as probabilidades são zero, usar distribuição uniforme
            probabilities = np.ones(self.num_decisions) / self.num_decisions
        
        return probabilities
    
    def _calculate_heuristic(self, lap: int, decision: str, current_compound: str, tyre_age: int) -> float:
        """
        Calcula a heurística para uma decisão.
        
        Args:
            lap: Volta atual
            decision: Decisão a ser avaliada
            current_compound: Composto atual
            tyre_age: Idade do pneu atual
            
        Returns:
            Valor heurístico (inverso do tempo da próxima volta)
        """
        try:
            if decision == 'CONTINUE':
                # Continuar com pneu atual
                next_lap_time = self.simulator._calculate_lap_time(
                    lap + 1, current_compound, tyre_age + 1
                )
                heuristic = 1.0 / max(next_lap_time, 60.0)
            else:
                # Trocar para novo composto - considerar custo do pit stop
                next_lap_time = self.simulator._calculate_lap_time(
                    lap + 1, decision, 0
                )
                pit_stop_cost = self.simulator.pit_stop_time
                
                # Heurística considera custo total (pit stop + tempo)
                total_cost = next_lap_time + pit_stop_cost
                heuristic = 1.0 / max(total_cost, 60.0)
            
            return heuristic
            
        except Exception:
            return 0.1  # Valor padrão em caso de erro
    
    def _choose_decision(self, probabilities: np.ndarray) -> int:
        """
        Escolhe uma decisão baseada nas probabilidades.
        
        Args:
            probabilities: Array com probabilidades
            
        Returns:
            Índice da decisão escolhida
        """
        return np.random.choice(len(probabilities), p=probabilities)
    
    def update_pheromones(self, ants: List[Ant]):
        """
        Atualiza a matriz de feromônios.
        
        Args:
            ants: Lista de formigas da iteração atual
        """
        # Evaporação
        self.pheromone_matrix *= (1 - self.evaporation_rate)
        
        # Depósito de feromônio
        for ant in ants:
            if ant.total_time < float('inf'):
                # Quantidade de feromônio é inversamente proporcional ao tempo
                pheromone_amount = 1.0 / ant.total_time
                
                # Depositar feromônio nas decisões tomadas
                for lap, compound in ant.strategy:
                    if 1 <= lap <= self.total_laps:
                        decision_idx = self.decisions.index(compound)
                        self.pheromone_matrix[lap - 1, decision_idx] += pheromone_amount
    
    def run(self) -> Ant:
        """
        Executa o algoritmo ACO.
        
        Returns:
            Melhor formiga encontrada
        """
        for iteration in range(self.iterations):
            # Construir soluções com todas as formigas
            ants = []
            for _ in range(self.num_ants):
                ant = self.build_solution()
                ants.append(ant)
            
            # Atualizar melhor solução
            for ant in ants:
                if ant.total_time < self.best_time:
                    self.best_time = ant.total_time
                    self.best_ant = Ant()
                    self.best_ant.strategy = ant.strategy.copy()
                    self.best_ant.total_time = ant.total_time
            
            # Atualizar feromônios
            self.update_pheromones(ants)
            
            # Registrar melhor fitness da iteração
            best_fitness = 1.0 / self.best_time if self.best_time < float('inf') else 0.0
            self.fitness_history.append(best_fitness)
            
            if iteration % 10 == 0:
                print(f"Iteração {iteration}: Melhor tempo = {self.best_time:.2f}s")
        
        return self.best_ant
    
    def get_fitness_history(self) -> List[float]:
        """
        Retorna o histórico de fitness para análise.
        
        Returns:
            Lista com melhor fitness de cada iteração
        """
        return self.fitness_history
    
    def get_pheromone_matrix(self) -> np.ndarray:
        """
        Retorna a matriz de feromônios para análise.
        
        Returns:
            Matriz de feromônios
        """
        return self.pheromone_matrix.copy() 