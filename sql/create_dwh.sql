-- Create the analytical database and Star Schema.
CREATE DATABASE LicentaDWH_DWH;
GO

USE LicentaDWH_DWH;
GO

CREATE SCHEMA dwh;
GO

CREATE TABLE dwh.DimDate (
    DateKey INT NOT NULL PRIMARY KEY,
    FullDate DATE NOT NULL UNIQUE,
    DayNumber TINYINT NOT NULL,
    MonthNumber TINYINT NOT NULL,
    MonthName NVARCHAR(20) NOT NULL,
    QuarterNumber TINYINT NOT NULL,
    YearNumber SMALLINT NOT NULL
);
GO

CREATE TABLE dwh.DimCustomer (
    CustomerKey INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    CustomerID INT NOT NULL UNIQUE,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(255) NOT NULL,
    City NVARCHAR(100) NOT NULL,
    SignupDate DATE NOT NULL
);
GO

CREATE TABLE dwh.DimProduct (
    ProductKey INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    ProductID INT NOT NULL UNIQUE,
    ProductName NVARCHAR(100) NOT NULL,
    CategoryName NVARCHAR(100) NOT NULL,
    Price DECIMAL(10,2) NOT NULL
);
GO

CREATE TABLE dwh.DimStore (
    StoreKey INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    StoreID INT NOT NULL UNIQUE,
    StoreName NVARCHAR(100) NOT NULL,
    City NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE dwh.FactSales (
    SalesKey BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    DateKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    ProductKey INT NOT NULL,
    StoreKey INT NOT NULL,
    OrderID INT NOT NULL,
    OrderItemID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    Discount DECIMAL(5,4) NOT NULL,
    Revenue DECIMAL(18,2) NOT NULL,
    CONSTRAINT FK_FactSales_DimDate
        FOREIGN KEY (DateKey) REFERENCES dwh.DimDate(DateKey),
    CONSTRAINT FK_FactSales_DimCustomer
        FOREIGN KEY (CustomerKey) REFERENCES dwh.DimCustomer(CustomerKey),
    CONSTRAINT FK_FactSales_DimProduct
        FOREIGN KEY (ProductKey) REFERENCES dwh.DimProduct(ProductKey),
    CONSTRAINT FK_FactSales_DimStore
        FOREIGN KEY (StoreKey) REFERENCES dwh.DimStore(StoreKey),
    CONSTRAINT UQ_FactSales_OrderItemID UNIQUE (OrderItemID),
    CONSTRAINT CK_FactSales_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_FactSales_Discount CHECK (Discount >= 0 AND Discount <= 1)
);
GO

CREATE INDEX IX_FactSales_DateKey ON dwh.FactSales(DateKey);
CREATE INDEX IX_FactSales_CustomerKey ON dwh.FactSales(CustomerKey);
CREATE INDEX IX_FactSales_ProductKey ON dwh.FactSales(ProductKey);
CREATE INDEX IX_FactSales_StoreKey ON dwh.FactSales(StoreKey);
GO
