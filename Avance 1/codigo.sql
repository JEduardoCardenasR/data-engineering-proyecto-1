-- ===========================================
-- PROYECTO INTEGRADOR - AVANCE 1
-- Análisis de datos de ventas con SQL
-- ===========================================

-- ===========================================
-- PREGUNTA 1: 5 Productos Más Vendidos y sus Vendedores Principales
-- ===========================================

-- Consulta 1.1: Los 5 productos más vendidos
-- Identifica los productos con mayor cantidad de unidades vendidas en total
SELECT s.ProductID, p.ProductName, SUM(s.Quantity) AS TotalQuantity
FROM products AS p
JOIN sales AS s 
ON p.ProductID = s.ProductID
GROUP BY s.ProductID, p.ProductName
ORDER BY TotalQuantity DESC
LIMIT 5;

-- Consulta 1.2: Vendedores que más vendieron de cada producto top
-- Encuentra el vendedor principal para cada uno de los 5 productos más vendidos
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

-- Consulta 1.3: Análisis de vendedores que superaron el 10% de ventas
-- Crea tablas temporales para analizar si algún vendedor supera el 10% de ventas de cada producto top
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

-- Consulta final: Muestra si el vendedor principal supera el 10% de ventas
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

-- ===========================================
-- PREGUNTA 2: Análisis de Clientes Únicos
-- ===========================================

-- Consulta 2.1: Clientes únicos por producto top 5
-- Cuenta cuántos clientes únicos compraron cada uno de los productos más vendidos
SELECT 
    s.ProductID,
    tp.ProductName,
    COUNT(DISTINCT s.CustomerID) as ClientesUnicos
FROM sales s
JOIN TopProducts tp ON s.ProductID = tp.ProductID
GROUP BY s.ProductID, tp.ProductName
ORDER BY ClientesUnicos DESC;

-- Consulta 2.2: Proporción de clientes sobre el total
-- Calcula qué porcentaje de la base total de clientes compró cada producto top
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

-- ===========================================
-- PREGUNTA 3: Análisis por Categorías
-- ===========================================

-- Consulta 3.1: Categorías de productos top 5 y su relevancia
-- Analiza qué porcentaje representa cada producto top dentro de su categoría
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

-- ===========================================
-- PREGUNTA 4: Top 10 Productos del Catálogo Completo
-- ===========================================

-- Consulta 4.1: Top 10 productos con categoría
-- Identifica los 10 productos más vendidos de todo el catálogo con su categoría
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

-- Consulta 4.2: Ranking de productos dentro de sus categorías
-- Determina la posición de cada producto top 10 dentro de su respectiva categoría
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

-- Consulta final: Muestra el ranking de cada producto top 10 en su categoría
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

-- ===========================================
-- LIMPIEZA DE TABLAS TEMPORALES
-- ===========================================

-- Eliminar tablas temporales creadas durante el análisis
DROP TABLE IF EXISTS TopProducts;
DROP TABLE IF EXISTS VendedorRanking;
DROP TABLE IF EXISTS Top10Productos;
DROP TABLE IF EXISTS ConRankingEnCategoria;