-- Create the operational database and normalized OLTP schema.
CREATE DATABASE LicentaDWH_OLTP;
GO

USE LicentaDWH_OLTP;
GO

CREATE SCHEMA oltp;
GO

CREATE TABLE oltp.Categories (
    CategoryID INT NOT NULL PRIMARY KEY,
    CategoryName NVARCHAR(100) NOT NULL UNIQUE
);
GO

CREATE TABLE oltp.Stores (
    StoreID INT NOT NULL PRIMARY KEY,
    StoreName NVARCHAR(100) NOT NULL,
    City NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE oltp.Customers (
    CustomerID INT NOT NULL PRIMARY KEY,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    City NVARCHAR(100) NOT NULL,
    SignupDate DATE NOT NULL
);
GO

CREATE TABLE oltp.Products (
    ProductID INT NOT NULL PRIMARY KEY,
    ProductName NVARCHAR(100) NOT NULL,
    CategoryID INT NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    CONSTRAINT FK_Products_Categories
        FOREIGN KEY (CategoryID) REFERENCES oltp.Categories(CategoryID),
    CONSTRAINT CK_Products_Price CHECK (Price > 0)
);
GO

CREATE TABLE oltp.Orders (
    OrderID INT NOT NULL PRIMARY KEY,
    CustomerID INT NOT NULL,
    StoreID INT NOT NULL,
    OrderDate DATE NOT NULL,
    Status NVARCHAR(20) NOT NULL,
    CONSTRAINT FK_Orders_Customers
        FOREIGN KEY (CustomerID) REFERENCES oltp.Customers(CustomerID),
    CONSTRAINT FK_Orders_Stores
        FOREIGN KEY (StoreID) REFERENCES oltp.Stores(StoreID),
    CONSTRAINT CK_Orders_Status CHECK (Status IN ('Completed', 'Pending', 'Cancelled'))
);
GO

CREATE TABLE oltp.OrderItems (
    OrderItemID INT NOT NULL PRIMARY KEY,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    Discount DECIMAL(5,4) NOT NULL,
    CONSTRAINT FK_OrderItems_Orders
        FOREIGN KEY (OrderID) REFERENCES oltp.Orders(OrderID),
    CONSTRAINT FK_OrderItems_Products
        FOREIGN KEY (ProductID) REFERENCES oltp.Products(ProductID),
    CONSTRAINT CK_OrderItems_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_OrderItems_UnitPrice CHECK (UnitPrice > 0),
    CONSTRAINT CK_OrderItems_Discount CHECK (Discount >= 0 AND Discount <= 1)
);
GO

CREATE INDEX IX_Orders_CustomerID ON oltp.Orders(CustomerID);
CREATE INDEX IX_Orders_StoreID ON oltp.Orders(StoreID);
CREATE INDEX IX_OrderItems_OrderID ON oltp.OrderItems(OrderID);
CREATE INDEX IX_OrderItems_ProductID ON oltp.OrderItems(ProductID);
GO
