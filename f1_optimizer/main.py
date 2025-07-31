#!/usr/bin/env python3
"""
Script principal para execução do otimizador de pit stop de F1.
"""

import sys
import os
import time
import json
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_handler import DataHandler
from src.race_simulator import RaceSimulator
from src.genetic_algorithm import GeneticAlgorithm
from src.ant_colony import AntColonyOptimizer


def main():
    """
    Função principal que executa o fluxo completo do projeto.
    """
    print("=" * 60)
    print("OTIMIZADOR DE ESTRATÉGIAS DE PIT STOP - FÓRMULA 1")
    print("=" * 60)
    
    # Configuração do cenário de teste
    year = 2023
    race_name = "Brazil Grand Prix"
    driver_code = "VER"  # Max Verstappen
    
    print(f"\nCenário de teste:")
    print(f"Ano: {year}")
    print(f"Corrida: {race_name}")
    print(f"Piloto: {driver_code}")
    print("-" * 40)
    
    # Passo 1: Carregar dados
    print("\n1. Carregando dados da corrida...")
    data_handler = DataHandler()
    race_data = data_handler.get_race_data(year, race_name, driver_code)
    
    if race_data.empty:
        print("Erro: Não foi possível carregar dados da corrida.")
        print("Verifique se os parâmetros estão corretos e se há conexão com a internet.")
        return
    
    # Informações da corrida
    race_info = data_handler.get_race_info(race_data)
    print(f"Dados carregados com sucesso!")
    print(f"Total de voltas: {race_info['total_laps']}")
    print(f"Compostos utilizados: {race_info['compounds_used']}")
    print(f"Tempo médio de volta: {race_info['avg_lap_time']:.2f}s")
    
    # Passo 2: Inicializar simulador
    print("\n2. Inicializando simulador de corrida...")
    simulator = RaceSimulator(race_data, pit_stop_time=25.0)
    
    # Mostrar parâmetros do modelo
    model_params = simulator.get_model_parameters()
    print(f"Parâmetros do modelo:")
    print(f"  Tempo base (T_base): {model_params['T_base']:.2f}s")
    print(f"  Efeito combustível: {model_params['fuel_effect_coeff']:.3f}s/volta")
    print(f"  Coeficientes de degradação: {model_params['degradation_coeffs']}")
    print(f"  Deltas de performance: {model_params['alpha_coeffs']}")
    
    # Passo 3: Executar Algoritmo Genético
    print("\n3. Executando Algoritmo Genético...")
    print("-" * 40)
    
    ga = GeneticAlgorithm(
        simulator=simulator,
        population_size=50,
        generations=100,
        mutation_rate=0.1,
        crossover_rate=0.8,
        elitism_size=5
    )
    
    start_time = time.time()
    best_ga_individual = ga.run()
    ga_time = time.time() - start_time
    
    print(f"\nResultados do Algoritmo Genético:")
    print(f"  Melhor estratégia: {best_ga_individual.chromosome}")
    print(f"  Tempo total: {1/best_ga_individual.fitness:.2f}s")
    print(f"  Tempo de execução: {ga_time:.2f}s")
    
    # Passo 4: Executar Algoritmo de Colônia de Formigas
    print("\n4. Executando Algoritmo de Colônia de Formigas...")
    print("-" * 40)
    
    aco = AntColonyOptimizer(
        simulator=simulator,
        num_ants=30,
        iterations=50,
        evaporation_rate=0.1,
        alpha=1.0,
        beta=2.0
    )
    
    start_time = time.time()
    best_aco_ant = aco.run()
    aco_time = time.time() - start_time
    
    print(f"\nResultados do Algoritmo ACO:")
    print(f"  Melhor estratégia: {best_aco_ant.strategy}")
    print(f"  Tempo total: {best_aco_ant.total_time:.2f}s")
    print(f"  Tempo de execução: {aco_time:.2f}s")
    
    # Passo 5: Análise comparativa
    print("\n5. Análise Comparativa")
    print("=" * 40)
    
    ga_time_total = 1/best_ga_individual.fitness if best_ga_individual.fitness > 0 else float('inf')
    aco_time_total = best_aco_ant.total_time
    
    print(f"Algoritmo Genético:")
    print(f"  Tempo total: {ga_time_total:.2f}s")
    print(f"  Estratégia: {best_ga_individual.chromosome}")
    print(f"  Tempo de execução: {ga_time:.2f}s")
    
    print(f"\nAlgoritmo ACO:")
    print(f"  Tempo total: {aco_time_total:.2f}s")
    print(f"  Estratégia: {best_aco_ant.strategy}")
    print(f"  Tempo de execução: {aco_time:.2f}s")
    
    # Determinar o melhor algoritmo
    if ga_time_total < aco_time_total:
        winner = "Algoritmo Genético"
        best_time = ga_time_total
        best_strategy = best_ga_individual.chromosome
    else:
        winner = "Algoritmo ACO"
        best_time = aco_time_total
        best_strategy = best_aco_ant.strategy
    
    print(f"\n🏆 MELHOR RESULTADO:")
    print(f"  Algoritmo: {winner}")
    print(f"  Tempo total: {best_time:.2f}s")
    print(f"  Estratégia: {best_strategy}")
    
    # Salvar resultados
    save_results(year, race_name, driver_code, race_info, model_params,
                best_ga_individual, ga_time, ga.get_fitness_history(),
                best_aco_ant, aco_time, aco.get_fitness_history())
    
    print(f"\n✅ Análise concluída! Resultados salvos em 'results/'")
    print("=" * 60)


def save_results(year, race_name, driver_code, race_info, model_params,
                best_ga_individual, ga_time, ga_history,
                best_aco_ant, aco_time, aco_history):
    """
    Salva os resultados da análise.
    """
    # Criar diretório de resultados
    os.makedirs('results', exist_ok=True)
    
    # Preparar dados para salvar
    results = {
        'scenario': {
            'year': year,
            'race_name': race_name,
            'driver_code': driver_code,
            'race_info': race_info
        },
        'model_parameters': model_params,
        'genetic_algorithm': {
            'best_strategy': best_ga_individual.chromosome,
            'best_time': 1/best_ga_individual.fitness if best_ga_individual.fitness > 0 else float('inf'),
            'execution_time': ga_time,
            'fitness_history': ga_history
        },
        'ant_colony': {
            'best_strategy': best_aco_ant.strategy,
            'best_time': best_aco_ant.total_time,
            'execution_time': aco_time,
            'fitness_history': aco_history
        },
        'timestamp': datetime.now().isoformat()
    }
    
    # Salvar em JSON
    filename = f"results/optimization_results_{year}_{race_name.replace(' ', '_')}_{driver_code}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Resultados salvos em: {filename}")


if __name__ == "__main__":
    main() 