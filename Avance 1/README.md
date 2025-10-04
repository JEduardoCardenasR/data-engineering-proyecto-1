# PROYECTO INTEGRADOR - AVANCE 1
## Carga y exploración de datos en SQL

Este documento contiene las consultas SQL desarrolladas para el análisis de ventas y los resultados obtenidos con sus respectivas interpretaciones.

---

## CONSIGNA
Desarrollar consultas SQL para análisis de datos de ventas e incluir en un documento una captura de pantalla con la salida de cada una, junto con una breve interpretación. Además, entregar el script SQL completo utilizado.

---

## CONSULTAS SQL DESARROLLADAS

### PREGUNTA 1: 5 Productos Más Vendidos y sus Vendedores Principales

#### Consulta 1.1: Los 5 productos más vendidos
```sql
SELECT s.ProductID, p.ProductName, SUM(s.Quantity) AS TotalQuantity
FROM products AS p
JOIN sales AS s 
ON p.ProductID = s.ProductID
GROUP BY s.ProductID, p.ProductName
ORDER BY TotalQuantity DESC
LIMIT 5;
```

#### Consulta 1.2: Vendedores que más vendieron de cada producto top
```sql
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
```

#### Consulta 1.3: Análisis de vendedores que superaron el 10% de ventas
```sql
CREATE TEMP TABLE TopProducts AS
SELECT 
    p.ProductID, 
    p.ProductName, 
    SUM(s.Quantity) as TotalVendido
FROM products p
JOIN sales s ON p.ProductID = s.ProductID
GROUP BY p.ProductID, p.ProductName
ORDER BY TotalVendido DESC
LIMIT 5;

CREATE TEMP TABLE VendedorRanking AS
SELECT 
    s.ProductID,
    tp.ProductName,
    s.SalesPersonID,
    e.FirstName || ' ' || e.LastName as Vendedor,
    SUM(s.Quantity) as UnidadesVendidas,
    tp.TotalVendido,
    ROUND((SUM(s.Quantity) * 100.0 / tp.TotalVendido), 2) as PorcentajeVendido,
    ROW_NUMBER() OVER (PARTITION BY s.ProductID ORDER BY SUM(s.Quantity) * 100.0 / tp.TotalVendido DESC) as Ranking
FROM sales s
JOIN employees e ON s.SalesPersonID = e.EmployeeID
JOIN TopProducts tp ON s.ProductID = tp.ProductID
GROUP BY s.ProductID, tp.ProductName, s.SalesPersonID, e.FirstName, e.LastName, tp.TotalVendido;

SELECT 
    vr.ProductID,
    vr.ProductName,
    vr.TotalVendido,
    vr.Vendedor,
    vr.UnidadesVendidas,
    vr.PorcentajeVendido || '%' as Porcentaje,
    CASE 
        WHEN vr.PorcentajeVendido > 10 THEN 'SÍ'
        ELSE 'NO'
    END as Supera10Porciento
FROM VendedorRanking vr
WHERE vr.Ranking = 1
ORDER BY vr.TotalVendido DESC;
```

---

### PREGUNTA 2: Análisis de Clientes Únicos

#### Consulta 2.1: Clientes únicos por producto top 5
```sql
SELECT 
    s.ProductID,
    tp.ProductName,
    COUNT(DISTINCT s.CustomerID) as ClientesUnicos
FROM sales s
JOIN TopProducts tp ON s.ProductID = tp.ProductID
GROUP BY s.ProductID, tp.ProductName
ORDER BY ClientesUnicos DESC;
```

