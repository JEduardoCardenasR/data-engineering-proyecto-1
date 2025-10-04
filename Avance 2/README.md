# PROYECTO INTEGRADOR - AVANCE 2
## Limpieza y optimización de consultas SQL

Este documento contiene el desarrollo de triggers automáticos y análisis de optimización de consultas SQL mediante índices, incluyendo resultados obtenidos y sus respectivas interpretaciones.

---

## CONSIGNA

Entrega un script SQL completo con las consultas desarrolladas junto con un documento donde muestres los resultados obtenidos (mediante capturas de pantalla) y agregues una breve interpretación o comentario para cada uno.

---

## DESARROLLO DEL PROYECTO

### TRIGGER AUTOMÁTICO DE MONITOREO

#### Objetivo
Crear un trigger que registre en una tabla de monitoreo cada vez que un producto supere las 200,000 unidades vendidas acumuladas.

#### Implementación
El trigger debe activarse después de insertar una nueva venta y registrar en la tabla el ID del producto, su nombre, la nueva cantidad total de unidades vendidas, y la fecha en que se superó el umbral.

#### Código SQL Implementado

```sql
-- ===========================================
-- PROYECTO INTEGRADOR - AVANCE 2
-- Optimización de consultas SQL con índices
-- ===========================================

-- ===========================================
-- CREACIÓN DE TABLA DE MONITOREO
-- ===========================================

-- Creación de la tabla monitoreo para registrar productos con alto volumen de ventas
CREATE TABLE monitoreo (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductId INTEGER,
    ProductName TEXT,
    TotalVendido INTEGER,
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- TRIGGER DE MONITOREO AUTOMÁTICO
-- ===========================================

-- Trigger para registrar automáticamente productos con más de 200,000 ventas
CREATE TRIGGER tr_monitoreo_after_insert
AFTER INSERT ON sales
FOR EACH ROW
WHEN (
    (SELECT SUM(Quantity) FROM sales WHERE ProductID = NEW.ProductID) > 200000
    AND NOT EXISTS (
        SELECT 1 FROM monitoreo 
        WHERE ProductId = NEW.ProductID
    )
)
BEGIN
    INSERT INTO monitoreo (ProductId, ProductName, TotalVendido)
    VALUES (
        NEW.ProductID,
        (SELECT ProductName FROM products WHERE ProductID = NEW.ProductID),
        (SELECT SUM(Quantity) FROM sales WHERE ProductID = NEW.ProductID)
    );
END;

-- ===========================================
-- DATOS DE PRUEBA
-- ===========================================

-- Insertar una venta de prueba para el producto 103 (1,876 unidades)
INSERT INTO sales (
    SalesID, 
    SalesPersonID, 
    CustomerID, 
    ProductID, 
    Quantity,
    Discount,
    TotalPrice,
    SalesDate,
    TransactionNumber
) VALUES (
    6758126, 
    9, 
    84, 
    103, 
    1876, 
    0.00,
    1200.00,
    CURRENT_TIMESTAMP, 
    'I28H3548AWIT4D2AS9FE'
);

-- ===========================================
-- ANÁLISIS DE OPTIMIZACIÓN CON ÍNDICES
-- Top 2 Consultas con Mayor Potencial de Optimización
-- ===========================================

-- ===========================================
-- CONSULTA #1 - Los 5 productos más vendidos
-- ===========================================

.timer on

SELECT s.ProductID, p.ProductName, SUM(s.Quantity) AS TotalQuantity
FROM products AS p
JOIN sales AS s 
ON p.ProductID = s.ProductID
GROUP BY s.ProductID, p.ProductName
ORDER BY TotalQuantity DESC
LIMIT 5;

-- Creación del índice optimizado para esta consulta
-- Optimiza: JOINs, GROUP BY, ORDER BY y agregaciones SUM
CREATE INDEX idx_sales_product_quantity ON sales(ProductID, Quantity);

-- ===========================================
-- CONSULTA #2 - Vendedores principales por producto
-- ===========================================

.timer on

-- Consulta original con CTEs
WITH TopProducts AS (
    SELECT 
        p.ProductID, 
        p.ProductName, 
        SUM(s.Quantity) as TotalVendido
    FROM products p
    JOIN sales s ON p.ProductID = s.ProductID
    GROUP BY p.ProductID, p.ProductName
    ORDER BY TotalVendido DESC
    LIMIT 5
),
TopSellersPerProduct AS (
    SELECT 
        s.ProductID,
        s.SalesPersonID,
        e.FirstName || ' ' || e.LastName as Vendedor,
        SUM(s.Quantity) as UnidadesVendidas,
        ROW_NUMBER() OVER (PARTITION BY s.ProductID ORDER BY SUM(s.Quantity) DESC) as rn
    FROM sales s
    JOIN employees e ON s.SalesPersonID = e.EmployeeID
    WHERE s.ProductID IN (SELECT ProductID FROM TopProducts)
    GROUP BY s.ProductID, s.SalesPersonID, e.FirstName, e.LastName
)
SELECT 
    tp.ProductID,
    tp.ProductName,
    tp.TotalVendido,
    tsv.Vendedor,
    tsv.UnidadesVendidas
FROM TopProducts tp
JOIN TopSellersPerProduct tsv ON tp.ProductID = tsv.ProductID
WHERE tsv.rn = 1
ORDER BY tp.TotalVendido DESC;

-- Creación del índice optimizado para esta consulta
-- Optimiza: Filtros WHERE, JOINs múltiples y GROUP BY compuesto
CREATE INDEX idx_sales_product_salesperson ON sales(ProductID, SalesPersonID);

-- ===========================================
-- RESUMEN DE ÍNDICES CREADOS
-- ===========================================

-- Los siguientes índices fueron creados para optimizar las consultas:
-- 1. idx_sales_product_quantity: Optimiza JOINs y GROUP BY en consulta #1
-- 2. idx_sales_product_salesperson: Optimiza filtros WHERE y JOINs en consulta #2

-- Para verificar el impacto de los índices, compara los tiempos de ejecución
-- antes y después de crear cada índice usando .timer on

-- ===========================================
-- NOTAS DE OPTIMIZACIÓN
-- ===========================================

-- Los índices compuestos son más efectivos en:
-- - Claves foráneas (ProductID, SalesPersonID)
-- - Columnas de agregación (Quantity)
-- - Operaciones de filtrado (WHERE)
-- - Operaciones de agrupación (GROUP BY)

-- El impacto varía según la complejidad de la consulta:
-- - Consultas simples: Mayor beneficio relativo
-- - Consultas complejas: Beneficio limitado por operaciones computacionales
```

