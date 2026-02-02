USE master;
GO
DROP DATABASE IF EXISTS LAB6;
GO
CREATE DATABASE LAB6;
GO
USE LAB6;
GO

-- 1. Table with auto incrementing IDENTITY

CREATE TABLE Products (
    ProductID INT IDENTITY(1,1) PRIMARY KEY,
    ProductName NVARCHAR(100) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    CreatedDate DATETIME2 DEFAULT GETDATE()
);
GO


-- 2. Add fields with CHECK constraints and DEFAULT values and functions
ALTER TABLE Products
ADD
    Quantity INT NOT NULL DEFAULT 0,
    Discount DECIMAL(5,2) DEFAULT 0 CHECK (Discount BETWEEN 0 AND 50),
    LastModified DATETIME2 DEFAULT GETDATE(),
    Status NVARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive', 'Discontinued')),
    TotalValue AS (Price * Quantity * (1 - Discount/100)) PERSISTED;
GO


-- 3. Table with GUID primary key
CREATE TABLE Customers (
    CustomerID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CustomerName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(100),
    RegistrationDate DATETIME2 DEFAULT GETDATE()
);
GO


-- 4. Table with sequence primary key

-- Create sequence
CREATE SEQUENCE OrderSequence
    AS INT
    START WITH 1000
    INCREMENT BY 1
    MINVALUE 1000
    MAXVALUE 9999
    CYCLE;
GO

-- Table using sequence
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY DEFAULT (NEXT VALUE FOR OrderSequence),
    CustomerID UNIQUEIDENTIFIER,
    OrderDate DATETIME2 DEFAULT GETDATE(),
    TotalAmount INT,
);
GO

-- 5. FK constraints

CREATE TABLE Categories (
    CategoryID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CategoryName NVARCHAR(50) NOT NULL,
    Description NVARCHAR(255)
);
GO


CREATE SEQUENCE MySeq START WITH 1 INCREMENT BY 1;

CREATE TABLE Suppliers (
    SupplierID INT DEFAULT NEXT VALUE FOR MySeq PRIMARY KEY,
    SupplierName NVARCHAR(100) NOT NULL,
    ContactEmail NVARCHAR(100)
);
GO

-- Insert a default supplier
INSERT INTO Suppliers (SupplierName, ContactEmail) VALUES
('DEFAULT SUPPLIER', 'china@qq.com');
GO

-- Create table Goods
CREATE TABLE Goods (
    GoodID INT IDENTITY(1,1) PRIMARY KEY,
    GoodName NVARCHAR(100) NOT NULL,
    CategoryID UNIQUEIDENTIFIER,
    SupplierID INT DEFAULT 1,
    Price DECIMAL(10,2) NOT NULL,

    CONSTRAINT FK_Goods_Category
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
    ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT FK_Goods_Supplier
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
    ON DELETE SET DEFAULT ON UPDATE NO ACTION
);
GO


---------------------------------------------------------
-- PREPARE TEST DATA
---------------------------------------------------------

-- Insert categories
INSERT INTO Categories (CategoryName, Description)
VALUES ('Electronics', 'Phones, laptops'),
       ('Food', 'Groceries');
GO
-- Insert suppliers
INSERT INTO Suppliers (SupplierName, ContactEmail)
VALUES ('Supplier A', 'a@test.com'),
       ('Supplier B', 'b@test.com');
GO

-- Insert goods
DECLARE @ELECTRONICS_CATEGORY UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Electronics');
DECLARE @FOOD_CATEGORY UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Food');
INSERT INTO Goods (GoodName, CategoryID, SupplierID, Price)
VALUES
('iPhone', @ELECTRONICS_CATEGORY, 2, 999.99),
('Bread', @FOOD_CATEGORY, 3, 2.99),     -- Using Supplier B
('Laptop', @ELECTRONICS_CATEGORY, NULL, 1500); -- Category exists, supplier NULL (default will kick if needed)
GO

-- Check goods
SELECT * FROM Goods;
GO


-- TEST 1 — Category FK (ON DELETE SET NULL)

-- DELETE CategoryID = 1 (Electronics)
DECLARE @ELECTRONICS_CATEGORY UNIQUEIDENTIFIER = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Electronics');
DELETE FROM Categories WHERE CategoryID = @ELECTRONICS_CATEGORY;
GO

-- Check result
SELECT * FROM Goods;
GO

-- TEST 2 — Category FK (ON UPDATE CASCADE)
UPDATE Categories SET CategoryID = NEWID() WHERE CategoryName = 'Food';
GO

-- Check result
SELECT * FROM Goods;
GO

-- TEST 3 — Supplier FK (ON DELETE SET DEFAULT)
DELETE FROM Suppliers WHERE SupplierID = 2;
GO

-- Check result
SELECT * FROM Goods;
GO

-- TEST 4 — Supplier FK (ON UPDATE NO ACTION)
-- This will be an error
UPDATE Suppliers SET SupplierID = 500 WHERE SupplierID = 1;
GO