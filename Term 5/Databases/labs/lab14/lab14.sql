USE master;
GO


DROP DATABASE IF EXISTS LAB14_A;
GO
DROP DATABASE IF EXISTS LAB14_B;
GO

/* 1) Create databases */
CREATE DATABASE LAB14_A;
GO
CREATE DATABASE LAB14_B;
GO

/* 2) Create vertically fragmented tables */

/* Fragment A: keys + Name */
USE LAB14_A;
GO

CREATE TABLE dbo.Customers_A
(
    CustomerID INT NOT NULL CONSTRAINT PK_Customers_A PRIMARY KEY,
    Name       NVARCHAR(100) NOT NULL
);
GO

/* Fragment B: keys + City */
USE LAB14_B;
GO

CREATE TABLE dbo.Customers_B
(
    CustomerID INT NOT NULL CONSTRAINT PK_Customers_B PRIMARY KEY,
    City       NVARCHAR(100) NULL
);
GO

/* 3) Create JOIN view in LAB14_A */
USE LAB14_A;
GO

CREATE VIEW dbo.Customers_V
AS
    SELECT
        a.CustomerID,
        a.Name,
        b.City
    FROM LAB14_A.dbo.Customers_A a
    INNER JOIN LAB14_B.dbo.Customers_B b
        ON b.CustomerID = a.CustomerID;
GO

/* 4) Triggers to support INSERT/UPDATE/DELETE through the VIEW */

/* 4.1 INSTEAD OF INSERT */
CREATE TRIGGER dbo.tr_Customers_V_I
ON dbo.Customers_V
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO LAB14_A.dbo.Customers_A (CustomerID, Name)
    SELECT i.CustomerID, i.Name
    FROM inserted i;

    INSERT INTO LAB14_B.dbo.Customers_B (CustomerID, City)
    SELECT i.CustomerID, i.City
    FROM inserted i;
END
GO

/* 4.2 INSTEAD OF UPDATE */
CREATE TRIGGER dbo.tr_Customers_V_U
ON dbo.Customers_V
INSTEAD OF UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(CustomerID)
    BEGIN
        RAISERROR(N'Нельзя изменять CustomerID (ключ связи фрагментов).', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END

    IF UPDATE(Name)
    BEGIN
        UPDATE a
        SET a.Name = i.Name
        FROM LAB14_A.dbo.Customers_A a
        INNER JOIN inserted i ON i.CustomerID = a.CustomerID;
    END

    IF UPDATE(City)
    BEGIN
        UPDATE b
        SET b.City = i.City
        FROM LAB14_B.dbo.Customers_B b
        INNER JOIN inserted i ON i.CustomerID = b.CustomerID;
    END
END
GO

/* 4.3 INSTEAD OF DELETE */
CREATE TRIGGER dbo.tr_Customers_V_D
ON dbo.Customers_V
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;

    DELETE b
    FROM LAB14_B.dbo.Customers_B b
    INNER JOIN deleted d ON d.CustomerID = b.CustomerID;

    DELETE a
    FROM LAB14_A.dbo.Customers_A a
    INNER JOIN deleted d ON d.CustomerID = a.CustomerID;
END
GO

/* 5) Test CRUD operations with the VIEW */

/* SELECT (empty) */
SELECT * FROM LAB14_A.dbo.Customers_V;
GO

/* INSERT через VIEW */
INSERT INTO LAB14_A.dbo.Customers_V (CustomerID, Name, City)
VALUES
 (10,    N'Иван', N'Томск'),
 (70000, N'Анна', N'Казань');
GO

/* SELECT через VIEW */
SELECT * FROM LAB14_A.dbo.Customers_V
WHERE CustomerID IN (10, 70000);
GO

/* UPDATE через VIEW */
UPDATE LAB14_A.dbo.Customers_V
SET City = N'Москва'
WHERE CustomerID = 70000;
GO

SELECT * FROM LAB14_A.dbo.Customers_V
WHERE CustomerID = 70000;
GO

/* DELETE через VIEW */
DELETE FROM LAB14_A.dbo.Customers_V
WHERE CustomerID = 10;
GO

SELECT * FROM LAB14_A.dbo.Customers_V
WHERE CustomerID = 10;
GO