#### Consulta 2.2: Proporción de clientes sobre el total
```sql
WITH TotalClientesEnTop5 AS (
    SELECT COUNT(DISTINCT CustomerID) as TotalClientes
    FROM sales 
),
ClientesPorProducto AS (
    SELECT 
        s.ProductID,
        tp.ProductName,
        COUNT(DISTINCT s.CustomerID) as ClientesUnicos
    FROM sales s
    JOIN TopProducts tp ON s.ProductID = tp.ProductID
    GROUP BY s.ProductID, tp.ProductName
)
SELECT 
    cpp.ProductID,
    cpp.ProductName,
    cpp.ClientesUnicos,
    tct.TotalClientes,
    ROUND((cpp.ClientesUnicos * 100.0 / tct.TotalClientes), 2) || '%' as PorcentajeDelTotal
FROM ClientesPorProducto cpp
CROSS JOIN TotalClientesEnTop5 tct
ORDER BY cpp.ClientesUnicos DESC;
```

---

### PREGUNTA 3: Análisis por Categorías

#### Consulta 3.1: Categorías de productos top 5 y su relevancia
```sql
WITH CategoriasDeTop5 AS (
    SELECT 
        tp.ProductID, 
        tp.ProductName, 
        tp.TotalVendido,
        c.CategoryID, 
        c.CategoryName
    FROM TopProducts tp
    JOIN products p ON tp.ProductID = p.ProductID
    JOIN categories c ON p.CategoryID = c.CategoryID
),
TotalVendidoCategoria AS (
    SELECT 
        p.CategoryID,
        SUM(s.Quantity) as TotalCategoria
    FROM sales s
    JOIN products p ON s.ProductID = p.ProductID
    WHERE p.CategoryID IN (SELECT CategoryID FROM CategoriasDeTop5)
    GROUP BY p.CategoryID
),
ConRankingEnCategoria AS (
    SELECT 
        s.ProductID,
        p.ProductName,
        c.CategoryID,
        c.CategoryName,
        RANK() OVER (PARTITION BY c.CategoryID ORDER BY SUM(s.Quantity) DESC) as RankingEnCategoria,
        COUNT(*) OVER (PARTITION BY c.CategoryID) as TotalProductosEnCategoria
    FROM sales s
    JOIN products p ON s.ProductID = p.ProductID
    JOIN categories c ON p.CategoryID = c.CategoryID
    JOIN TotalVendidoCategoria tc ON c.CategoryID = tc.CategoryID
    GROUP BY s.ProductID, p.ProductName, c.CategoryID, c.CategoryName
)
SELECT 
    cdt.ProductID,
    cdt.ProductName,
    cdt.TotalVendido,
    cdt.CategoryName,
    td.TotalCategoria,
    ROUND((cdt.TotalVendido * 100.0 / td.TotalCategoria), 2) || '%' as PorcentajeVendido,
    crc.RankingEnCategoria
FROM CategoriasDeTop5 cdt
JOIN TotalVendidoCategoria td ON cdt.CategoryID = td.CategoryID
JOIN ConRankingEnCategoria crc ON cdt.ProductID = crc.ProductID
ORDER BY cdt.TotalVendido DESC;
```

---

### PREGUNTA 4: Top 10 Productos del Catálogo Completo

#### Consulta 4.1: Top 10 productos con categoría
```sql
CREATE TEMP TABLE Top10Productos AS
    SELECT 
        s.ProductID,
        p.ProductName,
        c.CategoryID,
        c.CategoryName,
        SUM(s.Quantity) as TotalVendido
    FROM sales s
    JOIN products p ON s.ProductID = p.ProductID
    JOIN categories c ON p.CategoryID = c.CategoryID
    GROUP BY s.ProductID, p.ProductName, c.CategoryID, c.CategoryName
    ORDER BY TotalVendido DESC
    LIMIT 10;
```

