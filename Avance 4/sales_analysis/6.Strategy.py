from abc import ABC, abstractmethod
from typing import Dict, Any
from collections import deque
import pandas as pd

# ============================================================================
# STRATEGY PATTERN: Interfaz y Estrategias Concretas
# ============================================================================

class AnalysisStrategy(ABC):
    """
    Interfaz abstracta que define el contrato para todas las estrategias
    de análisis de ventas.
    """
    
    @abstractmethod
    def find_best_period(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Encuentra el periodo de N días consecutivos con mayores ventas.
        
        Args:
            data: DataFrame con columnas 'Fecha' y 'TotalVentas'
            window_size: Tamaño de la ventana (número de días consecutivos)
            
        Returns:
            Dict con información del mejor periodo encontrado
        """
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, str]:
        """
        Retorna información sobre la estrategia.
        
        Returns:
            Dict con nombre, descripción, complejidad y características
        """
        pass


class RollingWindowStrategy(AnalysisStrategy):
    """
    Estrategia que usa el método rolling() de pandas.
    
    Características:
    - Vectorizado en C/Cython
    - Más rápido (~10-50x)
    - Complejidad: O(n)
    - Recomendado para producción
    """
    
    def find_best_period(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        # Crear copia para no modificar el original
        df_copy = data.copy()
        
        # Calcular ventana deslizante
        column_name = f'Ventas_{window_size}dias'
        df_copy[column_name] = df_copy['TotalVentas'].rolling(
            window=window_size, 
            min_periods=window_size
        ).sum()
        
        # Encontrar el índice con mayor volumen
        max_idx = df_copy[column_name].idxmax()
        
        # Extraer el periodo
        periodo = df_copy.loc[max_idx - window_size + 1:max_idx].copy()
        
        return {
            'periodo': periodo[['Fecha', 'TotalVentas']],
            'fecha_inicio': periodo.iloc[0]['Fecha'],
            'fecha_fin': periodo.iloc[-1]['Fecha'],
            'total_ventas': df_copy.loc[max_idx, column_name],
            'estrategia': self.get_strategy_info()['nombre'],
            'dias': window_size
        }
    
    def get_strategy_info(self) -> Dict[str, str]:
        return {
            'nombre': 'Rolling Window',
            'descripcion': 'Operaciones vectorizadas con pandas rolling()',
            'complejidad': 'O(n)',
            'ventajas': 'Vectorizado en C, ultra eficiente',
            'uso_recomendado': 'Producción y datasets grandes'
        }


class ForceBruteStrategy(AnalysisStrategy):
    """
    Estrategia que usa iteración manual con deque.
    
    Características:
    - Fácil de entender
    - Usa deque para ventana deslizante eficiente
    - Complejidad: O(n)
    - Recomendado para aprendizaje
    """
    
    def find_best_period(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        # Usar deque para mantener ventana deslizante
        ventana_deque = deque(maxlen=window_size)
        ventanas = []
        
        # Iterar sobre todas las ventanas
        for i, row in data.iterrows():
            ventana_deque.append(row['TotalVentas'])
            
            # Cuando la deque está llena, calcular suma
            if len(ventana_deque) == window_size:
                suma_ventana = sum(ventana_deque)
                
                ventanas.append({
                    'indice_inicio': i - window_size + 1,
                    'indice_fin': i,
                    'fecha_inicio': data.iloc[i - window_size + 1]['Fecha'],
                    'fecha_fin': data.iloc[i]['Fecha'],
                    'total_ventas': suma_ventana
                })
        
        # Encontrar el periodo con mayor volumen
        max_ventana = max(ventanas, key=lambda x: x['total_ventas'])
        periodo = data.iloc[max_ventana['indice_inicio']:max_ventana['indice_fin']+1].copy()
        
        return {
            'periodo': periodo[['Fecha', 'TotalVentas']],
            'fecha_inicio': max_ventana['fecha_inicio'],
            'fecha_fin': max_ventana['fecha_fin'],
            'total_ventas': max_ventana['total_ventas'],
            'estrategia': self.get_strategy_info()['nombre'],
            'dias': window_size
        }
    
    def get_strategy_info(self) -> Dict[str, str]:
        return {
            'nombre': 'Fuerza Bruta',
            'descripcion': 'Iteración manual con deque para ventana deslizante',
            'complejidad': 'O(n)',
            'ventajas': 'Fácil de entender, explícito',
            'uso_recomendado': 'Verificación y aprendizaje'
        }


class CumulativeSumsStrategy(AnalysisStrategy):
    """
    Estrategia que usa sumas acumuladas con diferencias.
    
    Características:
    - Operaciones matemáticas eficientes
    - Usa cumsum() y diferencias
    - Complejidad: O(n)
    - Recomendado para flexibilidad
    """
    
    def find_best_period(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        # Crear copia
        df_copy = data.copy()
        
        # Crear columna de sumas acumuladas
        df_copy['suma_acumulada'] = df_copy['TotalVentas'].cumsum()
        
        # Calcular ventana usando diferencias de sumas acumuladas
        ventanas_valores = []
        for i in range(len(df_copy)):
            if i >= window_size - 1:
                suma_ventana = df_copy['suma_acumulada'].iloc[i] - \
                              (df_copy['suma_acumulada'].iloc[i-window_size] if i >= window_size else 0)
                ventanas_valores.append(suma_ventana)
            else:
                ventanas_valores.append(None)
        
        # Agregar columna
        column_name = f'Ventas_{window_size}dias'
        df_copy[column_name] = ventanas_valores
        
        # Encontrar el periodo con mayor volumen
        max_idx = df_copy[column_name].idxmax()
        periodo = df_copy.loc[max_idx - window_size + 1:max_idx].copy()
        
        return {
            'periodo': periodo[['Fecha', 'TotalVentas']],
            'fecha_inicio': periodo.iloc[0]['Fecha'],
            'fecha_fin': periodo.iloc[-1]['Fecha'],
            'total_ventas': df_copy.loc[max_idx, column_name],
            'estrategia': self.get_strategy_info()['nombre'],
            'dias': window_size
        }
    
    def get_strategy_info(self) -> Dict[str, str]:
        return {
            'nombre': 'Sumas Acumuladas',
            'descripcion': 'Operaciones matemáticas con sumas acumuladas y diferencias',
            'complejidad': 'O(n)',
            'ventajas': 'Operaciones matemáticas eficientes',
            'uso_recomendado': 'Cuando necesites flexibilidad adicional'
        }


# ============================================================================
# NUEVAS ESTRATEGIAS DE ANÁLISIS (Demostración de Extensibilidad)
# ============================================================================

class MaxSingleDayStrategy(AnalysisStrategy):
    """
    Estrategia que encuentra el día individual con mayor venta.
    
    Características:
    - No usa ventanas deslizantes
    - Encuentra el pico máximo de ventas en un solo día
    - Complejidad: O(n)
    - Útil para identificar días excepcionales
    """
    
    def find_best_period(self, data: pd.DataFrame, window_size: int = 1) -> Dict[str, Any]:
        # Ignorar window_size, siempre busca 1 día
        window_size = 1
        
        # Encontrar el índice del día con mayor venta
        max_idx = data['TotalVentas'].idxmax()
        
        # Extraer ese día
        periodo = data.loc[[max_idx]].copy()
        
        return {
            'periodo': periodo[['Fecha', 'TotalVentas']],
            'fecha_inicio': periodo.iloc[0]['Fecha'],
            'fecha_fin': periodo.iloc[0]['Fecha'],
            'total_ventas': periodo.iloc[0]['TotalVentas'],
            'estrategia': self.get_strategy_info()['nombre'],
            'dias': 1
        }
    
    def get_strategy_info(self) -> Dict[str, str]:
        return {
            'nombre': 'Día Máximo Individual',
            'descripcion': 'Encuentra el día con la venta más alta',
            'complejidad': 'O(n)',
            'ventajas': 'Simple y directo, identifica días excepcionales',
            'uso_recomendado': 'Análisis de picos de venta, eventos especiales'
        }