#!/usr/bin/env python3
"""
Script para testar múltiplos pilotos na mesma corrida.
"""

import sys
import os
import json
import time
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_handler import DataHandler
from src.race_simulator import RaceSimulator
from src.genetic_algorithm import GeneticAlgorithm
from src.ant_colony import AntColonyOptimizer


def test_driver(year: int, race_name: str, driver_code: str, n_executions: int = 10):
    """
    Testa um piloto específico com ambos os algoritmos.
    
    Args:
        year: Ano da corrida
        race_name: Nome da corrida
        driver_code: Código do piloto
        n_executions: Número de execuções por algoritmo
        
    Returns:
        Dicionário com resultados
    """
    print(f"\n{'='*60}")
    print(f"TESTANDO PILOTO: {driver_code}")
    print(f"{'='*60}")
    
    # Carregar dados
    print(f"📊 Carregando dados para {driver_code}...")
    data_handler = DataHandler()
    race_data = data_handler.get_race_data(year, race_name, driver_code)
    
    if race_data.empty:
        print(f"❌ Erro: Não foi possível carregar dados para {driver_code}")
        return None
    
    # Informações da corrida
    race_info = data_handler.get_race_info(race_data)
    initial_compound = race_data['Compound'].iloc[0] if not race_data.empty else "N/A"
    
    print(f"✅ Dados carregados!")
    print(f"   Total de voltas: {race_info['total_laps']}")
    print(f"   Compostos utilizados: {race_info['compounds_used']}")
    print(f"   Composto inicial: {initial_compound}")
    print(f"   Tempo médio de volta: {race_info['avg_lap_time']:.2f}s")
    
    # Criar simulador
    simulator = RaceSimulator(race_data)
    
    # Parâmetros otimizados (usando os encontrados para HAM)
    ga_params = {
        'population_size': 20,
        'generations': 100,
        'mutation_rate': 0.15,
        'crossover_rate': 0.6,
        'elitism_size': 5
    }
    
    aco_params = {
        'num_ants': 25,
        'iterations': 30,
        'evaporation_rate': 0.1,
        'alpha': 1.0,
        'beta': 2.0
    }
    
    # Testar GA
    print(f"\n🔬 Testando Algoritmo Genético...")
    ga_times = []
    ga_strategies = []
    
    for i in range(n_executions):
        print(f"  Execução {i+1}/{n_executions}...")
        start_time = time.time()
        
        ga = GeneticAlgorithm(simulator, **ga_params)
        best_individual = ga.run()
        execution_time = time.time() - start_time
        
        ga_times.append(1/best_individual.fitness if best_individual.fitness > 0 else float('inf'))
        ga_strategies.append(best_individual.chromosome)
    
    # Testar ACO
    print(f"\n🔬 Testando Algoritmo ACO...")
    aco_times = []
    aco_strategies = []
    
    for i in range(n_executions):
        print(f"  Execução {i+1}/{n_executions}...")
        start_time = time.time()
        
        aco = AntColonyOptimizer(simulator, **aco_params)
        best_ant = aco.run()
        execution_time = time.time() - start_time
        
        aco_times.append(best_ant.total_time)
        aco_strategies.append(best_ant.strategy)
    
    # Calcular estatísticas
    ga_mean = sum(ga_times) / len(ga_times)
    aco_mean = sum(aco_times) / len(aco_times)
    
    # Determinar melhor algoritmo
    if ga_mean < aco_mean:
        better_algorithm = 'GA'
        improvement = ((aco_mean - ga_mean) / aco_mean) * 100
    else:
        better_algorithm = 'ACO'
        improvement = ((ga_mean - aco_mean) / ga_mean) * 100
    
    # Resultados
    results = {
        'driver_code': driver_code,
        'scenario': {
            'year': year,
            'race_name': race_name,
            'initial_compound': initial_compound,
            'total_laps': race_info['total_laps'],
            'compounds_used': race_info['compounds_used']
        },
        'ga_results': {
            'times': ga_times,
            'strategies': ga_strategies,
            'mean_time': ga_mean,
            'best_time': min(ga_times),
            'best_strategy': ga_strategies[ga_times.index(min(ga_times))]
        },
        'aco_results': {
            'times': aco_times,
            'strategies': aco_strategies,
            'mean_time': aco_mean,
            'best_time': min(aco_times),
            'best_strategy': aco_strategies[aco_times.index(min(aco_times))]
        },
        'comparison': {
            'better_algorithm': better_algorithm,
            'improvement_percent': improvement,
            'ga_mean': ga_mean,
            'aco_mean': aco_mean
        }
    }
    
    # Exibir resultados
    print(f"\n📊 RESULTADOS PARA {driver_code}")
    print(f"{'='*40}")
    print(f"GA - Tempo médio: {ga_mean:.2f}s")
    print(f"GA - Melhor tempo: {min(ga_times):.2f}s")
    print(f"GA - Melhor estratégia: {ga_strategies[ga_times.index(min(ga_times))]}")
    print()
    print(f"ACO - Tempo médio: {aco_mean:.2f}s")
    print(f"ACO - Melhor tempo: {min(aco_times):.2f}s")
    print(f"ACO - Melhor estratégia: {aco_strategies[aco_times.index(min(aco_times))]}")
    print()
    print(f"🏆 MELHOR ALGORITMO: {better_algorithm}")
    print(f"📈 Melhoria: {improvement:.2f}%")
    
    return results


def main():
    """
    Função principal para testar múltiplos pilotos.
    """
    print("🏎️ TESTE DE MÚLTIPLOS PILOTOS - SPAIN 2024")
    print("=" * 60)
    
    # Configuração
    year = 2024
    race_name = "Spain Grand Prix"
    drivers = ["HAM", "VER", "ALO"]  # Hamilton, Verstappen, Alonso
    n_executions = 10  # Reduzido para teste mais rápido
    
    # Criar diretório de resultados
    os.makedirs('results', exist_ok=True)
    
    # Testar cada piloto
    all_results = {}
    
    for driver in drivers:
        try:
            results = test_driver(year, race_name, driver, n_executions)
            if results:
                all_results[driver] = results
        except Exception as e:
            print(f"❌ Erro ao testar {driver}: {e}")
    
    # Salvar resultados
    if all_results:
        filename = f"results/multiple_drivers_test_{year}_{race_name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        
        # Análise comparativa
        print(f"\n📊 ANÁLISE COMPARATIVA")
        print(f"{'='*40}")
        
        for driver, results in all_results.items():
            comp = results['comparison']
            print(f"\n{driver}:")
            print(f"  GA: {comp['ga_mean']:.2f}s")
            print(f"  ACO: {comp['aco_mean']:.2f}s")
            print(f"  Melhor: {comp['better_algorithm']}")
            print(f"  Melhoria: {comp['improvement_percent']:.2f}%")
        
        # Contar vitórias por algoritmo
        ga_wins = sum(1 for r in all_results.values() if r['comparison']['better_algorithm'] == 'GA')
        aco_wins = sum(1 for r in all_results.values() if r['comparison']['better_algorithm'] == 'ACO')
        
        print(f"\n🏆 RESUMO FINAL:")
        print(f"  GA venceu: {ga_wins} pilotos")
        print(f"  ACO venceu: {aco_wins} pilotos")
        
        if ga_wins > aco_wins:
            print(f"  🥇 GA é superior para esta corrida!")
        elif aco_wins > ga_wins:
            print(f"  🥇 ACO é superior para esta corrida!")
        else:
            print(f"  🤝 Empate entre os algoritmos!")
    
    print(f"\n✅ Teste de múltiplos pilotos concluído!")


if __name__ == "__main__":
    main() 