#### Consulta 4.2: Ranking de productos dentro de sus categorías
```sql
CREATE TEMP TABLE ConRankingEnCategoria AS 
    SELECT 
        s.ProductID,
        p.ProductName,
        c.CategoryID,
        c.CategoryName,
        RANK() OVER (PARTITION BY c.CategoryID ORDER BY SUM(s.Quantity) DESC) as RankingEnCategoria,
        COUNT(*) OVER (PARTITION BY c.CategoryID) as TotalProductosEnCategoria
    FROM sales s
    JOIN products p ON s.ProductID = p.ProductID
    JOIN categories c ON p.CategoryID = c.CategoryID
    JOIN Top10Productos tp ON c.CategoryID = tp.CategoryID
    GROUP BY s.ProductID, p.ProductName, c.CategoryID, c.CategoryName;

SELECT 
    tp.ProductID,
    tp.ProductName,
    tp.CategoryID,
    tp.CategoryName,
    tp.TotalVendido,
    crc.RankingEnCategoria,
    crc.TotalProductosEnCategoria
FROM Top10Productos tp
JOIN ConRankingEnCategoria crc ON tp.ProductID = crc.ProductID;
```

---

## RESULTADOS Y ANÁLISIS

### PREGUNTA 1: 5 Productos Más Vendidos y Vendedores Principales

#### Resultado: ¿Hay algún vendedor que aparece más de una vez como el que más vendió un producto?
**Sí, Devon Brewer aparece dos veces** como el principal vendedor de diferentes productos ("Thyme - Lemon; Fresh" y "Onion Powder").

#### Resultado: ¿Alguno de estos vendedores representa más del 10% de las ventas de este producto?
**No, ningún vendedor supera el 10% del total de ventas de cada producto.**

#### Interpretación:
El análisis muestra que los cinco productos más vendidos tienen una participación distribuida entre distintos vendedores, ninguno de los cuales supera el 10% del total de ventas de cada producto, lo que indica que la demanda está bien diversificada y no depende de un solo actor comercial. Sin embargo, se observa que Devon Brewer aparece dos veces como el principal vendedor de diferentes productos, lo que refleja un desempeño consistente y relevante en el portafolio. En general, los resultados sugieren que, aunque existen vendedores destacados, la concentración de ventas por individuo sigue siendo baja, lo que disminuye riesgos de dependencia excesiva y muestra un mercado con participación más equilibrada entre la fuerza de ventas.

---

### PREGUNTA 2: Análisis de Clientes Únicos

#### Resultado: Clientes únicos que compraron los productos más vendidos
Los cinco productos más vendidos fueron adquiridos por aproximadamente **14% de la base total de clientes**, con valores muy cercanos entre sí (14.23% a 14.43%).

#### Interpretación:
El análisis muestra que los cinco productos más vendidos fueron adquiridos por alrededor del 14% de la base total de clientes, con valores muy cercanos entre sí. Esto indica que los productos no dependen de un grupo reducido de compradores que concentren las ventas, sino que fueron ampliamente adoptados de forma consistente por una fracción significativa de clientes. La variación mínima entre productos sugiere que todos lograron un alcance similar y que no hay un caso particular de concentración en un segmento específico. En conclusión, el comportamiento observado refleja una distribución equilibrada de la demanda, donde cada producto gozó de aceptación generalizada dentro del mercado, más que de compras intensivas de pocos clientes.

---

### PREGUNTA 3: Análisis por Categorías

#### Resultado: Porcentaje que representa cada producto dentro de su categoría
Al observar su peso relativo dentro de cada categoría, se evidencia que la participación es **baja: ninguno de los productos supera el 3%** del total de unidades vendidas en su categoría, con valores que oscilan entre el 2.04% y el 2.85%.

#### Interpretación:
Al observar su peso relativo dentro de cada categoría, se evidencia que la participación es baja: ninguno de los productos supera el 3% del total de unidades vendidas en su categoría, con valores que oscilan entre el 2.04% y el 2.85%. Esto sugiere que, si bien estos artículos ocupan la primera posición en su categoría (ranking 1 en todos los casos), su dominio no es absoluto, sino que comparten protagonismo con una gran diversidad de productos que, en conjunto, representan la mayor parte de las ventas. En otras palabras, ser el producto más vendido no implica que concentre un volumen significativo dentro de la categoría, sino más bien que sobresale en un mercado fragmentado y competitivo. La comparación entre categorías también confirma esta idea: todas presentan un escenario similar, donde el producto líder apenas aporta una pequeña fracción del total.

