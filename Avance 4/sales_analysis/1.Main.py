"""
Proyecto Integrador 1 - Avance 4
Implementación de Patrones de Diseño: Strategy y Factory Method

Este módulo implementa un sistema orientado a objetos para encontrar los N días
consecutivos con mayores ventas usando diferentes estrategias de análisis.

Patrones de Diseño Implementados:
- Strategy Pattern: Encapsula diferentes algoritmos de análisis
- Factory Method Pattern: Crea estrategias en tiempo de ejecución
"""

import importlib.util
import sys
import os

# Importar el módulo 2.Demos usando importlib
_demos_path = os.path.join(os.path.dirname(__file__), '2.Demos.py')
_spec = importlib.util.spec_from_file_location("demos_module", _demos_path)
_demos_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_demos_module)

demo_basic_usage = _demos_module.demo_basic_usage
demo_factory_pattern = _demos_module.demo_factory_pattern
demo_runtime_strategy_switching = _demos_module.demo_runtime_strategy_switching
demo_benchmark = _demos_module.demo_benchmark
demo_interactive_selection = _demos_module.demo_interactive_selection

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que demuestra todas las capacidades del sistema.
    """
    print("\n" + "=" * 80)
    print("SISTEMA DE ANÁLISIS DE VENTAS")
    print("Implementación con Patrones de Diseño: Strategy y Factory Method")
    print("=" * 80)
    
    # Ejecutar todas las demos
    demo_basic_usage()
    demo_factory_pattern()
    demo_runtime_strategy_switching()
    demo_benchmark()
    demo_interactive_selection()
    
    print("\n" + "=" * 80)
    print("✅ TODAS LAS DEMOSTRACIONES COMPLETADAS")
    print("=" * 80)
    print("\n💡 Características implementadas:")
    print("   ✓ Strategy Pattern para encapsular algoritmos")
    print("   ✓ Factory Method para creación en tiempo de ejecución")
    print("   ✓ Selección automática basada en características del dataset")
    print("   ✓ Aliases y preferencias para facilitar uso")
    print("   ✓ Cambio de estrategia en tiempo de ejecución")
    print("   ✓ Benchmarking integrado de estrategias")
    print("   ✓ Sistema extensible para agregar nuevas estrategias")
    print("=" * 80)


if __name__ == "__main__":
    main()

