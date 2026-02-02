USE master;
GO

DROP DATABASE IF EXISTS LAB13_A;
GO
DROP DATABASE IF EXISTS LAB13_B;
GO
CREATE DATABASE LAB13_A;
GO
CREATE DATABASE LAB13_B;
GO



-- 2

-- Part 1: ID 1..49999
USE LAB13_A;
GO
CREATE TABLE dbo.Customers_P1
(
    CustomerID INT NOT NULL
        CONSTRAINT PK_Customers_P1 PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    City NVARCHAR(100) NULL,
    CONSTRAINT CK_Customers_P1_Range CHECK (CustomerID BETWEEN 1 AND 49999)
);
GO

-- Part 2: ID 50000..99999
USE LAB13_B;
GO
CREATE TABLE dbo.Customers_P2
(
    CustomerID INT NOT NULL
        CONSTRAINT PK_Customers_P2 PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    City NVARCHAR(100) NULL,
    CONSTRAINT CK_Customers_P2_Range CHECK (CustomerID BETWEEN 50000 AND 99999)
);
GO



-- 3. VIEW

USE LAB13_A;
GO
CREATE VIEW dbo.Customers
AS
    SELECT CustomerID, Name, City FROM LAB13_A.dbo.Customers_P1
    UNION ALL
    SELECT CustomerID, Name, City FROM LAB13_B.dbo.Customers_P2;
GO



--- Select

SELECT * FROM LAB13_A.dbo.Customers WHERE CustomerID IN (10, 60000);

-- Insert
INSERT INTO LAB13_A.dbo.Customers (CustomerID, Name, City)
VALUES
 (10,     N'Иван', N'Томск'),     -- должен уйти в LAB13_A..Customers_P1 (1..49999)
 (70000,  N'Анна', N'Казань');    -- должен уйти в LAB13_B..Customers_P2 (50000..99999)

-- UPDATE LAB13_A.dbo.Customers
-- SET CustomerID = 70001
-- WHERE CustomerID = 10;
--
-- Select * from LAB13_A.dbo.Customers_P1;
-- Select * from LAB13_B.dbo.Customers_P2;

-- Update

UPDATE LAB13_A.dbo.Customers
SET City = N'Москва'
WHERE CustomerID = 70000;


SELECT *
FROM LAB13_A.dbo.Customers
WHERE CustomerID = 70000;

-- Delete
DELETE FROM LAB13_A.dbo.Customers
WHERE CustomerID = 10;

SELECT *
FROM LAB13_A.dbo.Customers
WHERE CustomerID = 10;
