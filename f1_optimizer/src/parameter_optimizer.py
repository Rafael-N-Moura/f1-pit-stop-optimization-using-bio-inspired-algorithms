import itertools
import random
import time
import json
import numpy as np
from typing import Dict, List, Tuple, Any
from .data_handler import DataHandler
from .race_simulator import RaceSimulator
from .genetic_algorithm import GeneticAlgorithm
from .ant_colony import AntColonyOptimizer


class ParameterOptimizer:
    """
    Classe para otimização de parâmetros dos algoritmos GA e ACO.
    """
    
    def __init__(self, algorithm_type: str, base_params: Dict, param_ranges: Dict):
        """
        Inicializa o otimizador de parâmetros.
        
        Args:
            algorithm_type: 'GA' ou 'ACO'
            base_params: Parâmetros base do algoritmo
            param_ranges: Dicionário com ranges de parâmetros para testar
        """
        self.algorithm_type = algorithm_type
        self.base_params = base_params
        self.param_ranges = param_ranges
        self.results = []
        self.best_params = None
        self.best_score = float('inf')
    
    def grid_search(self, scenario: Dict, n_executions: int = 5) -> Dict:
        """
        Realiza busca em grade para encontrar melhores parâmetros.
        
        Args:
            scenario: Dicionário com cenário (year, race_name, driver_code)
            n_executions: Número de execuções por configuração
            
        Returns:
            Dicionário com melhores parâmetros encontrados
        """
        print(f"🔍 Iniciando Grid Search para {self.algorithm_type}")
        
        # Carregar dados do cenário
        data_handler = DataHandler()
        race_data = data_handler.get_race_data(
            scenario['year'], 
            scenario['race_name'], 
            scenario['driver_code']
        )
        
        if race_data.empty:
            print("❌ Erro: Não foi possível carregar dados do cenário")
            return {}
        
        # Criar simulador
        simulator = RaceSimulator(race_data)
        
        # Gerar todas as combinações de parâmetros
        param_names = list(self.param_ranges.keys())
        param_values = list(self.param_ranges.values())
        combinations = list(itertools.product(*param_values))
        
        print(f"📊 Testando {len(combinations)} combinações de parâmetros...")
        
        for i, combination in enumerate(combinations):
            # Criar dicionário de parâmetros
            params = dict(zip(param_names, combination))
            
            # Avaliar configuração
            score = self._evaluate_configuration(simulator, params, n_executions)
            
            # Armazenar resultado
            result = {
                'params': params,
                'score': score,
                'combination_id': i
            }
            self.results.append(result)
            
            # Atualizar melhor resultado
            if score < self.best_score:
                self.best_score = score
                self.best_params = params.copy()
            
            if (i + 1) % 10 == 0:
                print(f"  Progresso: {i + 1}/{len(combinations)} - Melhor score: {self.best_score:.2f}")
        
        print(f"✅ Grid Search concluído! Melhor score: {self.best_score:.2f}")
        return self.best_params
    
    def random_search(self, scenario: Dict, n_trials: int = 100, n_executions: int = 3) -> Dict:
        """
        Realiza busca aleatória para exploração rápida.
        
        Args:
            scenario: Dicionário com cenário
            n_trials: Número de tentativas aleatórias
            n_executions: Número de execuções por configuração
            
        Returns:
            Dicionário com melhores parâmetros encontrados
        """
        print(f"🎲 Iniciando Random Search para {self.algorithm_type}")
        
        # Carregar dados do cenário
        data_handler = DataHandler()
        race_data = data_handler.get_race_data(
            scenario['year'], 
            scenario['race_name'], 
            scenario['driver_code']
        )
        
        if race_data.empty:
            print("❌ Erro: Não foi possível carregar dados do cenário")
            return {}
        
        # Criar simulador
        simulator = RaceSimulator(race_data)
        
        for trial in range(n_trials):
            # Gerar parâmetros aleatórios
            params = self._generate_random_params()
            
            # Avaliar configuração
            score = self._evaluate_configuration(simulator, params, n_executions)
            
            # Armazenar resultado
            result = {
                'params': params,
                'score': score,
                'trial_id': trial
            }
            self.results.append(result)
            
            # Atualizar melhor resultado
            if score < self.best_score:
                self.best_score = score
                self.best_params = params.copy()
            
            if (trial + 1) % 20 == 0:
                print(f"  Progresso: {trial + 1}/{n_trials} - Melhor score: {self.best_score:.2f}")
        
        print(f"✅ Random Search concluído! Melhor score: {self.best_score:.2f}")
        return self.best_params
    
    def _evaluate_configuration(self, simulator: RaceSimulator, params: Dict, n_executions: int) -> float:
        """
        Avalia uma configuração de parâmetros.
        
        Args:
            simulator: Simulador de corrida
            params: Parâmetros a testar
            n_executions: Número de execuções
            
        Returns:
            Score médio da configuração (menor = melhor)
        """
        scores = []
        
        for _ in range(n_executions):
            try:
                if self.algorithm_type == 'GA':
                    algorithm = GeneticAlgorithm(simulator, **params)
                    best_individual = algorithm.run()
                    score = 1 / best_individual.fitness if best_individual.fitness > 0 else float('inf')
                elif self.algorithm_type == 'ACO':
                    algorithm = AntColonyOptimizer(simulator, **params)
                    best_ant = algorithm.run()
                    score = best_ant.total_time
                else:
                    raise ValueError(f"Algoritmo não suportado: {self.algorithm_type}")
                
                scores.append(score)
                
            except Exception as e:
                print(f"⚠️ Erro na execução: {e}")
                scores.append(float('inf'))
        
        return np.mean(scores)
    
    def _generate_random_params(self) -> Dict:
        """
        Gera parâmetros aleatórios dentro dos ranges definidos.
        
        Returns:
            Dicionário com parâmetros aleatórios
        """
        params = {}
        
        for param_name, param_range in self.param_ranges.items():
            if isinstance(param_range, list):
                params[param_name] = random.choice(param_range)
            elif isinstance(param_range, tuple) and len(param_range) == 2:
                # Range numérico
                min_val, max_val = param_range
                if isinstance(min_val, int):
                    params[param_name] = random.randint(min_val, max_val)
                else:
                    params[param_name] = random.uniform(min_val, max_val)
            else:
                params[param_name] = random.choice(param_range)
        
        return params
    
    def get_best_params(self) -> Dict:
        """
        Retorna os melhores parâmetros encontrados.
        
        Returns:
            Dicionário com melhores parâmetros
        """
        return self.best_params
    
    def get_results_summary(self) -> Dict:
        """
        Retorna resumo dos resultados.
        
        Returns:
            Dicionário com resumo dos resultados
        """
        if not self.results:
            return {}
        
        scores = [r['score'] for r in self.results]
        
        return {
            'algorithm_type': self.algorithm_type,
            'best_params': self.best_params,
            'best_score': self.best_score,
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'n_evaluations': len(self.results)
        }
    
    def save_results(self, filename: str):
        """
        Salva resultados em arquivo JSON.
        
        Args:
            filename: Nome do arquivo para salvar
        """
        results_data = {
            'algorithm_type': self.algorithm_type,
            'best_params': self.best_params,
            'best_score': self.best_score,
            'all_results': self.results,
            'summary': self.get_results_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"💾 Resultados salvos em: {filename}")


