from typing import Dict
import pandas as pd
import importlib.util
import sys
import os

# Importar el módulo 6.Strategy usando importlib
_module_path = os.path.join(os.path.dirname(__file__), '6.Strategy.py')
_spec = importlib.util.spec_from_file_location("strategy_module", _module_path)
_strategy_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_strategy_module)

AnalysisStrategy = _strategy_module.AnalysisStrategy
RollingWindowStrategy = _strategy_module.RollingWindowStrategy
ForceBruteStrategy = _strategy_module.ForceBruteStrategy
CumulativeSumsStrategy = _strategy_module.CumulativeSumsStrategy
MaxSingleDayStrategy = _strategy_module.MaxSingleDayStrategy

# ============================================================================
# FACTORY METHOD PATTERN: Creación de Estrategias en Tiempo de Ejecución
# ============================================================================

class AnalysisStrategyFactory:
    """
    Factory que crea instancias de estrategias de análisis en tiempo de ejecución.
    
    Permite seleccionar estrategias por:
    - Nombre específico
    - Preferencia de rendimiento (fastest, balanced, educational)
    - Características del dataset (automatic)
    """
    
    # Registro de estrategias disponibles
    _strategies = {
        'rolling': RollingWindowStrategy,
        'force_brute': ForceBruteStrategy,
        'cumulative': CumulativeSumsStrategy,
        'max_day': MaxSingleDayStrategy,  # Nueva estrategia agregada
    }
    
    # Alias para facilitar selección
    _aliases = {
        'rolling_window': 'rolling',
        'brute': 'force_brute',
        'brute_force': 'force_brute',
        'cumulative_sums': 'cumulative',
        'sumas': 'cumulative',
        
        # Preferencias de rendimiento
        'fastest': 'rolling',
        'rapido': 'rolling',
        'production': 'rolling',
        'produccion': 'rolling',
        
        'balanced': 'cumulative',
        'balanceado': 'cumulative',
        'moderate': 'cumulative',
        
        'educational': 'force_brute',
        'educativo': 'force_brute',
        'learning': 'force_brute',
        'simple': 'force_brute',
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str) -> AnalysisStrategy:
        """
        Crea una instancia de estrategia basada en el nombre.
        
        Args:
            strategy_name: Nombre de la estrategia o alias
            
        Returns:
            Instancia de la estrategia solicitada
            
        Raises:
            ValueError: Si el nombre de estrategia no es válido
        """
        # Normalizar el nombre
        name = strategy_name.lower().strip()
        
        # Resolver alias
        if name in cls._aliases:
            name = cls._aliases[name]
        
        # Obtener la clase de estrategia
        strategy_class = cls._strategies.get(name)
        
        if strategy_class is None:
            available = list(cls._strategies.keys()) + list(cls._aliases.keys())
            raise ValueError(
                f"Estrategia '{strategy_name}' no encontrada. "
                f"Estrategias disponibles: {', '.join(available)}"
            )
        
        return strategy_class()
    
    @classmethod
    def create_automatic(cls, data: pd.DataFrame, threshold_size: int = 1000) -> AnalysisStrategy:
        """
        Selecciona automáticamente la estrategia más apropiada según el tamaño del dataset.
        
        Args:
            data: DataFrame a analizar
            threshold_size: Umbral para considerar dataset "grande"
            
        Returns:
            Instancia de la estrategia recomendada
        """
        dataset_size = len(data)
        
        if dataset_size < threshold_size:
            # Para datasets pequeños, usar fuerza bruta es aceptable y educativo
            return cls.create_strategy('educational')
        else:
            # Para datasets grandes, usar la estrategia más rápida
            return cls.create_strategy('fastest')
    
    @classmethod
    def get_all_strategies(cls) -> Dict[str, AnalysisStrategy]:
        """
        Retorna un diccionario con todas las estrategias disponibles.
        
        Returns:
            Dict con nombre -> instancia de estrategia
        """
        return {name: strategy_class() for name, strategy_class in cls._strategies.items()}
    
    @classmethod
    def list_available_strategies(cls) -> None:
        """Imprime información sobre todas las estrategias disponibles."""
        print("=" * 80)
        print("ESTRATEGIAS DE ANÁLISIS DISPONIBLES")
        print("=" * 80)
        
        for name, strategy_class in cls._strategies.items():
            strategy = strategy_class()
            info = strategy.get_strategy_info()
            
            print(f"\n📊 {info['nombre']} ('{name}')")
            print(f"   Descripción: {info['descripcion']}")
            print(f"   Complejidad: {info['complejidad']}")
            print(f"   Ventajas: {info['ventajas']}")
            print(f"   Uso recomendado: {info['uso_recomendado']}")
        
        print("\n" + "=" * 80)
        print("ALIASES Y PREFERENCIAS")
        print("=" * 80)
        print("\nPreferencias de Rendimiento:")
        print("  • 'fastest' / 'rapido' / 'production' → Rolling Window")
        print("  • 'balanced' / 'balanceado' / 'moderate' → Sumas Acumuladas")
        print("  • 'educational' / 'educativo' / 'simple' → Fuerza Bruta")
        print("\nModo Automático:")
        print("  • Usa create_automatic() para selección automática según tamaño del dataset")
        print("=" * 80)