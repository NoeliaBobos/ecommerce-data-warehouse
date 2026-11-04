USE Ecommerce_DWH;
GO

-- ========================
-- KPI 1: Total Revenue
-- ========================
SELECT 
    SUM(Revenue) AS TotalRevenue
FROM dwh.FactSales;
GO

-- ========================
-- KPI 2: Monthly Revenue
-- ========================
SELECT
    dd.YearNumber,
    dd.MonthNumber,
    dd.MonthName,
    SUM(fs.Revenue) AS MonthlyRevenue
FROM dwh.FactSales fs
JOIN dwh.DimDate dd
    ON fs.DateKey = dd.DateKey
GROUP BY
    dd.YearNumber,
    dd.MonthNumber,
    dd.MonthName
ORDER BY
    dd.YearNumber,
    dd.MonthNumber;
GO

-- ========================
-- KPI 3: Top Products by Revenue
-- ========================
SELECT TOP 10
    dp.ProductName,
    SUM(fs.Revenue) AS TotalRevenue
FROM dwh.FactSales fs
JOIN dwh.DimProduct dp
    ON fs.ProductKey = dp.ProductKey
GROUP BY
    dp.ProductName
ORDER BY
    TotalRevenue DESC;
GO

-- ========================
-- KPI 4: Top Cities by Revenue
-- ========================
SELECT
    ds.City,
    SUM(fs.Revenue) AS TotalRevenue
FROM dwh.FactSales fs
JOIN dwh.DimStore ds
    ON fs.StoreKey = ds.StoreKey
GROUP BY
    ds.City
ORDER BY
    TotalRevenue DESC;
GO

-- ========================
-- KPI 5: Average Order Value
-- ========================
SELECT 
    CAST(ROUND(AVG(OrderTotal), 2) AS DECIMAL(18,2)) AS AverageOrderValue
FROM (
    SELECT 
        OrderID,
        SUM(Revenue) AS OrderTotal
    FROM dwh.FactSales
    GROUP BY OrderID
) t;
GO