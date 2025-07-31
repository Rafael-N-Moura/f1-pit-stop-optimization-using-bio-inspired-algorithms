import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple, Dict, Optional


class RaceSimulator:
    """
    Simulador de corrida que calcula o tempo total para uma estratégia específica.
    """
    
    def __init__(self, race_data: pd.DataFrame, pit_stop_time: float = 25.0):
        """
        Inicializa o simulador com dados da corrida.
        
        Args:
            race_data: DataFrame com dados processados da corrida
            pit_stop_time: Tempo de pit stop em segundos (padrão: 25s)
        """
        self.race_data = race_data
        self.pit_stop_time = pit_stop_time
        self.total_laps = len(race_data)
        
        # Calcular parâmetros do modelo
        self._calculate_model_parameters()
    
    def _calculate_model_parameters(self):
        """
        Calcula os parâmetros do modelo de tempo de volta.
        """
        # Efeito do combustível (padrão da indústria)
        self.fuel_effect_coeff = 0.035  # segundos por volta
        
        # Inicializar dicionários para coeficientes
        self.degradation_coeffs = {}
        self.alpha_coeffs = {}
        
        # Obter compostos únicos
        compounds = self.race_data['Compound'].unique()
        
        # Definir composto de referência (HARD como baseline)
        reference_compound = 'HARD' if 'HARD' in compounds else compounds[0]
        
        # Calcular parâmetros para cada composto
        compound_intercepts = {}
        
        for compound in compounds:
            if pd.isna(compound):
                continue
                
            # Filtrar dados para este composto
            compound_data = self.race_data[self.race_data['Compound'] == compound].copy()
            
            if len(compound_data) < 3:
                continue
            
            # Corrigir tempos para efeito do combustível
            compound_data['CorrectedTime'] = (
                compound_data['LapTimeSeconds'] + 
                (self.fuel_effect_coeff * compound_data['LapNumber'])
            )
            
            # Preparar dados para regressão linear
            X = compound_data[['TyreLife']].values
            y = compound_data['CorrectedTime'].values
            
            # Ajustar regressão linear
            model = LinearRegression()
            model.fit(X, y)
            
            # Armazenar coeficientes
            self.degradation_coeffs[compound] = model.coef_[0]  # Penalidade por volta
            compound_intercepts[compound] = model.intercept_
        
        # Calcular deltas de performance (alpha_coeffs)
        reference_intercept = compound_intercepts.get(reference_compound, 0)
        
        for compound in compounds:
            if compound in compound_intercepts:
                self.alpha_coeffs[compound] = reference_intercept - compound_intercepts[compound]
            else:
                self.alpha_coeffs[compound] = 0
        
        # Tempo de volta base
        self.T_base = reference_intercept
        
        # Se não temos dados suficientes, usar valores padrão
        if not self.degradation_coeffs:
            self._set_default_parameters()
        
        # Validar e corrigir parâmetros irrealistas
        self._validate_and_correct_parameters()
    
    def _set_default_parameters(self):
        """
        Define parâmetros padrão quando não há dados suficientes.
        """
        self.degradation_coeffs = {
            'SOFT': 0.15,      # Degradação mais rápida
            'MEDIUM': 0.08,    # Degradação moderada
            'HARD': 0.03,      # Degradação lenta
            'INTERMEDIATE': 0.05  # Degradação baixa (pneu de chuva)
        }
        
        self.alpha_coeffs = {
            'SOFT': -1.5,      # Mais rápido
            'MEDIUM': 0.0,     # Neutro
            'HARD': 1.5,       # Mais lento
            'INTERMEDIATE': -0.5  # Ligeiramente mais rápido
        }
        
        self.T_base = 90.0  # Tempo base de volta
    
    def _validate_and_correct_parameters(self):
        """
        Valida e corrige parâmetros irrealistas.
        """
        # Verificar coeficientes de degradação negativos ou extremos
        for compound, coeff in self.degradation_coeffs.items():
            if coeff < 0 or coeff > 0.5:  # Valores irrealistas
                print(f"Aviso: Coeficiente de degradação irrealista para {compound}: {coeff}")
                print(f"Usando valor padrão para {compound}")
                if compound == 'SOFT':
                    self.degradation_coeffs[compound] = 0.15
                elif compound == 'MEDIUM':
                    self.degradation_coeffs[compound] = 0.08
                elif compound == 'HARD':
                    self.degradation_coeffs[compound] = 0.03
                elif compound == 'INTERMEDIATE':
                    self.degradation_coeffs[compound] = 0.05
                else:
                    self.degradation_coeffs[compound] = 0.08  # Valor padrão
        
        # Verificar deltas de performance extremos
        for compound, alpha in self.alpha_coeffs.items():
            if abs(alpha) > 10:  # Valores extremos
                print(f"Aviso: Delta de performance extremo para {compound}: {alpha}")
                print(f"Usando valor padrão para {compound}")
                if compound == 'SOFT':
                    self.alpha_coeffs[compound] = -1.5
                elif compound == 'MEDIUM':
                    self.alpha_coeffs[compound] = 0.0
                elif compound == 'HARD':
                    self.alpha_coeffs[compound] = 1.5
                elif compound == 'INTERMEDIATE':
                    self.alpha_coeffs[compound] = -0.5
                else:
                    self.alpha_coeffs[compound] = 0.0  # Valor padrão
    
    def evaluate_strategy(self, strategy: List[Tuple[int, str]]) -> float:
        """
        Avalia uma estratégia de pit stop.
        
        Args:
            strategy: Lista de tuplas (volta_parada, composto_novo)
            
        Returns:
            Tempo total da corrida em segundos
        """
        if not strategy:
            # Estratégia sem paradas - usar composto inicial
            initial_compound = self.race_data['Compound'].iloc[0]
            return self._simulate_no_pit_strategy(initial_compound)
        
        # Ordenar estratégia por volta
        strategy = sorted(strategy, key=lambda x: x[0])
        
        # Penalização por excesso de paradas
        penalty = 0
        if len(strategy) > 3:
            penalty = (len(strategy) - 3) * 1000  # Penalização alta por excesso
        
        # Simular corrida
        total_time = 0
        current_lap = 1
        current_compound = self.race_data['Compound'].iloc[0]
        current_tyre_age = 0
        
        for i, (pit_lap, new_compound) in enumerate(strategy):
            # Simular voltas até a parada
            while current_lap < pit_lap and current_lap <= self.total_laps:
                lap_time = self._calculate_lap_time(
                    current_lap, current_compound, current_tyre_age
                )
                total_time += lap_time
                current_lap += 1
                current_tyre_age += 1
            
            # Adicionar tempo de pit stop (exceto na última parada)
            if i < len(strategy) - 1:
                total_time += self.pit_stop_time
            
            # Atualizar estado do pneu
            current_compound = new_compound
            current_tyre_age = 0
        
        # Simular voltas restantes
        while current_lap <= self.total_laps:
            lap_time = self._calculate_lap_time(
                current_lap, current_compound, current_tyre_age
            )
            total_time += lap_time
            current_lap += 1
            current_tyre_age += 1
        
        return total_time + penalty
    
    def _calculate_lap_time(self, lap_number: int, compound: str, tyre_age: int) -> float:
        """
        Calcula o tempo de uma volta específica.
        
        Args:
            lap_number: Número da volta
            compound: Composto do pneu
            tyre_age: Idade do pneu (voltas de uso)
            
        Returns:
            Tempo da volta em segundos
        """
        # Usar valores padrão se o composto não estiver nos dados
        degradation_coeff = self.degradation_coeffs.get(compound, 0.05)
        alpha_coeff = self.alpha_coeffs.get(compound, 0.0)
        
        # Fórmula do modelo
        lap_time = (
            self.T_base + 
            alpha_coeff + 
            (degradation_coeff * tyre_age) - 
            (self.fuel_effect_coeff * lap_number)
        )
        
        return max(lap_time, 60.0)  # Tempo mínimo de 60s
    
    def _simulate_no_pit_strategy(self, compound: str) -> float:
        """
        Simula uma estratégia sem paradas.
        
        Args:
            compound: Composto inicial
            
        Returns:
            Tempo total da corrida
        """
        total_time = 0
        
        for lap in range(1, self.total_laps + 1):
            lap_time = self._calculate_lap_time(lap, compound, lap - 1)
            total_time += lap_time
        
        return total_time
    
    def get_model_parameters(self) -> Dict:
        """
        Retorna os parâmetros do modelo para análise.
        
        Returns:
            Dicionário com parâmetros do modelo
        """
        return {
            'T_base': self.T_base,
            'fuel_effect_coeff': self.fuel_effect_coeff,
            'degradation_coeffs': self.degradation_coeffs,
            'alpha_coeffs': self.alpha_coeffs,
            'pit_stop_time': self.pit_stop_time,
            'total_laps': self.total_laps
        } 