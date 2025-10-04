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