---

## RESULTADOS Y ANÁLISIS

### REGISTRO DE VENTA Y MONITOREO AUTOMÁTICO

#### Registro de la venta:
Se registró una venta correspondiente al vendedor con ID 9, al cliente con ID 84, del producto con ID 103, por una cantidad de 1,876 unidades y un valor de 1200 unidades.

#### Registro automático en la tabla monitoreo:
El trigger se activó automáticamente y registró el producto en la tabla de monitoreo al superar las 200,000 unidades vendidas acumuladas.

#### Análisis del Sistema de Monitoreo:
El sistema implementado consiste en la creación de una tabla de monitoreo con campos auto-incrementales compatibles con SQLite, seguida de un trigger automático que se ejecuta después de cada inserción en la tabla `sales`. Cuando se inserta una nueva venta, el trigger evalúa automáticamente si el producto vendido cumple con dos condiciones específicas: que la suma total de cantidades vendidas para ese producto supere las 200,000 unidades y que dicho producto no exista previamente en la tabla de monitoreo. Si ambas condiciones se cumplen, el trigger ejecuta automáticamente un INSERT en la tabla `monitoreo`, registrando el ID del producto, su nombre, el total vendido acumulado y la fecha de registro actual, creando así un sistema de alerta automática que identifica productos con altos volúmenes de venta sin intervención manual. En este caso se realizó un registro exitoso con los datos: vendedor con ID 9, cliente con ID 84, producto con ID 103, cantidad de 1,876 unidades y un valor de 1200 unidades.

---

### OPTIMIZACIÓN DE CONSULTAS CON ÍNDICES

#### Resultados de Rendimiento:

| Consulta | Sin Índices | Con Índices | Mejora |
|----------|-------------|-------------|---------|
| **Primera consulta** | 9.0s | 4.9s | **45.6% mejora** |
| **Segunda consulta** | 5.1s | 4.8s | **5.9% mejora** |