def optimize_ga_parameters(scenario: Dict) -> Dict:
    """
    Otimiza parâmetros do Algoritmo Genético.
    
    Args:
        scenario: Dicionário com cenário
        
    Returns:
        Dicionário com melhores parâmetros
    """
    # Ranges de parâmetros para GA
    ga_ranges = {
        'population_size': [20, 30, 50, 75, 100],
        'generations': [50, 75, 100, 150, 200],
        'mutation_rate': [0.05, 0.1, 0.15, 0.2, 0.25],
        'crossover_rate': [0.6, 0.7, 0.8, 0.9, 0.95],
        'elitism_size': [2, 3, 5, 7, 10]
    }
    
    # Parâmetros base
    ga_base = {
        'population_size': 50,
        'generations': 100,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8,
        'elitism_size': 5
    }
    
    optimizer = ParameterOptimizer('GA', ga_base, ga_ranges)
    
    # Realizar otimização
    best_params = optimizer.grid_search(scenario, n_executions=3)
    
    # Salvar resultados
    optimizer.save_results(f'results/ga_optimization_{scenario["year"]}_{scenario["race_name"].replace(" ", "_")}_{scenario["driver_code"]}.json')
    
    return best_params


def optimize_aco_parameters(scenario: Dict) -> Dict:
    """
    Otimiza parâmetros do Algoritmo ACO.
    
    Args:
        scenario: Dicionário com cenário
        
    Returns:
        Dicionário com melhores parâmetros
    """
    # Ranges de parâmetros para ACO
    aco_ranges = {
        'num_ants': [15, 25, 30, 40, 50],
        'iterations': [30, 50, 75, 100, 150],
        'evaporation_rate': [0.05, 0.1, 0.15, 0.2, 0.25],
        'alpha': [0.5, 1.0, 1.5, 2.0, 2.5],
        'beta': [1.0, 1.5, 2.0, 2.5, 3.0]
    }
    
    # Parâmetros base
    aco_base = {
        'num_ants': 30,
        'iterations': 50,
        'evaporation_rate': 0.1,
        'alpha': 1.0,
        'beta': 2.0
    }
    
    optimizer = ParameterOptimizer('ACO', aco_base, aco_ranges)
    
    # Realizar otimização
    best_params = optimizer.grid_search(scenario, n_executions=3)
    
    # Salvar resultados
    optimizer.save_results(f'results/aco_optimization_{scenario["year"]}_{scenario["race_name"].replace(" ", "_")}_{scenario["driver_code"]}.json')
    
    return best_params 