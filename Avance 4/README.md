# 🎯 AVANCE 4 - Proyecto Integrador 1

## 📋 Descripción General

Este avance implementa análisis de ventas utilizando múltiples enfoques computacionales y patrones de diseño de software. El objetivo principal es encontrar periodos consecutivos con el mayor volumen de ventas, demostrando tanto eficiencia computacional como buenas prácticas de programación orientada a objetos.

---

## 📂 Estructura del Proyecto

```
Avance 4/
│
├── extra_credit.ipynb          # Notebook con análisis exploratorio y benchmarking
│
└── sales_analysis/             # Sistema modular con patrones de diseño
    ├── 1.Main.py              # Punto de entrada del sistema
    ├── 2.Demos.py             # Funciones de demostración
    ├── 3.Utils.py             # Utilidades y carga de datos
    ├── 4.Analyzer.py          # Clase contexto SalesAnalyzer
    ├── 5.Factory.py           # Factory Method para crear estrategias
    └── 6.Strategy.py          # Estrategias de análisis (Strategy Pattern)
```

---

## 📊 1. Extra Credit Notebook (`extra_credit.ipynb`)

### 🎯 Objetivo
Encontrar el periodo de **5 días consecutivos** con el mayor volumen de ventas totales usando múltiples enfoques computacionales.

### 🚀 Enfoques Implementados

#### 1️⃣ **Rolling Window**
- ✅ Operaciones vectorizadas con pandas
- ✅ Implementado en C/Cython
- ✅ Más eficiente (~10-50x más rápido)
- ✅ Complejidad: O(n)
- 🎯 **Recomendado para:** Producción y datasets grandes

#### 2️⃣ **Fuerza Bruta** (Iteración manual con deque)
- ✅ Fácil de entender
- ✅ Explícito y educativo
- ✅ Usa `deque` para ventana deslizante eficiente
- ✅ Complejidad: O(n)
- 🎯 **Recomendado para:** Verificación y aprendizaje

#### 3️⃣ **Sumas Acumuladas** (Con diferencias)
- ✅ Operaciones matemáticas eficientes
- ✅ Usa `cumsum()` y diferencias
- ✅ Complejidad: O(n)
- 🎯 **Recomendado para:** Flexibilidad adicional

### 📈 Análisis de Rendimiento

El notebook incluye:
- ⏱️ **Perfilamiento con `timeit`**: 1000 repeticiones por enfoque
- 📊 **Métricas estadísticas**: promedio, mínimo, máximo, desviación estándar
- 📉 **Coeficiente de variación**: evaluación de estabilidad
- 📊 **Visualizaciones**: gráficos comparativos de rendimiento

### ✅ Resultado

**Periodo de 5 días con mayor volumen:**
- 📅 **Fecha inicio:** 2018-03-28
- 📅 **Fecha fin:** 2018-04-01
- 💰 **Total de ventas:** $166,612,521.77

---

## 🏗️ 2. Sistema Modular (`sales_analysis/`)

### 🎨 Patrones de Diseño Implementados

#### 1. **Strategy Pattern** (`6.Strategy.py`)
Encapsula diferentes algoritmos de análisis en clases intercambiables.

**Estrategias disponibles:**
- `RollingWindowStrategy` - Análisis con rolling window de pandas
- `ForceBruteStrategy` - Iteración manual con deque
- `CumulativeSumsStrategy` - Análisis con sumas acumuladas
- `MaxSingleDayStrategy` 🆕 - Encuentra el día con máxima venta individual

#### 2. **Factory Method Pattern** (`5.Factory.py`)
Crea instancias de estrategias en tiempo de ejecución.

**Modos de selección:**
- Por nombre directo: `'rolling'`, `'force_brute'`, `'cumulative'`, `'max_day'`
- Por preferencia de rendimiento: `'fastest'`, `'balanced'`, `'educational'`
- Automático: Selecciona según tamaño del dataset

#### 3. **Context Class** (`4.Analyzer.py`)
Clase `SalesAnalyzer` que coordina el análisis usando la estrategia seleccionada.

---

## 📦 Módulos del Sistema

### `1.Main.py` - Punto de Entrada
Función principal que ejecuta todas las demostraciones del sistema.

### `2.Demos.py` - Demostraciones
Incluye 5 demos:
1. **Demo básico** - Uso básico del sistema
2. **Factory pattern** - Creación de estrategias en tiempo de ejecución
3. **Runtime switching** - Cambio de estrategia dinámico
4. **Benchmark** - Comparación de rendimiento de todas las estrategias
5. **Selección interactiva** - Simulación de selección de usuario

### `3.Utils.py` - Utilidades
Funciones auxiliares para carga y preparación de datos.

### `4.Analyzer.py` - Analizador
Clase `SalesAnalyzer` que encapsula la lógica de análisis:
- Validación de datos
- Ejecución de estrategias
- Impresión de resultados
- Benchmarking de estrategias

### `5.Factory.py` - Factory
Clase `AnalysisStrategyFactory` que:
- Registra estrategias disponibles
- Crea instancias basadas en nombre o preferencia
- Soporta aliases para facilitar uso
- Selección automática según características del dataset

### `6.Strategy.py` - Estrategias
Interfaz `AnalysisStrategy` y 4 implementaciones concretas:
- Todas comparten la misma interfaz
- Cada una implementa un algoritmo diferente
- Fácil de extender con nuevas estrategias

---

## 🚀 Cómo Ejecutar

### Prerrequisitos
```bash
pip install pandas numpy
```

### Ejecutar el notebook
```bash
jupyter notebook extra_credit.ipynb
```

