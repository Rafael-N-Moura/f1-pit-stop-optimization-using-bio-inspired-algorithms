#!/usr/bin/env python3
"""
Script para visualização dos resultados estatísticos.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configurar estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


def load_statistical_results(filename):
    """
    Carrega resultados estatísticos de arquivo JSON.
    
    Args:
        filename: Nome do arquivo JSON
        
    Returns:
        Dicionário com resultados
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo {filename}: {e}")
        return None


def plot_performance_comparison(results):
    """
    Cria gráfico de comparação de performance entre GA e ACO.
    
    Args:
        results: Dicionário com resultados
    """
    if 'results' not in results:
        print("❌ Dados de resultados não encontrados")
        return
    
    ga_results = results['results'].get('GA', {})
    aco_results = results['results'].get('ACO', {})
    
    if not ga_results or not aco_results:
        print("❌ Dados de GA ou ACO não encontrados")
        return
    
    # Extrair tempos
    ga_times = [r['best_time'] for r in ga_results['execution_results'] if 'error' not in r]
    aco_times = [r['best_time'] for r in aco_results['execution_results'] if 'error' not in r]
    
    if not ga_times or not aco_times:
        print("❌ Dados de tempo insuficientes")
        return
    
    # Criar figura
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comparação de Performance: GA vs ACO', fontsize=16, fontweight='bold')
    
    # 1. Boxplot
    data = [ga_times, aco_times]
    labels = ['GA', 'ACO']
    bp = ax1.boxplot(data, tick_labels=labels, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax1.set_title('Distribuição dos Tempos de Corrida')
    ax1.set_ylabel('Tempo (segundos)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Histograma
    ax2.hist(ga_times, alpha=0.7, label='GA', bins=15, color='lightblue', edgecolor='black')
    ax2.hist(aco_times, alpha=0.7, label='ACO', bins=15, color='lightcoral', edgecolor='black')
    ax2.set_title('Distribuição de Frequência')
    ax2.set_xlabel('Tempo (segundos)')
    ax2.set_ylabel('Frequência')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Gráfico de barras - estatísticas
    stats_ga = ga_results['statistics']
    stats_aco = aco_results['statistics']
    
    metrics = ['mean_time', 'std_time', 'cv_time']
    metric_labels = ['Tempo Médio', 'Desvio Padrão', 'CV (%)']
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ga_values = [stats_ga.get(m, 0) for m in metrics]
    aco_values = [stats_aco.get(m, 0) for m in metrics]
    
    bars1 = ax3.bar(x - width/2, ga_values, width, label='GA', color='lightblue')
    bars2 = ax3.bar(x + width/2, aco_values, width, label='ACO', color='lightcoral')
    
    ax3.set_title('Comparação de Métricas Estatísticas')
    ax3.set_ylabel('Valor')
    ax3.set_xticks(x)
    ax3.set_xticklabels(metric_labels)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
    
    # 4. Gráfico de convergência
    if 'fitness_history' in ga_results['execution_results'][0]:
        # Média das histórias de fitness
        ga_histories = [r['fitness_history'] for r in ga_results['execution_results'] if 'error' not in r]
        aco_histories = [r['fitness_history'] for r in aco_results['execution_results'] if 'error' not in r]
        
        if ga_histories and aco_histories:
            ga_mean_history = np.mean(ga_histories, axis=0)
            aco_mean_history = np.mean(aco_histories, axis=0)
            
            generations = range(len(ga_mean_history))
            iterations = range(len(aco_mean_history))
            
            ax4.plot(generations, ga_mean_history, label='GA', color='blue', linewidth=2)
            ax4.plot(iterations, aco_mean_history, label='ACO', color='red', linewidth=2)
            ax4.set_title('Convergência dos Algoritmos')
            ax4.set_xlabel('Geração/Iteração')
            ax4.set_ylabel('Fitness')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_statistical_tests(results):
    """
    Cria gráfico com resultados dos testes estatísticos.
    
    Args:
        results: Dicionário com resultados
    """
    if 'statistical_tests' not in results:
        print("❌ Dados de testes estatísticos não encontrados")
        return
    
    tests = results['statistical_tests']
    
    if 'comparison' not in tests:
        print("❌ Dados de comparação não encontrados")
        return
    
    comp = tests['comparison']
    
    # Criar figura
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise Estatística: GA vs ACO', fontsize=16, fontweight='bold')
    
    # 1. Comparação de médias
    algorithms = ['GA', 'ACO']
    means = [comp['ga_mean'], comp['aco_mean']]
    colors = ['lightblue', 'lightcoral']
    
    bars = ax1.bar(algorithms, means, color=colors, edgecolor='black')
    ax1.set_title('Comparação de Tempos Médios')
    ax1.set_ylabel('Tempo (segundos)')
    ax1.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, mean in zip(bars, means):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{mean:.2f}s', ha='center', va='bottom')
    
    # 2. Melhoria percentual
    improvement = comp['improvement_percent']
    better_alg = comp['better_algorithm']
    
    ax2.bar([better_alg], [improvement], color='lightgreen', edgecolor='black')
    ax2.set_title(f'Melhoria do {better_alg}')
    ax2.set_ylabel('Melhoria (%)')
    ax2.grid(True, alpha=0.3)
    
    # Adicionar valor na barra
    ax2.text(0, improvement, f'{improvement:.2f}%', ha='center', va='bottom')
    
    # 3. Significância estatística
    significant = comp['significant_difference']
    significance_text = 'Sim' if significant else 'Não'
    significance_color = 'lightgreen' if significant else 'lightcoral'
    
    ax3.bar(['Diferença Significativa'], [1], color=significance_color, edgecolor='black')
    ax3.set_title('Teste de Significância (α = 0.05)')
    ax3.set_ylabel('Resultado')
    ax3.set_ylim(0, 1.2)
    ax3.text(0, 0.5, significance_text, ha='center', va='center', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Tamanho do efeito
    if 'effect_size' in tests:
        effect = tests['effect_size']
        cohens_d = effect['cohens_d']
        interpretation = effect['interpretation']
        
        # Criar gráfico de tamanho do efeito
        effect_sizes = ['Pequeno', 'Médio', 'Grande', 'Muito Grande']
        effect_thresholds = [0.2, 0.5, 0.8, 2.0]
        
        # Determinar categoria
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            category = 'Pequeno'
        elif abs_d < 0.5:
            category = 'Médio'
        elif abs_d < 0.8:
            category = 'Grande'
        else:
            category = 'Muito Grande'
        
        # Criar gráfico
        categories = ['Pequeno', 'Médio', 'Grande', 'Muito Grande']
        values = [0.1, 0.35, 0.65, 1.0]  # Valores representativos
        
        colors_map = ['lightblue', 'lightgreen', 'orange', 'red']
        bar_colors = [colors_map[i] if cat == category else 'lightgray' for i, cat in enumerate(categories)]
        
        bars = ax4.bar(categories, values, color=bar_colors, edgecolor='black')
        ax4.set_title(f'Tamanho do Efeito (Cohen\'s d = {cohens_d:.3f})')
        ax4.set_ylabel('Magnitude')
        ax4.grid(True, alpha=0.3)
        
        # Adicionar valor na barra destacada
        for i, (bar, cat) in enumerate(zip(bars, categories)):
            if cat == category:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{cohens_d:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_strategy_analysis(results):
    """
    Cria gráfico de análise das estratégias encontradas.
    
    Args:
        results: Dicionário com resultados
    """
    if 'results' not in results:
        print("❌ Dados de resultados não encontrados")
        return
    
    ga_results = results['results'].get('GA', {})
    aco_results = results['results'].get('ACO', {})
    
    if not ga_results or not aco_results:
        print("❌ Dados de GA ou ACO não encontrados")
        return
    
    # Extrair dados de estratégias
    ga_strategies = [r['best_strategy'] for r in ga_results['execution_results'] if 'error' not in r]
    aco_strategies = [r['best_strategy'] for r in aco_results['execution_results'] if 'error' not in r]
    
    # Contar número de paradas
    ga_pit_stops = [len(s) for s in ga_strategies]
    aco_pit_stops = [len(s) for s in aco_strategies]
    
    # Criar figura
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise das Estratégias Encontradas', fontsize=16, fontweight='bold')
    
    # 1. Distribuição de número de paradas
    ax1.hist(ga_pit_stops, alpha=0.7, label='GA', bins=range(min(ga_pit_stops), max(ga_pit_stops) + 2), 
             color='lightblue', edgecolor='black')
    ax1.hist(aco_pit_stops, alpha=0.7, label='ACO', bins=range(min(aco_pit_stops), max(aco_pit_stops) + 2), 
             color='lightcoral', edgecolor='black')
    ax1.set_title('Distribuição do Número de Paradas')
    ax1.set_xlabel('Número de Paradas')
    ax1.set_ylabel('Frequência')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Comparação de estatísticas de paradas
    stats_ga = ga_results['statistics']
    stats_aco = aco_results['statistics']
    
    metrics = ['mean_pit_stops', 'std_pit_stops', 'unique_strategies']
    metric_labels = ['Média de Paradas', 'Desvio Paradas', 'Estratégias Únicas']
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ga_values = [stats_ga.get(m, 0) for m in metrics]
    aco_values = [stats_aco.get(m, 0) for m in metrics]
    
    bars1 = ax2.bar(x - width/2, ga_values, width, label='GA', color='lightblue')
    bars2 = ax2.bar(x + width/2, aco_values, width, label='ACO', color='lightcoral')
    
    ax2.set_title('Estatísticas das Estratégias')
    ax2.set_ylabel('Valor')
    ax2.set_xticks(x)
    ax2.set_xticklabels(metric_labels)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
    
    # 3. Tempo de execução
    ga_exec_times = [r['execution_time'] for r in ga_results['execution_results'] if 'error' not in r]
    aco_exec_times = [r['execution_time'] for r in aco_results['execution_results'] if 'error' not in r]
    
    bp = ax3.boxplot([ga_exec_times, aco_exec_times], labels=['GA', 'ACO'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax3.set_title('Tempo de Execução dos Algoritmos')
    ax3.set_ylabel('Tempo (segundos)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Resumo das melhores estratégias
    best_ga = min(ga_results['execution_results'], key=lambda x: x['best_time'] if 'error' not in x else float('inf'))
    best_aco = min(aco_results['execution_results'], key=lambda x: x['best_time'] if 'error' not in x else float('inf'))
    
    algorithms = ['GA', 'ACO']
    best_times = [best_ga['best_time'], best_aco['best_time']]
    best_pit_stops = [len(best_ga['best_strategy']), len(best_aco['best_strategy'])]
    
    # Gráfico de barras para melhores tempos
    bars = ax4.bar(algorithms, best_times, color=['lightblue', 'lightcoral'], edgecolor='black')
    ax4.set_title('Melhores Estratégias Encontradas')
    ax4.set_ylabel('Tempo (segundos)')
    ax4.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, time_val, pit_stops in zip(bars, best_times, best_pit_stops):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{time_val:.2f}s\n({pit_stops} paradas)', ha='center', va='bottom')
    
    plt.tight_layout()
    return fig


def main():
    """
    Função principal para gerar visualizações estatísticas.
    """
    print("📊 Gerando Visualizações Estatísticas")
    print("=" * 40)
    
    # Procurar arquivo de resultados mais recente
    results_dir = 'results'
    if not os.path.exists(results_dir):
        print("❌ Diretório 'results' não encontrado")
        return
    
    # Listar arquivos de estudo estatístico
    stat_files = [f for f in os.listdir(results_dir) if f.startswith('statistical_study_') and f.endswith('.json')]
    
    if not stat_files:
        print("❌ Nenhum arquivo de estudo estatístico encontrado")
        print("Execute primeiro: python optimize_and_analyze.py")
        return
    
    # Usar o arquivo mais recente
    latest_file = max(stat_files, key=lambda x: os.path.getctime(os.path.join(results_dir, x)))
    filepath = os.path.join(results_dir, latest_file)
    
    print(f"📁 Carregando resultados de: {latest_file}")
    
    # Carregar resultados
    results = load_statistical_results(filepath)
    if not results:
        return
    
    # Criar visualizações
    print("🎨 Criando visualizações...")
    
    # 1. Comparação de performance
    fig1 = plot_performance_comparison(results)
    if fig1:
        fig1.savefig('results/performance_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ Gráfico de performance salvo")
    
    # 2. Testes estatísticos
    fig2 = plot_statistical_tests(results)
    if fig2:
        fig2.savefig('results/statistical_tests.png', dpi=300, bbox_inches='tight')
        print("✅ Gráfico de testes estatísticos salvo")
    
    # 3. Análise de estratégias
    fig3 = plot_strategy_analysis(results)
    if fig3:
        fig3.savefig('results/strategy_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Gráfico de análise de estratégias salvo")
    
    print("\n✅ Todas as visualizações foram salvas em: results/")
    print("📊 Arquivos gerados:")
    print("   - performance_comparison.png")
    print("   - statistical_tests.png")
    print("   - strategy_analysis.png")


if __name__ == "__main__":
    main() 