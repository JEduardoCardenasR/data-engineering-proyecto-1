
CREATE TABLE monitoreo (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    ProductId INT,
    ProductName VARCHAR(255),
    TotalVendido INT,
    FechaRegistro DATETIME DEFAULT CURRENT_TIMESTAMP
);

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
    ) VALUES 
    (
    99999999999999999, 
    8, 
    70, 
    103, 
    1880, 
    0.00,
    1200.00,
    CURRENT_TIMESTAMP, 
    'TX999991234567890'
);

SELECT * 
FROM sales
WHERE "SalesID" = 99999999999999999;

SELECT * FROM monitoreo;