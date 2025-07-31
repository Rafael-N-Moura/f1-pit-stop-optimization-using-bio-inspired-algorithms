import fastf1
import pandas as pd
import numpy as np
from typing import Optional


class DataHandler:
    """
    Classe responsável por buscar e preparar os dados de uma corrida de F1.
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        """
        Inicializa o DataHandler com configuração de cache.
        
        Args:
            cache_dir: Diretório para armazenar o cache dos dados
        """
        # Configurar o cache do FastF1
        fastf1.Cache.enable_cache(cache_dir)
        self.cache_dir = cache_dir
    
    def get_race_data(self, year: int, race_name: str, driver_code: str) -> pd.DataFrame:
        """
        Obtém e processa os dados de uma corrida específica para um piloto.
        
        Args:
            year: Ano da corrida
            race_name: Nome da corrida (ex: 'Monaco Grand Prix')
            driver_code: Código do piloto (ex: 'HAM', 'VER')
            
        Returns:
            DataFrame processado com os dados da corrida
        """
        try:
            # Carregar a sessão da corrida
            session = fastf1.get_session(year, race_name, 'R')
            session.load()
            
            # Filtrar dados para o piloto específico
            driver_data = session.laps.pick_driver(driver_code)
            
            # Pré-processamento dos dados
            processed_data = self._preprocess_data(driver_data)
            
            return processed_data
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return pd.DataFrame()
    
    def _preprocess_data(self, driver_data: pd.DataFrame) -> pd.DataFrame:
        """
        Pré-processa os dados do piloto.
        
        Args:
            driver_data: DataFrame com dados brutos do piloto
            
        Returns:
            DataFrame processado
        """
        if driver_data.empty:
            return pd.DataFrame()
        
        # Converter LapTime para segundos
        driver_data['LapTimeSeconds'] = driver_data['LapTime'].dt.total_seconds()
        
        # Filtrar apenas voltas precisas (remover entrada/saída dos boxes e Safety Car)
        accurate_laps = driver_data[driver_data['IsAccurate'] == True].copy()
        
        # Remover voltas com valores nulos ou inválidos
        accurate_laps = accurate_laps.dropna(subset=['LapTimeSeconds', 'TyreLife', 'Compound'])
        
        # Garantir que temos dados suficientes
        if len(accurate_laps) < 10:
            print("Aviso: Poucos dados precisos encontrados para análise")
            return accurate_laps
        
        return accurate_laps
    
    def get_available_compounds(self, race_data: pd.DataFrame) -> list:
        """
        Obtém a lista de compostos de pneu disponíveis nos dados.
        
        Args:
            race_data: DataFrame com dados da corrida
            
        Returns:
            Lista de compostos únicos
        """
        if race_data.empty:
            return []
        
        compounds = race_data['Compound'].unique().tolist()
        return [c for c in compounds if pd.notna(c)]
    
    def get_race_info(self, race_data: pd.DataFrame) -> dict:
        """
        Obtém informações básicas sobre a corrida.
        
        Args:
            race_data: DataFrame com dados da corrida
            
        Returns:
            Dicionário com informações da corrida
        """
        if race_data.empty:
            return {}
        
        info = {
            'total_laps': len(race_data),
            'compounds_used': self.get_available_compounds(race_data),
            'avg_lap_time': race_data['LapTimeSeconds'].mean(),
            'best_lap_time': race_data['LapTimeSeconds'].min(),
            'worst_lap_time': race_data['LapTimeSeconds'].max()
        }
        
        return info 