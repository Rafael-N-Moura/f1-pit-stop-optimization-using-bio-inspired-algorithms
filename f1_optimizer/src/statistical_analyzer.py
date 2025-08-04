import numpy as np
import pandas as pd
import json
import time
from typing import Dict, List, Tuple, Any
from scipy import stats
from .data_handler import DataHandler
from .race_simulator import RaceSimulator
from .genetic_algorithm import GeneticAlgorithm
from .ant_colony import AntColonyOptimizer


class StatisticalAnalyzer:
    """
    Classe para análise estatística robusta dos algoritmos GA e ACO.
    """
    
    def __init__(self):
        """
        Inicializa o analisador estatístico.
        """
        self.results = {}
        self.statistical_tests = {}
    
    def run_multiple_executions(self, algorithm_type: str, params: Dict, 
                               scenario: Dict, n_executions: int = 30) -> Dict:
        """
        Executa algoritmo múltiplas vezes para análise estatística.
        
        Args:
            algorithm_type: 'GA' ou 'ACO'
            params: Parâmetros do algoritmo
            scenario: Dicionário com cenário
            n_executions: Número de execuções
            
        Returns:
            Dicionário com resultados estatísticos
        """
        print(f"📊 Executando {n_executions} execuções do {algorithm_type}...")
        
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
        
        # Lista para armazenar resultados
        execution_results = []
        
        for execution in range(n_executions):
            print(f"  Execução {execution + 1}/{n_executions}...")
            
            start_time = time.time()
            
            try:
                if algorithm_type == 'GA':
                    algorithm = GeneticAlgorithm(simulator, **params)
                    best_individual = algorithm.run()
                    execution_time = time.time() - start_time
                    
                    result = {
                        'execution_id': execution,
                        'best_time': 1 / best_individual.fitness if best_individual.fitness > 0 else float('inf'),
                        'best_strategy': best_individual.chromosome,
                        'execution_time': execution_time,
                        'fitness_history': algorithm.get_fitness_history(),
                        'convergence_generation': np.argmax(algorithm.get_fitness_history()),
                        'final_fitness': best_individual.fitness
                    }
                    
                elif algorithm_type == 'ACO':
                    algorithm = AntColonyOptimizer(simulator, **params)
                    best_ant = algorithm.run()
                    execution_time = time.time() - start_time
                    
                    result = {
                        'execution_id': execution,
                        'best_time': best_ant.total_time,
                        'best_strategy': best_ant.strategy,
                        'execution_time': execution_time,
                        'fitness_history': algorithm.get_fitness_history(),
                        'convergence_iteration': np.argmax(algorithm.get_fitness_history()),
                        'final_fitness': 1 / best_ant.total_time if best_ant.total_time > 0 else 0
                    }
                    
                else:
                    raise ValueError(f"Algoritmo não suportado: {algorithm_type}")
                
                execution_results.append(result)
                
            except Exception as e:
                print(f"⚠️ Erro na execução {execution + 1}: {e}")
                execution_results.append({
                    'execution_id': execution,
                    'best_time': float('inf'),
                    'best_strategy': [],
                    'execution_time': 0,
                    'error': str(e)
                })
        
        # Calcular estatísticas
        statistics = self._calculate_statistics(execution_results, algorithm_type)
        
        # Armazenar resultados
        self.results[algorithm_type] = {
            'execution_results': execution_results,
            'statistics': statistics,
            'params': params,
            'scenario': scenario
        }
        
        print(f"✅ {algorithm_type} concluído! Tempo médio: {statistics['mean_time']:.2f}s")
        
        return statistics
    
    def _calculate_statistics(self, execution_results: List[Dict], algorithm_type: str) -> Dict:
        """
        Calcula estatísticas dos resultados de execução.
        
        Args:
            execution_results: Lista com resultados de execuções
            algorithm_type: Tipo do algoritmo
            
        Returns:
            Dicionário com estatísticas calculadas
        """
        # Filtrar execuções com erro
        valid_results = [r for r in execution_results if 'error' not in r]
        
        if not valid_results:
            return {'error': 'Nenhuma execução válida encontrada'}
        
        # Extrair tempos
        times = [r['best_time'] for r in valid_results]
        execution_times = [r['execution_time'] for r in valid_results]
        
        # Estatísticas básicas
        statistics = {
            'n_executions': len(valid_results),
            'n_errors': len(execution_results) - len(valid_results),
            'mean_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times),
            'cv_time': (np.std(times) / np.mean(times)) * 100 if np.mean(times) > 0 else 0,
            'mean_execution_time': np.mean(execution_times),
            'std_execution_time': np.std(execution_times),
            'median_time': np.median(times),
            'q25_time': np.percentile(times, 25),
            'q75_time': np.percentile(times, 75)
        }
        
        # Análise de estratégias
        strategies = [r['best_strategy'] for r in valid_results]
        n_pit_stops = [len(s) for s in strategies]
        
        statistics.update({
            'mean_pit_stops': np.mean(n_pit_stops),
            'std_pit_stops': np.std(n_pit_stops),
            'min_pit_stops': np.min(n_pit_stops),
            'max_pit_stops': np.max(n_pit_stops),
            'unique_strategies': len(set(str(s) for s in strategies))
        })
        
        # Análise de convergência
        if algorithm_type == 'GA':
            convergence_gens = [r['convergence_generation'] for r in valid_results]
            statistics['mean_convergence_gen'] = np.mean(convergence_gens)
            statistics['std_convergence_gen'] = np.std(convergence_gens)
        else:  # ACO
            convergence_iters = [r['convergence_iteration'] for r in valid_results]
            statistics['mean_convergence_iter'] = np.mean(convergence_iters)
            statistics['std_convergence_iter'] = np.std(convergence_iters)
        
        return statistics
    
    def perform_statistical_tests(self, ga_results: Dict, aco_results: Dict) -> Dict:
        """
        Realiza testes estatísticos para comparar GA e ACO.
        
        Args:
            ga_results: Resultados do GA
            aco_results: Resultados do ACO
            
        Returns:
            Dicionário com resultados dos testes estatísticos
        """
        print("🔬 Realizando testes estatísticos...")
        
        # Extrair tempos
        ga_times = [r['best_time'] for r in ga_results['execution_results'] if 'error' not in r]
        aco_times = [r['best_time'] for r in aco_results['execution_results'] if 'error' not in r]
        
        if not ga_times or not aco_times:
            return {'error': 'Dados insuficientes para testes estatísticos'}
        
        # Teste de normalidade (Shapiro-Wilk)
        ga_normal = stats.shapiro(ga_times)
        aco_normal = stats.shapiro(aco_times)
        
        # Teste t-Student (paramétrico)
        t_test = stats.ttest_ind(ga_times, aco_times)
        
        # Teste de Wilcoxon (não paramétrico)
        wilcoxon_test = stats.wilcoxon(ga_times, aco_times)
        
        # Teste de Mann-Whitney U (não paramétrico para amostras independentes)
        mannwhitney_test = stats.mannwhitneyu(ga_times, aco_times, alternative='two-sided')
        
        # Calcular tamanho do efeito (Cohen's d)
        pooled_std = np.sqrt(((len(ga_times) - 1) * np.var(ga_times) + 
                             (len(aco_times) - 1) * np.var(aco_times)) / 
                            (len(ga_times) + len(aco_times) - 2))
        cohens_d = (np.mean(ga_times) - np.mean(aco_times)) / pooled_std
        
        # Determinar qual algoritmo é melhor
        ga_mean = np.mean(ga_times)
        aco_mean = np.mean(aco_times)
        
        if ga_mean < aco_mean:
            better_algorithm = 'GA'
            improvement = ((aco_mean - ga_mean) / aco_mean) * 100
        else:
            better_algorithm = 'ACO'
            improvement = ((ga_mean - aco_mean) / ga_mean) * 100
        
        tests_results = {
            'normality_tests': {
                'ga_shapiro': {'statistic': ga_normal.statistic, 'p_value': ga_normal.pvalue},
                'aco_shapiro': {'statistic': aco_normal.statistic, 'p_value': aco_normal.pvalue}
            },
            'parametric_tests': {
                't_test': {'statistic': t_test.statistic, 'p_value': t_test.pvalue}
            },
            'non_parametric_tests': {
                'wilcoxon': {'statistic': wilcoxon_test.statistic, 'p_value': wilcoxon_test.pvalue},
                'mannwhitney': {'statistic': mannwhitney_test.statistic, 'p_value': mannwhitney_test.pvalue}
            },
            'effect_size': {
                'cohens_d': cohens_d,
                'interpretation': self._interpret_cohens_d(cohens_d)
            },
            'comparison': {
                'ga_mean': ga_mean,
                'aco_mean': aco_mean,
                'better_algorithm': better_algorithm,
                'improvement_percent': improvement,
                'significant_difference': t_test.pvalue < 0.05
            }
        }
        
        self.statistical_tests = tests_results
        
        print(f"✅ Testes estatísticos concluídos!")
        print(f"   Melhor algoritmo: {better_algorithm}")
        print(f"   Diferença significativa: {'Sim' if t_test.pvalue < 0.05 else 'Não'}")
        print(f"   Tamanho do efeito: {cohens_d:.3f} ({self._interpret_cohens_d(cohens_d)})")
        
        return tests_results
    
    def _interpret_cohens_d(self, cohens_d: float) -> str:
        """
        Interpreta o tamanho do efeito de Cohen's d.
        
        Args:
            cohens_d: Valor de Cohen's d
            
        Returns:
            Interpretação do tamanho do efeito
        """
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "Efeito pequeno"
        elif abs_d < 0.5:
            return "Efeito médio"
        elif abs_d < 0.8:
            return "Efeito grande"
        else:
            return "Efeito muito grande"
    
    def generate_report(self, results: Dict = None) -> Dict:
        """
        Gera relatório estatístico completo.
        
        Args:
            results: Resultados opcionais (usa self.results se None)
            
        Returns:
            Dicionário com relatório completo
        """
        if results is None:
            results = self.results
        
        if not results:
            return {'error': 'Nenhum resultado disponível'}
        
        report = {
            'summary': {},
            'detailed_results': {},
            'statistical_tests': self.statistical_tests,
            'recommendations': {}
        }
        
        # Resumo executivo
        if 'GA' in results and 'ACO' in results:
            ga_stats = results['GA']['statistics']
            aco_stats = results['ACO']['statistics']
            
            # Determinar melhor algoritmo
            if ga_stats['mean_time'] < aco_stats['mean_time']:
                better_algorithm = 'GA'
                improvement = ((aco_stats['mean_time'] - ga_stats['mean_time']) / aco_stats['mean_time']) * 100
            else:
                better_algorithm = 'ACO'
                improvement = ((ga_stats['mean_time'] - aco_stats['mean_time']) / ga_stats['mean_time']) * 100
            
            report['summary'] = {
                'better_algorithm': better_algorithm,
                'improvement_percent': improvement,
                'ga_performance': {
                    'mean_time': ga_stats['mean_time'],
                    'std_time': ga_stats['std_time'],
                    'cv_time': ga_stats['cv_time']
                },
                'aco_performance': {
                    'mean_time': aco_stats['mean_time'],
                    'std_time': aco_stats['std_time'],
                    'cv_time': aco_stats['cv_time']
                }
            }
        
        # Resultados detalhados
        for algorithm, data in results.items():
            report['detailed_results'][algorithm] = {
                'statistics': data['statistics'],
                'params': data['params'],
                'scenario': data['scenario']
            }
        
        # Recomendações
        if 'GA' in results and 'ACO' in results:
            ga_stats = results['GA']['statistics']
            aco_stats = results['ACO']['statistics']
            
            recommendations = []
            
            # Recomendação baseada na qualidade
            if ga_stats['mean_time'] < aco_stats['mean_time']:
                recommendations.append("GA é recomendado para melhor qualidade de solução")
            else:
                recommendations.append("ACO é recomendado para melhor qualidade de solução")
            
            # Recomendação baseada na consistência
            if ga_stats['cv_time'] < aco_stats['cv_time']:
                recommendations.append("GA é mais consistente (menor variabilidade)")
            else:
                recommendations.append("ACO é mais consistente (menor variabilidade)")
            
            # Recomendação baseada na velocidade
            if ga_stats['mean_execution_time'] < aco_stats['mean_execution_time']:
                recommendations.append("GA é mais rápido para executar")
            else:
                recommendations.append("ACO é mais rápido para executar")
            
            report['recommendations'] = recommendations
        
        return report
    
    def save_results(self, filename: str):
        """
        Salva resultados em arquivo JSON.
        
        Args:
            filename: Nome do arquivo para salvar
        """
        results_data = {
            'results': self.results,
            'statistical_tests': self.statistical_tests,
            'report': self.generate_report()
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"💾 Resultados estatísticos salvos em: {filename}")


