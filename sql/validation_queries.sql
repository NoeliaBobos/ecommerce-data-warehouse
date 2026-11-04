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
-- 6. Check for NULL values in FactSales
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
-- 7. Check revenue calculations
-- ========================
SELECT TOP 10
    Quantity,
    UnitPrice,
    Revenue,
    (Quantity * UnitPrice) AS CalculatedRevenue
FROM dwh.FactSales;
GO

-- ========================
-- 8. Check foreign-key integrity (orphan rows)
-- ========================
SELECT *
FROM dwh.FactSales fs
LEFT JOIN dwh.DimCustomer dc ON fs.CustomerKey = dc.CustomerKey
WHERE dc.CustomerKey IS NULL;
GO

-- ========================
-- 9. FactSales contains completed orders only
-- Expected result: 0 rows.
-- ========================
SELECT COUNT(*) AS NonCompletedOrderItemsInFactSales
FROM dwh.FactSales AS fs
INNER JOIN [Ecommerce_OLTP].oltp.Orders AS o
    ON fs.OrderID = o.OrderID
WHERE o.Status <> 'Completed';
GO

-- ========================
-- 10. Compare loaded fact rows with completed source order items
-- The two counts should match after the OLTP -> DWH load.
-- ========================
SELECT COUNT(*) AS CompletedOrderItemsExpected
FROM [Ecommerce_OLTP].oltp.Orders AS o
INNER JOIN [Ecommerce_OLTP].oltp.OrderItems AS oi
    ON o.OrderID = oi.OrderID
WHERE o.Status = 'Completed';
GO

SELECT COUNT(*) AS FactSalesRowsLoaded
FROM dwh.FactSales;
GO