#### Capturas de Pantalla de Resultados:

**Primera consulta (Sin índices) – tiempo 9s:**
![Primera consulta sin índices - 9 segundos]

**Primera consulta (Con índice) – tiempo 4.9s:**
![Primera consulta con índice - 4.9 segundos]

**Segunda consulta (Sin índices) – tiempo 5.1s:**
![Segunda consulta sin índices - 5.1 segundos]

**Segunda consulta (Con índices) – tiempo 4.8s:**
![Segunda consulta con índices - 4.8 segundos]

#### Análisis de Optimización:

Los resultados demuestran que los índices compuestos son **altamente efectivos** para optimizar consultas SQL, especialmente aquellas que involucran JOINs por claves foráneas, agregaciones y filtros WHERE. La primera consulta mostró una mejora dramática del **45.6%** (de 9.0s a 4.9s) gracias al índice `(ProductID, Quantity)` que optimizó directamente las operaciones de JOIN, GROUP BY y ORDER BY. Sin embargo, la segunda consulta tuvo una mejora limitada del **5.9%** (de 5.1s a 4.8s) debido a su mayor complejidad con múltiples CTEs y funciones de ventana que no se benefician completamente de los índices simples. Los índices resultan **más efectivos en columnas con alta selectividad** como claves foráneas (`ProductID`, `SalesPersonID`) y columnas de agregación (`Quantity`), mientras que su impacto es menor en consultas complejas con múltiples operaciones computacionales. En general, los índices proporcionaron una **mejora del 31.2%** en el tiempo total de ejecución, confirmando su valor como herramienta fundamental de optimización de bases de datos para operaciones de análisis y reportes.

---

## ÍNDICES IMPLEMENTADOS

### Índices Críticos Creados:

1. **`idx_sales_product_quantity`**: `(ProductID, Quantity)`
   - **Propósito**: Optimiza JOINs, GROUP BY, ORDER BY y agregaciones SUM
   - **Impacto**: 45.6% mejora en primera consulta

2. **`idx_sales_product_salesperson`**: `(ProductID, SalesPersonID)`
   - **Propósito**: Optimiza filtros WHERE, JOINs múltiples y GROUP BY compuesto
   - **Impacto**: 5.9% mejora en segunda consulta

### Características de los Índices:

- **Índices compuestos**: Combinan múltiples columnas para optimización integral
- **Claves foráneas**: ProductID y SalesPersonID para optimizar JOINs
- **Columnas de agregación**: Quantity para optimizar SUM y GROUP BY
- **Alta selectividad**: Columnas con muchos valores únicos para mayor eficiencia

---

## CONCLUSIONES

### Sistema de Monitoreo Automático:
El trigger implementado demuestra la capacidad de SQLite para automatizar procesos de monitoreo y alertas, creando un sistema robusto que identifica productos con alto volumen de ventas sin intervención manual.

### Optimización con Índices:
Los índices compuestos demostraron ser **herramientas fundamentales** para la optimización de consultas SQL, especialmente efectivos en:
- Operaciones de JOIN por claves foráneas
- Agregaciones y funciones de agrupación
- Filtros WHERE con alta selectividad
- Operaciones de ordenamiento

### Impacto en el Rendimiento:
- **Mejora general**: 31.2% en tiempo total de ejecución
- **Consultas simples**: Mayor beneficio relativo (45.6%)
- **Consultas complejas**: Beneficio limitado por operaciones computacionales (5.9%)

### Recomendaciones:
1. **Priorizar índices** en claves foráneas y columnas de agregación
2. **Evaluar costo-beneficio** entre velocidad de consulta y mantenimiento
3. **Considerar complejidad** de consultas al diseñar estrategias de optimización
4. **Monitorear rendimiento** continuamente para ajustar índices según patrones de uso

---

## ARCHIVOS INCLUÍDOS

1. **`codigo.sql`**: Script completo con triggers, datos de prueba y análisis de optimización
2. **`README.md`**: Este documento con resumen ejecutivo y documentación completa del proyecto

---

*Proyecto Integrador - Avance 2*  
*Módulo: Limpieza y optimización de consultas SQL*
