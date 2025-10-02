-- 5 productos más vendidos

SELECT s.ProductID, p.ProductName, SUM(s.Quantity) AS TotalQuantity
FROM products AS p
JOIN sales AS s 
ON p.ProductID = s.ProductID
GROUP BY s.ProductID, p.ProductName
ORDER BY TotalQuantity DESC
LIMIT 5;

-- Vendedores que más vendieron los 5 productos más vendidos

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

-- Vendedores que superaron el 10% de ventas en los 5 productos más vendidos con tablas temporales

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

SELECT * FROM VendedorPorProducto;
SELECT * FROM VendedorRanking;

DROP TABLE VendedorRanking;