#!/usr/bin/env python3
"""
Script para visualização e análise dos resultados do otimizador.
"""

import sys
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configurar estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


def load_results(filename):
    """
    Carrega resultados de um arquivo JSON.
    
    Args:
        filename: Caminho do arquivo JSON
        
    Returns:
        Dicionário com os resultados
    """
    with open(filename, 'r') as f:
        return json.load(f)


def plot_convergence_comparison(results):
    """
    Plota comparação de convergência entre GA e ACO.
    
    Args:
        results: Dicionário com resultados
    """
    ga_history = results['genetic_algorithm']['fitness_history']
    aco_history = results['ant_colony']['fitness_history']
    
    plt.figure(figsize=(12, 6))
    
    # Normalizar para mesma escala
    ga_normalized = [x/max(ga_history) for x in ga_history]
    aco_normalized = [x/max(aco_history) for x in aco_history]
    
    plt.plot(ga_normalized, label='Algoritmo Genético', linewidth=2, marker='o', markersize=4)
    plt.plot(aco_normalized, label='Algoritmo ACO', linewidth=2, marker='s', markersize=4)
    
    plt.xlabel('Geração/Iteração')
    plt.ylabel('Fitness Normalizado')
    plt.title('Comparação de Convergência: GA vs ACO')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/convergence_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_strategy_comparison(results):
    """
    Plota comparação das estratégias encontradas.
    
    Args:
        results: Dicionário com resultados
    """
    ga_strategy = results['genetic_algorithm']['best_strategy']
    aco_strategy = results['ant_colony']['best_strategy']
    
    ga_time = results['genetic_algorithm']['best_time']
    aco_time = results['ant_colony']['best_time']
    
    # Preparar dados para visualização
    strategies_data = []
    
    # Estratégia do GA
    for lap, compound in ga_strategy:
        strategies_data.append({
            'Algoritmo': 'GA',
            'Volta': lap,
            'Composto': compound,
            'Tempo': ga_time
        })
    
    # Estratégia do ACO
    for lap, compound in aco_strategy:
        strategies_data.append({
            'Algoritmo': 'ACO',
            'Volta': lap,
            'Composto': compound,
            'Tempo': aco_time
        })
    
    df = pd.DataFrame(strategies_data)
    
    if not df.empty:
        plt.figure(figsize=(12, 6))
        
        # Criar gráfico de barras
        colors = {'GA': 'skyblue', 'ACO': 'lightcoral'}
        
        for algorithm in ['GA', 'ACO']:
            alg_data = df[df['Algoritmo'] == algorithm]
            if not alg_data.empty:
                plt.bar(alg_data['Volta'], 
                       [1] * len(alg_data), 
                       label=f'{algorithm} ({alg_data["Tempo"].iloc[0]:.1f}s)',
                       color=colors[algorithm],
                       alpha=0.7)
        
        plt.xlabel('Volta da Parada')
        plt.ylabel('Estratégia')
        plt.title('Comparação das Estratégias Encontradas')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('results/strategy_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()


def plot_performance_metrics(results):
    """
    Plota métricas de performance dos algoritmos.
    
    Args:
        results: Dicionário com resultados
    """
    ga_time = results['genetic_algorithm']['best_time']
    aco_time = results['ant_colony']['best_time']
    ga_exec_time = results['genetic_algorithm']['execution_time']
    aco_exec_time = results['ant_colony']['execution_time']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico 1: Tempo total da corrida
    algorithms = ['GA', 'ACO']
    times = [ga_time, aco_time]
    colors = ['skyblue', 'lightcoral']
    
    bars1 = ax1.bar(algorithms, times, color=colors, alpha=0.7)
    ax1.set_ylabel('Tempo Total (segundos)')
    ax1.set_title('Tempo Total da Corrida')
    ax1.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, time in zip(bars1, times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{time:.1f}s', ha='center', va='bottom')
    
    # Gráfico 2: Tempo de execução
    exec_times = [ga_exec_time, aco_exec_time]
    
    bars2 = ax2.bar(algorithms, exec_times, color=colors, alpha=0.7)
    ax2.set_ylabel('Tempo de Execução (segundos)')
    ax2.set_title('Tempo de Execução dos Algoritmos')
    ax2.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, time in zip(bars2, exec_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{time:.2f}s', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('results/performance_metrics.png', dpi=300, bbox_inches='tight')
    plt.show()


def create_summary_report(results):
    """
    Cria um relatório resumido dos resultados.
    
    Args:
        results: Dicionário com resultados
    """
    scenario = results['scenario']
    ga_results = results['genetic_algorithm']
    aco_results = results['ant_colony']
    
    print("=" * 60)
    print("RELATÓRIO DE ANÁLISE - OTIMIZADOR F1")
    print("=" * 60)
    
    print(f"\nCENÁRIO:")
    print(f"  Ano: {scenario['year']}")
    print(f"  Corrida: {scenario['race_name']}")
    print(f"  Piloto: {scenario['driver_code']}")
    print(f"  Total de voltas: {scenario['race_info']['total_laps']}")
    
    print(f"\nRESULTADOS:")
    print(f"  Algoritmo Genético:")
    print(f"    Estratégia: {ga_results['best_strategy']}")
    print(f"    Tempo total: {ga_results['best_time']:.2f}s")
    print(f"    Tempo de execução: {ga_results['execution_time']:.2f}s")
    
    print(f"  Algoritmo ACO:")
    print(f"    Estratégia: {aco_results['best_strategy']}")
    print(f"    Tempo total: {aco_results['best_time']:.2f}s")
    print(f"    Tempo de execução: {aco_results['execution_time']:.2f}s")
    
    # Determinar o melhor
    if ga_results['best_time'] < aco_results['best_time']:
        winner = "Algoritmo Genético"
        improvement = ((aco_results['best_time'] - ga_results['best_time']) / aco_results['best_time']) * 100
    else:
        winner = "Algoritmo ACO"
        improvement = ((ga_results['best_time'] - aco_results['best_time']) / ga_results['best_time']) * 100
    
    print(f"\n🏆 MELHOR ALGORITMO: {winner}")
    print(f"   Melhoria: {improvement:.2f}%")
    
    print(f"\nPARÂMETROS DO MODELO:")
    model_params = results['model_parameters']
    print(f"  Tempo base: {model_params['T_base']:.2f}s")
    print(f"  Efeito combustível: {model_params['fuel_effect_coeff']:.3f}s/volta")
    print(f"  Tempo de pit stop: {model_params['pit_stop_time']:.1f}s")


def main():
    """
    Função principal para visualização dos resultados.
    """
    # Procurar por arquivos de resultados
    results_dir = 'results'
    if not os.path.exists(results_dir):
        print("Diretório 'results' não encontrado. Execute main.py primeiro.")
        return
    
    result_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    
    if not result_files:
        print("Nenhum arquivo de resultados encontrado. Execute main.py primeiro.")
        return
    
    # Usar o arquivo mais recente
    latest_file = max(result_files, key=lambda x: os.path.getctime(os.path.join(results_dir, x)))
    filepath = os.path.join(results_dir, latest_file)
    
    print(f"Carregando resultados de: {filepath}")
    
    # Carregar resultados
    results = load_results(filepath)
    
    # Criar visualizações
    print("\nGerando visualizações...")
    
    # Criar diretório para imagens se não existir
    os.makedirs('results', exist_ok=True)
    
    # Gerar gráficos
    plot_convergence_comparison(results)
    plot_strategy_comparison(results)
    plot_performance_metrics(results)
    
    # Criar relatório
    create_summary_report(results)
    
    print(f"\n✅ Visualizações salvas em 'results/'")
    print("=" * 60)


if __name__ == "__main__":
    main() 