def run_statistical_study(scenario: Dict, ga_params: Dict, aco_params: Dict, 
                         n_executions: int = 30) -> Dict:
    """
    Executa estudo estatístico completo.
    
    Args:
        scenario: Dicionário com cenário
        ga_params: Parâmetros otimizados do GA
        aco_params: Parâmetros otimizados do ACO
        n_executions: Número de execuções por algoritmo
        
    Returns:
        Dicionário com resultados do estudo
    """
    print("📊 Iniciando estudo estatístico completo...")
    
    analyzer = StatisticalAnalyzer()
    
    # Executar GA múltiplas vezes
    print("\n🔬 Executando Algoritmo Genético...")
    ga_statistics = analyzer.run_multiple_executions('GA', ga_params, scenario, n_executions)
    
    # Executar ACO múltiplas vezes
    print("\n🔬 Executando Algoritmo ACO...")
    aco_statistics = analyzer.run_multiple_executions('ACO', aco_params, scenario, n_executions)
    
    # Realizar testes estatísticos
    print("\n🔬 Realizando testes estatísticos...")
    statistical_tests = analyzer.perform_statistical_tests(
        analyzer.results['GA'], 
        analyzer.results['ACO']
    )
    
    # Gerar relatório
    report = analyzer.generate_report()
    
    # Salvar resultados
    filename = f"results/statistical_study_{scenario['year']}_{scenario['race_name'].replace(' ', '_')}_{scenario['driver_code']}.json"
    analyzer.save_results(filename)
    
    print(f"\n✅ Estudo estatístico concluído!")
    print(f"   Relatório salvo em: {filename}")
    
    return report 