---

### PREGUNTA 4: Top 10 Productos del Catálogo Completo

#### Resultado: Ranking de cada producto dentro de su categoría
El análisis muestra que los diez productos con mayor cantidad de unidades vendidas provienen de categorías variadas como Seafood, Snails, Poultry, Beverages, Meat, Produce y Dairy. **La mayoría de ellos ocupan la posición número 1 en su respectiva categoría**, lo que confirma que no solo son líderes en el ranking global de ventas, sino que también encabezan el desempeño dentro de su segmento.

Sin embargo, en algunos casos específicos —**como Apricots - Dried en la categoría Snails o Hersey Shakes en Poultry— aparecen en la posición número 2**, lo que refleja que, si bien tienen un volumen de ventas elevado, compiten estrechamente con otros productos que alcanzan cifras similares.

#### Interpretación:
El análisis muestra que los diez productos con mayor cantidad de unidades vendidas provienen de categorías variadas como Seafood, Snails, Poultry, Beverages, Meat, Produce y Dairy. La mayoría de ellos ocupan la posición número 1 en su respectiva categoría, lo que confirma que no solo son líderes en el ranking global de ventas, sino que también encabezan el desempeño dentro de su segmento. Sin embargo, en algunos casos específicos —como Apricots - Dried en la categoría Snails o Hersey Shakes en Poultry— aparecen en la posición número 2, lo que refleja que, si bien tienen un volumen de ventas elevado, compiten estrechamente con otros productos que alcanzan cifras similares.

Un aspecto relevante es la cantidad de productos dentro de cada categoría: mientras algunas como Meat (50 productos) o Poultry (47 productos) son más amplias, otras como Dairy (35 productos) o Seafood (36 productos) tienen una oferta algo más acotada. Esto influye en la concentración: un product top en una categoría pequeña puede tener un peso proporcional mayor que en una categoría muy diversa, donde las ventas se distribuyen entre más artículos.

En términos de concentración, los datos sugieren que la mayoría de las categorías presentan una distribución amplia y fragmentada, donde los productos líderes no acaparan de manera decisiva las ventas, sino que se destacan apenas por encima de competidores cercanos. El caso de Apricots - Dried y Hersey Shakes ejemplifica cómo incluso entre los más vendidos a nivel global, la supremacía dentro de la categoría no está asegurada, mostrando un mercado interno competitivo.

---

## CONCLUSIÓN GENERAL

El análisis integral refleja que los productos más vendidos destacan por su relevancia en términos de volumen y liderazgo dentro de sus categorías, pero lo hacen en un contexto de **baja concentración**: 

- ✅ Ningún vendedor individual supera el 10% de las ventas
- ✅ La adopción por clientes es amplia y consistente (alrededor del 14% de la base total)
- ✅ La participación relativa en las categorías no supera el 3%

Esto evidencia un **mercado diversificado y competitivo**, donde existen actores y productos destacados —como el caso de Devon Brewer en dos artículos— pero sin que ello genere dependencia excesiva de un único vendedor, cliente o producto. En conjunto, los resultados muestran un portafolio equilibrado, con riesgos de concentración reducidos y una distribución de la demanda que aporta solidez y sostenibilidad al negocio.

---

## ARCHIVOS INCLUÍDOS

1. **codigo.sql**: Script completo con todas las consultas SQL desarrolladas
2. **Interpretación.docx**: Documento con capturas de pantalla y análisis detallado de resultados
3. **README.md**: Este archivo con resumen ejecutivo y documentación completa del proyecto

---

*Proyecto Integrador - Avance 1*  
*Módulo: Carga y exploración de datos en SQL*