### Ejecutar el sistema modular
```bash
cd sales_analysis
python 1.Main.py
```

### Usar el sistema en tu código
```python
from sales_analysis import SalesAnalyzer, AnalysisStrategyFactory, load_and_prepare_data

# Cargar datos
data = load_and_prepare_data('../../data/sales_price.csv')

# Crear analizador con estrategia específica
strategy = AnalysisStrategyFactory.create_strategy('rolling')
analyzer = SalesAnalyzer(strategy)

# Ejecutar análisis
results = analyzer.analyze(data, window_size=5)
analyzer.print_results(results)

# Cambiar estrategia en tiempo de ejecución
strategy = AnalysisStrategyFactory.create_strategy('max_day')
analyzer.set_strategy(strategy)
results = analyzer.analyze(data)
```

---

## ✨ Características Destacadas

### 🎯 Extensibilidad
- ✅ Agregar nuevas estrategias sin modificar código existente
- ✅ Solo requiere crear una clase que herede de `AnalysisStrategy`
- ✅ Registrar en Factory con 1 línea de código
- ✅ Demostrado con `MaxSingleDayStrategy`

### 📊 Rendimiento
- ✅ Benchmarking integrado de todas las estrategias
- ✅ Métricas detalladas (promedio, mín, máx, desviación estándar)
- ✅ Comparación visual de rendimiento
- ✅ Identificación automática de la estrategia más rápida

### 🔄 Flexibilidad
- ✅ Cambio de estrategia en tiempo de ejecución
- ✅ Selección automática según tamaño del dataset
- ✅ Aliases para facilitar uso
- ✅ Configuración flexible de parámetros

### 📝 Código Limpio
- ✅ Separación de responsabilidades
- ✅ Código modular y reutilizable
- ✅ Documentación completa (docstrings)
- ✅ Nombres descriptivos y claros

---

## 📈 Resultados de Rendimiento

### Ventana de 5 días (129 días de datos)

| Estrategia | Promedio (ms) | Mínimo (ms) | Máximo (ms) |
|------------|---------------|-------------|-------------|
| Rolling Window | ~0.5 | ~0.4 | ~0.8 |
| Fuerza Bruta | ~15.0 | ~12.0 | ~25.0 |
| Sumas Acumuladas | ~2.5 | ~2.0 | ~4.0 |
| Día Máximo | ~0.3 | ~0.2 | ~0.5 |

**Conclusión:** Rolling Window es **~30x más rápido** que Fuerza Bruta.

---

## 🎓 Conceptos Demostrados

### Patrones de Diseño
- ✅ **Strategy Pattern** - Encapsulación de algoritmos
- ✅ **Factory Method** - Creación de objetos en tiempo de ejecución
- ✅ **Principio Open/Closed** - Abierto a extensión, cerrado a modificación

### Buenas Prácticas
- ✅ **Programación Orientada a Objetos**
- ✅ **Código modular y reutilizable**
- ✅ **Documentación completa**
- ✅ **Type hints** para mejor legibilidad

### Análisis de Rendimiento
- ✅ **Perfilamiento con timeit**
- ✅ **Análisis estadístico de rendimiento**
- ✅ **Comparación de enfoques algorítmicos**
- ✅ **Visualización de resultados**

---

## 🆕 Nueva Estrategia Agregada

### `MaxSingleDayStrategy`

**Propósito:** Demostrar la extensibilidad del sistema

**Características:**
- Encuentra el día individual con mayor venta
- No usa ventanas deslizantes
- Útil para identificar picos de venta y eventos especiales
- Complejidad: O(n)

**Cómo se agregó:**
1. Se creó la clase en `6.Strategy.py` (sin modificar código existente)
2. Se registró en `5.Factory.py` con el nombre `'max_day'`
3. Automáticamente disponible en todo el sistema
4. Incluida en demos y benchmarking

**Esto demuestra:** Agregar nuevos tipos de análisis es trivial y no requiere cambios en el código central.

---

## 📚 Referencias y Documentación

### Archivos principales
- `extra_credit.ipynb` - Análisis exploratorio y benchmarking
- `1.Main.py` - Ejecuta todas las demostraciones
- `6.Strategy.py` - Define todas las estrategias de análisis

### Datos
- **Dataset:** `../data/sales_price.csv`
- **Periodo:** 2018-01-01 a 2018-05-09
- **Total días:** 129

### Dependencias
- Python 3.8+
- pandas
- numpy
- jupyter (para el notebook)

---

## 👥 Autor

Proyecto Integrador 1 - Avance 4  
Data Engineering - Módulo 1

---

## 📝 Notas Adicionales

### Ventajas del enfoque modular
1. **Mantenibilidad:** Cada módulo tiene una responsabilidad única
2. **Testabilidad:** Fácil escribir tests unitarios para cada componente
3. **Escalabilidad:** Agregar funcionalidad es simple y seguro
4. **Legibilidad:** Código organizado y fácil de entender

### Lecciones aprendidas
1. Los patrones de diseño facilitan la extensibilidad
2. El perfilamiento es crucial para optimización
3. Las operaciones vectorizadas son significativamente más rápidas
4. La modularización mejora la calidad del código

---

## 🎯 Conclusiones

Este avance demuestra:
- ✅ Múltiples enfoques para resolver el mismo problema
- ✅ Análisis de rendimiento riguroso
- ✅ Implementación de patrones de diseño clásicos
- ✅ Sistema extensible y mantenible
- ✅ Código profesional y bien documentado

El sistema es **robusto, eficiente y fácil de extender**, cumpliendo con las mejores prácticas de desarrollo de software.

---

**🎉 ¡Proyecto completado exitosamente!**

