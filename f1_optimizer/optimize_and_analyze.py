#!/usr/bin/env python3
"""
Script principal para otimização de parâmetros e análise estatística.
"""

import sys
import os
import json
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.parameter_optimizer import optimize_ga_parameters, optimize_aco_parameters
from src.statistical_analyzer import run_statistical_study


def create_results_directory():
    """
    Cria diretório de resultados se não existir.
    """
    if not os.path.exists('results'):
        os.makedirs('results')
        print("📁 Diretório 'results' criado")


def load_optimized_params(scenario):
    """
    Carrega parâmetros otimizados se existirem, senão otimiza.
    
    Args:
        scenario: Dicionário com cenário
        
    Returns:
        Tupla com parâmetros otimizados (ga_params, aco_params)
    """
    ga_filename = f"results/ga_optimization_{scenario['year']}_{scenario['race_name'].replace(' ', '_')}_{scenario['driver_code']}.json"
    aco_filename = f"results/aco_optimization_{scenario['year']}_{scenario['race_name'].replace(' ', '_')}_{scenario['driver_code']}.json"
    
    ga_params = None
    aco_params = None
    
    # Tentar carregar parâmetros otimizados do GA
    if os.path.exists(ga_filename):
        try:
            with open(ga_filename, 'r') as f:
                data = json.load(f)
                ga_params = data.get('best_params')
                print(f"✅ Parâmetros otimizados do GA carregados de: {ga_filename}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar parâmetros do GA: {e}")
    
    # Tentar carregar parâmetros otimizados do ACO
    if os.path.exists(aco_filename):
        try:
            with open(aco_filename, 'r') as f:
                data = json.load(f)
                aco_params = data.get('best_params')
                print(f"✅ Parâmetros otimizados do ACO carregados de: {aco_filename}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar parâmetros do ACO: {e}")
    
    # Otimizar se necessário
    if ga_params is None:
        print("\n🔧 Otimizando parâmetros do Algoritmo Genético...")
        ga_params = optimize_ga_parameters(scenario)
    
    if aco_params is None:
        print("\n🔧 Otimizando parâmetros do Algoritmo ACO...")
        aco_params = optimize_aco_parameters(scenario)
    
    return ga_params, aco_params


def main():
    """
    Função principal para executar otimização e análise estatística.
    """
    print("🎯 Iniciando Otimização de Parâmetros e Análise Estatística")
    print("=" * 60)
    
    # Criar diretório de resultados
    create_results_directory()
    
    # Definir cenário de teste
    scenario = {
        'year': 2024,
        'race_name': 'Spain Grand Prix',
        'driver_code': 'HAM'
    }
    
    print(f"📊 Cenário: {scenario['year']} {scenario['race_name']} - {scenario['driver_code']}")
    print()
    
    # Carregar ou otimizar parâmetros
    ga_params, aco_params = load_optimized_params(scenario)
    
    if not ga_params or not aco_params:
        print("❌ Erro: Não foi possível obter parâmetros otimizados")
        return
    
    print("\n📋 Parâmetros Otimizados:")
    print(f"   GA: {ga_params}")
    print(f"   ACO: {aco_params}")
    print()
    
    # Executar estudo estatístico
    print("📈 Iniciando Análise Estatística...")
    print("=" * 40)
    
    try:
        # Executar com 30 execuções por algoritmo (pode ser reduzido para testes)
        n_executions = 30  # Reduzir para 10-15 se demorar muito
        
        report = run_statistical_study(scenario, ga_params, aco_params, n_executions)
        
        # Exibir resumo dos resultados
        if 'summary' in report:
            summary = report['summary']
            print("\n📊 RESUMO DOS RESULTADOS")
            print("=" * 40)
            print(f"🎯 Melhor Algoritmo: {summary['better_algorithm']}")
            print(f"📈 Melhoria: {summary['improvement_percent']:.2f}%")
            print()
            print("📊 Performance GA:")
            print(f"   Tempo médio: {summary['ga_performance']['mean_time']:.2f}s")
            print(f"   Desvio padrão: {summary['ga_performance']['std_time']:.2f}s")
            print(f"   CV: {summary['ga_performance']['cv_time']:.2f}%")
            print()
            print("📊 Performance ACO:")
            print(f"   Tempo médio: {summary['aco_performance']['mean_time']:.2f}s")
            print(f"   Desvio padrão: {summary['aco_performance']['std_time']:.2f}s")
            print(f"   CV: {summary['aco_performance']['cv_time']:.2f}%")
        
        if 'recommendations' in report:
            print("\n💡 RECOMENDAÇÕES")
            print("=" * 20)
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
        
        if 'statistical_tests' in report:
            tests = report['statistical_tests']
            if 'comparison' in tests:
                comp = tests['comparison']
                print(f"\n🔬 TESTES ESTATÍSTICOS")
                print("=" * 30)
                print(f"Diferença significativa: {'Sim' if comp['significant_difference'] else 'Não'}")
                if 'effect_size' in tests:
                    effect = tests['effect_size']
                    print(f"Tamanho do efeito: {effect['cohens_d']:.3f} ({effect['interpretation']})")
        
        print(f"\n✅ Análise concluída com sucesso!")
        print(f"📁 Resultados salvos em: results/")
        
    except Exception as e:
        print(f"❌ Erro durante análise estatística: {e}")
        import traceback
        traceback.print_exc()


def run_quick_test():
    """
    Executa teste rápido com menos execuções para verificação.
    """
    print("🧪 Executando Teste Rápido...")
    
    scenario = {
        'year': 2024,
        'race_name': 'Spain Grand Prix',
        'driver_code': 'HAM'
    }
    
    # Usar parâmetros padrão para teste rápido
    ga_params = {
        'population_size': 30,
        'generations': 50,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8,
        'elitism_size': 3
    }
    
    aco_params = {
        'num_ants': 20,
        'iterations': 30,
        'evaporation_rate': 0.1,
        'alpha': 1.0,
        'beta': 2.0
    }
    
    # Executar com apenas 5 execuções por algoritmo
    report = run_statistical_study(scenario, ga_params, aco_params, n_executions=5)
    
    print("✅ Teste rápido concluído!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Otimização de Parâmetros e Análise Estatística')
    parser.add_argument('--quick', action='store_true', help='Executar teste rápido')
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_test()
    else:
        main() 