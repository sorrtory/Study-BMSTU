USE master;
GO

DROP DATABASE IF EXISTS LAB15_A;
GO
DROP DATABASE IF EXISTS LAB15_B;
GO

CREATE DATABASE LAB15_A;
GO
CREATE DATABASE LAB15_B;
GO


--   1) Создать "связанные таблицы" в двух БД
--      LAB15_A: Customers (родитель)
--      LAB15_B: Orders (дочерняя, логически ссылается на Customers.CustomerID)

USE LAB15_A;
GO

CREATE TABLE dbo.Customers
(
    CustomerID INT NOT NULL CONSTRAINT PK_Customers PRIMARY KEY,
    Name       NVARCHAR(100) NOT NULL
);
GO

USE LAB15_B;
GO

CREATE TABLE dbo.Orders
(
    OrderID    INT NOT NULL CONSTRAINT PK_Orders PRIMARY KEY,
    CustomerID INT NOT NULL,         -- логический FK на LAB15_A..Customers(CustomerID)
    Amount     DECIMAL(12,2) NOT NULL,
    OrderDate  DATE NOT NULL
);
GO


--   2) Представление + триггеры для работы со связанными таблицами
--      Всё делаем в LAB15_A (единая точка доступа)

USE LAB15_A;
GO

/* VIEW: объединяет данные из двух БД */
CREATE VIEW dbo.CustomerOrders_V
AS
SELECT
    c.CustomerID,
    c.Name,
    o.OrderID,
    o.Amount,
    o.OrderDate
FROM LAB15_A.dbo.Customers c
INNER JOIN LAB15_B.dbo.Orders o
    ON o.CustomerID = c.CustomerID;
GO

/* INSERT через VIEW:
   - если клиента нет -> ошибка
   - создаём заказ в LAB15_B
*/
CREATE TRIGGER dbo.tr_CustomerOrders_V_I
ON dbo.CustomerOrders_V
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1
        FROM inserted i
        LEFT JOIN LAB15_A.dbo.Customers c ON c.CustomerID = i.CustomerID
        WHERE c.CustomerID IS NULL
    )
    BEGIN
        RAISERROR(N'Сначала добавьте клиента в LAB15_A.dbo.Customers, затем вставляйте заказ через VIEW.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END

    INSERT INTO LAB15_B.dbo.Orders (OrderID, CustomerID, Amount, OrderDate)
    SELECT i.OrderID, i.CustomerID, i.Amount, i.OrderDate
    FROM inserted i;
END
GO

/* UPDATE через VIEW:
   - запрещаем менять ключи CustomerID/OrderID
   - Name -> LAB15_A..Customers
   - Amount/OrderDate -> LAB15_B..Orders
*/
CREATE TRIGGER dbo.tr_CustomerOrders_V_U
ON dbo.CustomerOrders_V
INSTEAD OF UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(CustomerID) OR UPDATE(OrderID)
    BEGIN
        RAISERROR(N'Нельзя изменять CustomerID или OrderID через VIEW.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END

    IF UPDATE(Name)
    BEGIN
        UPDATE c
        SET c.Name = i.Name
        FROM LAB15_A.dbo.Customers c
        INNER JOIN inserted i ON i.CustomerID = c.CustomerID;
    END

    IF UPDATE(Amount) OR UPDATE(OrderDate)
    BEGIN
        UPDATE o
        SET
            o.Amount    = COALESCE(i.Amount, o.Amount),
            o.OrderDate = COALESCE(i.OrderDate, o.OrderDate)
        FROM LAB15_B.dbo.Orders o
        INNER JOIN inserted i ON i.OrderID = o.OrderID;
    END
END
GO

/* DELETE через VIEW:
   - удаляем заказ из LAB15_B
*/
CREATE TRIGGER dbo.tr_CustomerOrders_V_D
ON dbo.CustomerOrders_V
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;

    DELETE o
    FROM LAB15_B.dbo.Orders o
    INNER JOIN deleted d ON d.OrderID = o.OrderID;
END
GO

--   ТЕСТЫ: работа только через VIEW (и отдельное создание клиентов)

-- Создаём клиентов (обычно это отдельная операция администрирования)
INSERT INTO LAB15_A.dbo.Customers (CustomerID, Name)
VALUES (1, N'Иван'), (2, N'Анна');
GO

-- INSERT заказа через VIEW
INSERT INTO LAB15_A.dbo.CustomerOrders_V (CustomerID, Name, OrderID, Amount, OrderDate)
VALUES (1, N'Иван', 1001, 2500.00, '2025-12-17');
GO

-- SELECT через VIEW
SELECT * FROM LAB15_A.dbo.CustomerOrders_V;
GO

-- UPDATE через VIEW
UPDATE LAB15_A.dbo.CustomerOrders_V
SET Amount = 3000.00, OrderDate = '2025-12-18', Name = N'Иван П.'
WHERE OrderID = 1001;
GO

SELECT * FROM LAB15_A.dbo.CustomerOrders_V WHERE OrderID = 1001;
GO

-- DELETE через VIEW
DELETE FROM LAB15_A.dbo.CustomerOrders_V
WHERE OrderID = 1001;
GO

SELECT * FROM LAB15_A.dbo.CustomerOrders_V WHERE OrderID = 1001;
GO
