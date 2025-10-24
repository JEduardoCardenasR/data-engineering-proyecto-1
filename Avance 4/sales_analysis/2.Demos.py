import importlib.util
import sys
import os

# Importar el módulo 3.Utils usando importlib
_utils_path = os.path.join(os.path.dirname(__file__), '3.Utils.py')
_spec1 = importlib.util.spec_from_file_location("utils_module", _utils_path)
_utils_module = importlib.util.module_from_spec(_spec1)
_spec1.loader.exec_module(_utils_module)

load_and_prepare_data = _utils_module.load_and_prepare_data

# Importar el módulo 4.Analyzer usando importlib
_analyzer_path = os.path.join(os.path.dirname(__file__), '4.Analyzer.py')
_spec2 = importlib.util.spec_from_file_location("analyzer_module", _analyzer_path)
_analyzer_module = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(_analyzer_module)

SalesAnalyzer = _analyzer_module.SalesAnalyzer

# Importar el módulo 5.Factory usando importlib
_factory_path = os.path.join(os.path.dirname(__file__), '5.Factory.py')
_spec3 = importlib.util.spec_from_file_location("factory_module", _factory_path)
_factory_module = importlib.util.module_from_spec(_spec3)
_spec3.loader.exec_module(_factory_module)

AnalysisStrategyFactory = _factory_module.AnalysisStrategyFactory

# ============================================================================
# DEMOSTRACIÓN Y EJEMPLOS DE USO
# ============================================================================

def demo_basic_usage():
    """Demuestra el uso básico del sistema."""
    print("\n" + "=" * 80)
    print("DEMO 1: USO BÁSICO")
    print("=" * 80)
    
    # Cargar datos
    print("\n1️⃣ Cargando datos...")
    data = load_and_prepare_data('../../data/sales_price.csv')
    print(f"   ✅ {len(data)} días cargados")
    
    # Crear analizador con estrategia por defecto
    print("\n2️⃣ Creando analizador con estrategia por defecto (Rolling Window)...")
    analyzer = SalesAnalyzer()
    print(f"   ✅ Estrategia actual: {analyzer.get_current_strategy_info()['nombre']}")
    
    # Ejecutar análisis
    print("\n3️⃣ Ejecutando análisis para encontrar los 5 mejores días...")
    results = analyzer.analyze(data, window_size=5)
    analyzer.print_results(results)


def demo_factory_pattern():
    """Demuestra el uso del Factory Method para crear estrategias."""
    print("\n" + "=" * 80)
    print("DEMO 2: FACTORY METHOD - Selección en Tiempo de Ejecución")
    print("=" * 80)
    
    # Listar estrategias disponibles
    print("\n1️⃣ Listando estrategias disponibles:")
    AnalysisStrategyFactory.list_available_strategies()
    
    # Cargar datos
    data = load_and_prepare_data('../../data/sales_price.csv')
    
    # Probar diferentes formas de crear estrategias
    print("\n2️⃣ Creando estrategias usando el Factory:")
    
    # Por nombre directo
    print("\n   a) Por nombre directo: 'rolling'")
    strategy1 = AnalysisStrategyFactory.create_strategy('rolling')
    analyzer1 = SalesAnalyzer(strategy1)
    print(f"      ✅ Creada: {analyzer1.get_current_strategy_info()['nombre']}")
    
    # Por preferencia
    print("\n   b) Por preferencia de rendimiento: 'fastest'")
    strategy2 = AnalysisStrategyFactory.create_strategy('fastest')
    analyzer2 = SalesAnalyzer(strategy2)
    print(f"      ✅ Creada: {analyzer2.get_current_strategy_info()['nombre']}")
    
    # Por preferencia educativa
    print("\n   c) Por preferencia educativa: 'educational'")
    strategy3 = AnalysisStrategyFactory.create_strategy('educational')
    analyzer3 = SalesAnalyzer(strategy3)
    print(f"      ✅ Creada: {analyzer3.get_current_strategy_info()['nombre']}")
    
    # Automática basada en datos
    print("\n   d) Selección automática basada en tamaño del dataset:")
    strategy4 = AnalysisStrategyFactory.create_automatic(data)
    analyzer4 = SalesAnalyzer(strategy4)
    print(f"      ✅ Creada: {analyzer4.get_current_strategy_info()['nombre']}")


def demo_runtime_strategy_switching():
    """Demuestra el cambio de estrategia en tiempo de ejecución."""
    print("\n" + "=" * 80)
    print("DEMO 3: CAMBIO DE ESTRATEGIA EN TIEMPO DE EJECUCIÓN")
    print("=" * 80)
    
    # Cargar datos
    data = load_and_prepare_data('../../data/sales_price.csv')
    
    # Crear analizador
    analyzer = SalesAnalyzer()
    
    # Probar con diferentes estrategias
    estrategias_a_probar = ['rolling', 'force_brute', 'cumulative', 'max_day']
    
    for nombre in estrategias_a_probar:
        print(f"\n{'='*80}")
        strategy = AnalysisStrategyFactory.create_strategy(nombre)
        analyzer.set_strategy(strategy)
        
        info = analyzer.get_current_strategy_info()
        print(f"🔄 Estrategia cambiada a: {info['nombre']}")
        print(f"   Descripción: {info['descripcion']}")
        
        results = analyzer.analyze(data, window_size=5)
        print(f"   ✅ Resultado: ${results['total_ventas']:,.2f}")


def demo_benchmark():
    """Demuestra el benchmarking de estrategias."""
    print("\n" + "=" * 80)
    print("DEMO 4: BENCHMARK DE TODAS LAS ESTRATEGIAS")
    print("=" * 80)
    
    # Cargar datos
    data = load_and_prepare_data('../../data/sales_price.csv')
    
    # Crear analizador
    analyzer = SalesAnalyzer()
    
    # Ejecutar benchmark
    benchmark_results = analyzer.benchmark_strategies(data, window_size=5, repetitions=100)


def demo_interactive_selection():
    """Demuestra la selección interactiva de estrategias."""
    print("\n" + "=" * 80)
    print("DEMO 5: SELECCIÓN INTERACTIVA (Simulada)")
    print("=" * 80)
    
    # Cargar datos
    data = load_and_prepare_data('../../data/sales_price.csv')
    
    # Simular entrada del usuario
    opciones = ['fastest', 'balanced', 'educational']
    
    print("\n📋 Opciones disponibles:")
    print("   1. fastest - Máximo rendimiento")
    print("   2. balanced - Rendimiento balanceado")
    print("   3. educational - Fácil de entender")
    
    for i, opcion in enumerate(opciones, 1):
        print(f"\n{'='*80}")
        print(f"🔍 Simulando selección de opción {i}: '{opcion}'")
        
        strategy = AnalysisStrategyFactory.create_strategy(opcion)
        analyzer = SalesAnalyzer(strategy)
        
        info = analyzer.get_current_strategy_info()
        print(f"   ✅ Estrategia seleccionada: {info['nombre']}")
        print(f"   Uso recomendado: {info['uso_recomendado']}")
        
        results = analyzer.analyze(data, window_size=5)
        print(f"   Resultado: {results['fecha_inicio'].strftime('%Y-%m-%d')} a {results['fecha_fin'].strftime('%Y-%m-%d')}")
        print(f"   Total: ${results['total_ventas']:,.2f}")