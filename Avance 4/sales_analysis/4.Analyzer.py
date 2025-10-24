from typing import Dict, Any
import pandas as pd
import timeit
import statistics
import importlib.util
import sys
import os

# Importar el módulo 6.Strategy usando importlib
_strategy_path = os.path.join(os.path.dirname(__file__), '6.Strategy.py')
_spec1 = importlib.util.spec_from_file_location("strategy_module", _strategy_path)
_strategy_module = importlib.util.module_from_spec(_spec1)
_spec1.loader.exec_module(_strategy_module)

AnalysisStrategy = _strategy_module.AnalysisStrategy
RollingWindowStrategy = _strategy_module.RollingWindowStrategy

# Importar el módulo 5.Factory usando importlib
_factory_path = os.path.join(os.path.dirname(__file__), '5.Factory.py')
_spec2 = importlib.util.spec_from_file_location("factory_module", _factory_path)
_factory_module = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(_factory_module)

AnalysisStrategyFactory = _factory_module.AnalysisStrategyFactory

# ============================================================================
# CONTEXT CLASS: Analizador de Ventas
# ============================================================================

class SalesAnalyzer:
    """
    Clase contexto que utiliza una estrategia para realizar análisis de ventas.
    
    Esta clase encapsula la lógica de preparación de datos y coordinación
    del análisis, delegando el algoritmo específico a la estrategia elegida.
    """
    
    def __init__(self, strategy: AnalysisStrategy = None):
        """
        Inicializa el analizador con una estrategia específica.
        
        Args:
            strategy: Instancia de estrategia a usar. Si es None, usa rolling por defecto
        """
        self._strategy = strategy if strategy is not None else RollingWindowStrategy()
    
    def set_strategy(self, strategy: AnalysisStrategy) -> None:
        """
        Cambia la estrategia en tiempo de ejecución.
        
        Args:
            strategy: Nueva estrategia a usar
        """
        self._strategy = strategy
    
    def get_current_strategy_info(self) -> Dict[str, str]:
        """Retorna información sobre la estrategia actual."""
        return self._strategy.get_strategy_info()
    
    def analyze(self, data: pd.DataFrame, window_size: int = 5) -> Dict[str, Any]:
        """
        Ejecuta el análisis usando la estrategia actual.
        
        Args:
            data: DataFrame con datos de ventas
            window_size: Tamaño de la ventana (días consecutivos)
            
        Returns:
            Dict con resultados del análisis
        """
        # Validar datos
        if data is None or len(data) == 0:
            raise ValueError("El DataFrame no puede estar vacío")
        
        if window_size < 1 or window_size > len(data):
            raise ValueError(f"window_size debe estar entre 1 y {len(data)}")
        
        # Ejecutar estrategia
        return self._strategy.find_best_period(data, window_size)
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """
        Imprime los resultados del análisis de forma formateada.
        
        Args:
            results: Diccionario con resultados del análisis
        """
        print("\n" + "=" * 80)
        print(f"🎯 RESULTADOS DEL ANÁLISIS - Estrategia: {results['estrategia']}")
        print("=" * 80)
        
        print(f"\n📅 Periodo encontrado: {results['dias']} días consecutivos")
        print(f"   Fecha inicio: {results['fecha_inicio'].strftime('%Y-%m-%d')}")
        print(f"   Fecha fin: {results['fecha_fin'].strftime('%Y-%m-%d')}")
        print(f"   Total de ventas: ${results['total_ventas']:,.2f}")
        
        print("\n📊 Desglose por día:")
        print("-" * 80)
        for idx, row in results['periodo'].iterrows():
            print(f"   {row['Fecha'].strftime('%Y-%m-%d')}: ${row['TotalVentas']:,.2f}")
        
        print("=" * 80)
    
    def benchmark_strategies(self, data: pd.DataFrame, window_size: int = 5, 
                           repetitions: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Compara el rendimiento de todas las estrategias disponibles.
        
        Args:
            data: DataFrame con datos de ventas
            window_size: Tamaño de la ventana
            repetitions: Número de repeticiones para el benchmark
            
        Returns:
            Dict con resultados de rendimiento de cada estrategia
        """
        print("\n" + "=" * 80)
        print(f"⏱️  BENCHMARK DE ESTRATEGIAS - {repetitions} repeticiones")
        print("=" * 80)
        
        all_strategies = AnalysisStrategyFactory.get_all_strategies()
        benchmark_results = {}
        
        for name, strategy in all_strategies.items():
            self.set_strategy(strategy)
            
            # Medir tiempo de ejecución
            times = timeit.repeat(
                lambda: self.analyze(data, window_size),
                number=1,
                repeat=repetitions
            )
            
            info = strategy.get_strategy_info()
            
            benchmark_results[name] = {
                'nombre': info['nombre'],
                'promedio_ms': statistics.mean(times) * 1000,
                'minimo_ms': min(times) * 1000,
                'maximo_ms': max(times) * 1000,
                'stdev_ms': statistics.stdev(times) * 1000,
                'cv_percent': (statistics.stdev(times) / statistics.mean(times)) * 100
            }
        
        # Imprimir resultados
        print(f"\n{'Estrategia':<20} {'Promedio (ms)':<15} {'Mínimo (ms)':<15} {'Máximo (ms)':<15}")
        print("-" * 65)
        
        for name, results in benchmark_results.items():
            print(f"{results['nombre']:<20} {results['promedio_ms']:>12.3f} {results['minimo_ms']:>12.3f} {results['maximo_ms']:>12.3f}")
        
        # Encontrar la más rápida
        fastest = min(benchmark_results.items(), key=lambda x: x[1]['promedio_ms'])
        print(f"\n✅ Estrategia más rápida: {fastest[1]['nombre']} ({fastest[1]['promedio_ms']:.3f} ms)")
        print("=" * 80)
        
        return benchmark_results