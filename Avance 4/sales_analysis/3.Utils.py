import pandas as pd

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def load_and_prepare_data(filepath: str) -> pd.DataFrame:
    """
    Carga y prepara los datos de ventas para análisis.
    
    Args:
        filepath: Ruta al archivo CSV con datos de ventas
        
    Returns:
        DataFrame preparado con ventas agregadas por día
    """
    # Cargar datos
    df = pd.read_csv(filepath)
    
    # Convertir a datetime
    df['SalesDate'] = pd.to_datetime(df['SalesDate'])
    
    # Agregar ventas por día
    ventas_por_dia = df.groupby(df['SalesDate'].dt.date)['TotalPriceCalculated'].sum().reset_index()
    ventas_por_dia.columns = ['Fecha', 'TotalVentas']
    ventas_por_dia['Fecha'] = pd.to_datetime(ventas_por_dia['Fecha'])
    
    # Ordenar por fecha
    ventas_por_dia = ventas_por_dia.sort_values('Fecha').reset_index(drop=True)
    
    return ventas_por_dia