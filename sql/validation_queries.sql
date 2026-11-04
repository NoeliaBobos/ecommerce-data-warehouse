USE Ecommerce_DWH;
GO

-- ========================
-- 1. Row count FactSales
-- ========================
SELECT COUNT(*) AS FactSalesCount
FROM dwh.FactSales;
GO

-- ========================
-- 2. Row count DimCustomer
-- ========================
SELECT COUNT(*) AS DimCustomerCount
FROM dwh.DimCustomer;
GO

-- ========================
-- 3. Row count DimProduct
-- ========================
SELECT COUNT(*) AS DimProductCount
FROM dwh.DimProduct;
GO

-- ========================
-- 4. Row count DimStore
-- ========================
SELECT COUNT(*) AS DimStoreCount
FROM dwh.DimStore;
GO

-- ========================
-- 5. Row count DimDate
-- ========================
SELECT COUNT(*) AS DimDateCount
FROM dwh.DimDate;
GO

-- ========================
-- 6. Verificare valori NULL în FactSales
-- ========================
SELECT *
FROM dwh.FactSales
WHERE
    DateKey IS NULL
    OR CustomerKey IS NULL
    OR ProductKey IS NULL
    OR StoreKey IS NULL;
GO

-- ========================
-- 7. Verificare Revenue calcul corect
-- ========================
SELECT TOP 10
    Quantity,
    UnitPrice,
    Revenue,
    (Quantity * UnitPrice) AS CalculatedRevenue
FROM dwh.FactSales;
GO

-- ========================
-- 8. Verificare FK-uri (orphan check)
-- ========================
SELECT *
FROM dwh.FactSales fs
LEFT JOIN dwh.DimCustomer dc ON fs.CustomerKey = dc.CustomerKey
WHERE dc.CustomerKey IS NULL;
GO