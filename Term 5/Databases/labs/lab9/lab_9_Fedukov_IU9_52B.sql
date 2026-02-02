USE master;
GO

DROP DATABASE IF EXISTS LAB9;
GO
CREATE DATABASE LAB9;
GO
USE LAB9;

DROP TRIGGER IF EXISTS dbo.trg_Lab9_Employee_Insert;
DROP TRIGGER IF EXISTS dbo.trg_Lab9_Employee_Update;
DROP TRIGGER IF EXISTS dbo.trg_Lab9_Employee_Delete;

DROP TRIGGER IF EXISTS dbo.trg_vLab9_Employee_Insert;
DROP TRIGGER IF EXISTS dbo.trg_vLab9_Employee_Update;
DROP TRIGGER IF EXISTS dbo.trg_vLab9_Employee_Delete;

DROP VIEW IF EXISTS dbo.vLab9_Employee;
DROP TABLE IF EXISTS dbo.Lab9_Employee;
DROP TABLE IF EXISTS dbo.Lab9_Department;
GO

DROP TRIGGER IF EXISTS dbo.trg_vLab9_Employee_1to1_Insert;
DROP TRIGGER IF EXISTS dbo.trg_vLab9_Employee_1to1_Update;
DROP TRIGGER IF EXISTS dbo.trg_vLab9_Employee_1to1_Delete;

DROP VIEW IF EXISTS dbo.vLab9_Employee_1to1;
DROP TABLE IF EXISTS dbo.Lab9_EmployeeDetails;
GO


-- Initial data
CREATE TABLE dbo.Lab9_Department
(
    DeptID   INT IDENTITY(1,1) CONSTRAINT PK_Lab9_Department PRIMARY KEY,
    DeptName NVARCHAR(100) NOT NULL UNIQUE
);
GO

CREATE TABLE dbo.Lab9_Employee
(
    EmployeeID INT IDENTITY(1,1) CONSTRAINT PK_Lab9_Employee PRIMARY KEY,
    FullName   NVARCHAR(100) NOT NULL,
    DeptID     INT NOT NULL CONSTRAINT FK_Lab9_Employee_Dept
        REFERENCES dbo.Lab9_Department(DeptID),
    Salary     DECIMAL(18,2) NOT NULL
        CONSTRAINT CK_Lab9_Employee_Salary CHECK (Salary >= 0)
);
GO

INSERT INTO dbo.Lab9_Department (DeptName)
VALUES (N'Отдел продаж'), (N'Бухгалтерия'), (N'IT');

INSERT INTO dbo.Lab9_Employee (FullName, DeptID, Salary)
SELECT N'Иванов Иван', DeptID, 60000 FROM dbo.Lab9_Department WHERE DeptName = N'Отдел продаж'
UNION ALL
SELECT N'Петров Петр', DeptID, 45000 FROM dbo.Lab9_Department WHERE DeptName = N'Бухгалтерия'
UNION ALL
SELECT N'Сидоров Сидор', DeptID, 80000 FROM dbo.Lab9_Department WHERE DeptName = N'IT';
GO

-- table for 1 to 1
CREATE TABLE dbo.Lab9_EmployeeDetails
(
    EmployeeID INT NOT NULL
        CONSTRAINT PK_Lab9_EmployeeDetails PRIMARY KEY
        CONSTRAINT FK_Lab9_EmployeeDetails_Employee
            REFERENCES dbo.Lab9_Employee(EmployeeID),
    Phone NVARCHAR(50)  NULL,
    Email NVARCHAR(100) NULL
);
GO

-- populate 1 to 1 table
INSERT INTO dbo.Lab9_EmployeeDetails (EmployeeID, Phone, Email)
SELECT 
    e.EmployeeID,
    N'+7-900-000-00-0' + CAST(e.EmployeeID AS NVARCHAR(10)),
    N'employee' + CAST(e.EmployeeID AS NVARCHAR(10)) + N'@example.com'
FROM dbo.Lab9_Employee e;
GO


-- 1. After triggers for Lab9_Employee table

-- inset trigger: salary must be >= 20000
CREATE TRIGGER dbo.trg_Lab9_Employee_Insert
ON dbo.Lab9_Employee
AFTER INSERT
AS
BEGIN
    IF EXISTS (
        SELECT 1
        FROM inserted
        WHERE Salary < 20000
    )
    BEGIN
        -- RAISERROR vs THROW
        -- https://learn.microsoft.com/en-us/sql/t-sql/language-elements/throw-transact-sql?view=sql-server-ver17#differences-between-raiserror-and-throw
        RAISERROR (N'Зарплата сотрудника не может быть ниже 20000.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;
END;
GO

-- update trigger: salary cannot be decreased below 20000
CREATE TRIGGER dbo.trg_Lab9_Employee_Update
ON dbo.Lab9_Employee
AFTER UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 1
        FROM inserted i
        JOIN deleted d ON i.EmployeeID = d.EmployeeID
        WHERE i.Salary < 20000
    )
    BEGIN
        RAISERROR (N'Нельзя уменьшать зарплату ниже 20000.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;
END;
GO

-- delete trigger: just log message
CREATE TRIGGER dbo.trg_Lab9_Employee_Delete
ON dbo.Lab9_Employee
AFTER DELETE
AS
BEGIN
    with deleted_count AS (
        SELECT COUNT(*) AS cnt FROM deleted
    )
    SELECT N'Удалено сотрудников: ' + CAST(cnt AS NVARCHAR(10)) FROM deleted_count;
END;
GO

-- 2. View with INSTEAD OF triggers

-- view for Lab9_Employee with DepartmentName
CREATE VIEW dbo.vLab9_Employee
AS
SELECT 
    e.EmployeeID,
    e.FullName,
    d.DeptName,
    e.Salary
FROM dbo.Lab9_Employee AS e
JOIN dbo.Lab9_Department AS d ON d.DeptID = e.DeptID;
GO

-- instead of insert trigger on the view
CREATE TRIGGER dbo.trg_vLab9_Employee_Insert
ON dbo.vLab9_Employee
INSTEAD OF INSERT
AS
BEGIN
    -- check existence of departments
    IF EXISTS (
        SELECT 1
        FROM inserted i
        LEFT JOIN dbo.Lab9_Department d -- left join to find missing departments
            ON d.DeptName = i.DeptName
        WHERE d.DeptID IS NULL -- keep only missing departments
    )
    BEGIN
        RAISERROR (N'Указан несуществующий отдел.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;

    -- insert employees
    INSERT INTO dbo.Lab9_Employee (FullName, DeptID, Salary)
    SELECT 
        i.FullName,
        d.DeptID,
        i.Salary
    FROM inserted i
    JOIN dbo.Lab9_Department d
        ON d.DeptName = i.DeptName;
END;
GO


-- instead of update trigger on the view
CREATE TRIGGER dbo.trg_vLab9_Employee_Update
ON dbo.vLab9_Employee
INSTEAD OF UPDATE
AS
BEGIN
    -- check existence of departments if DeptName is updated
    IF UPDATE(DeptName)
       AND EXISTS (
            SELECT 1
            FROM inserted i
            LEFT JOIN dbo.Lab9_Department d
                ON d.DeptName = i.DeptName
            WHERE d.DeptID IS NULL
       )
    BEGIN
        RAISERROR (N'Указан несуществующий отдел при обновлении.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;

    -- restrict EmployeeID changes
    IF UPDATE(EmployeeID)
    BEGIN
        RAISERROR('Нельзя изменять столбец EmployeeID через это представление.', 16, 1);
        ROLLBACK TRANSACTION;
    RETURN;
    END;

    -- update employees
    UPDATE e
    SET 
        e.FullName = ISNULL(i.FullName, e.FullName),
        e.Salary   = ISNULL(i.Salary,   e.Salary),
        e.DeptID   = ISNULL(d.DeptID,   e.DeptID)
    FROM dbo.Lab9_Employee e
    JOIN inserted i
        ON e.EmployeeID = i.EmployeeID
    LEFT JOIN dbo.Lab9_Department d
        ON d.DeptName = i.DeptName;
END;
GO

-- instead of delete trigger on the view
CREATE TRIGGER dbo.trg_vLab9_Employee_Delete
ON dbo.vLab9_Employee
INSTEAD OF DELETE
AS
BEGIN
    -- first delete details
    DELETE d
    FROM dbo.Lab9_EmployeeDetails d
    JOIN deleted x ON x.EmployeeID = d.EmployeeID;

    -- then the employee itself
    DELETE e
    FROM dbo.Lab9_Employee e
    JOIN deleted x ON x.EmployeeID = e.EmployeeID;
END;
GO

-- -- PROBLEM: Solved
-- select * from dbo.vLab9_Employee
-- update dbo.vLab9_Employee set EmployeeID = EmployeeID+1
-- select * from dbo.vLab9_Employee
-- GO

-- 3. dbo.vLab9_Employee_1to1 view with INSTEAD OF triggers
-- (join details and department to employee)

CREATE VIEW dbo.vLab9_Employee_1to1
AS
SELECT 
    e.EmployeeID,
    e.FullName,
    e.DeptID,
    e.Salary,
    d.Phone,
    d.Email
FROM dbo.Lab9_Employee       AS e
JOIN dbo.Lab9_EmployeeDetails AS d ON d.EmployeeID = e.EmployeeID
JOIN dbo.Lab9_Department AS dep ON dep.DeptID = e.DeptID;
GO

CREATE TRIGGER dbo.trg_vLab9_Employee_1to1_Insert
ON dbo.vLab9_Employee_1to1
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- staging
    DECLARE @staging TABLE
    (
        rn INT NOT NULL PRIMARY KEY,
        FullName NVARCHAR(100) NOT NULL,
        DeptID INT NOT NULL,
        Salary DECIMAL(18,2) NOT NULL,
        Phone NVARCHAR(50) NULL,
        Email NVARCHAR(100) NULL
    );

    INSERT INTO @staging (rn, FullName, DeptID, Salary, Phone, Email)
    SELECT
        ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS rn,
        i.FullName, i.DeptID, i.Salary, i.Phone, i.Email
    FROM inserted AS i;

    -- check DeptID to exist
    IF EXISTS (
        SELECT 1
        FROM @staging s
        LEFT JOIN dbo.Lab9_Department d ON d.DeptID = s.DeptID
        WHERE d.DeptID IS NULL
    )
    BEGIN
        RAISERROR (N'Указан несуществующий отдел.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;

    -- map rn -> new EmployeeID
    DECLARE @ids TABLE
    (
        rn INT NOT NULL PRIMARY KEY,
        EmployeeID INT NOT NULL
    );

    -- insert in Employee + get new ID
    MERGE dbo.Lab9_Employee AS tgt
    USING (SELECT rn, FullName, DeptID, Salary FROM @staging) AS src
        ON 1 = 0
    WHEN NOT MATCHED THEN
        INSERT (FullName, DeptID, Salary)
        VALUES (src.FullName, src.DeptID, src.Salary)
    OUTPUT src.rn, inserted.EmployeeID
    INTO @ids (rn, EmployeeID);

    -- insert in Details
    INSERT INTO dbo.Lab9_EmployeeDetails (EmployeeID, Phone, Email)
    SELECT x.EmployeeID, s.Phone, s.Email
    FROM @ids x
    JOIN @staging s ON s.rn = x.rn;
END;
GO


-- update trigger
CREATE TRIGGER dbo.trg_vLab9_Employee_1to1_Update
ON dbo.vLab9_Employee_1to1
INSTEAD OF UPDATE
AS
BEGIN
    -- Restrict EmployeeID changes
    IF UPDATE(EmployeeID)
    BEGIN
        RAISERROR (N'Нельзя изменять EmployeeID через представление vLab9_Employee_1to1.', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END;

    -- Update base table
    UPDATE e
    SET 
        e.FullName = ISNULL(i.FullName, e.FullName),
        e.DeptID   = ISNULL(i.DeptID,   e.DeptID),
        e.Salary   = ISNULL(i.Salary,   e.Salary)
    FROM dbo.Lab9_Employee e
    JOIN inserted i
        ON e.EmployeeID = i.EmployeeID;

    -- Update details table
    UPDATE d
    SET
        d.Phone = ISNULL(i.Phone, d.Phone),
        d.Email = ISNULL(i.Email, d.Email)
    FROM dbo.Lab9_EmployeeDetails d
    JOIN inserted i
        ON d.EmployeeID = i.EmployeeID;
    -- AFTER trigger on Lab9_Employee will check salary reduction constraint
END;
GO


-- delete trigger
CREATE TRIGGER dbo.trg_vLab9_Employee_1to1_Delete
ON dbo.vLab9_Employee_1to1
INSTEAD OF DELETE
AS
BEGIN
    -- First delete details
    DELETE d
    FROM dbo.Lab9_EmployeeDetails d
    JOIN deleted x
        ON d.EmployeeID = x.EmployeeID;

    -- Then the employee itself
    DELETE e
    FROM dbo.Lab9_Employee e
    JOIN deleted x
        ON e.EmployeeID = x.EmployeeID;
    -- AFTER trigger on Lab9_Employee will output the number of deleted rows
END;
GO


-- Examples

-- inset into view
INSERT INTO dbo.vLab9_Employee (FullName, DeptName, Salary)
VALUES (N'Новиков Никита', N'IT', 55000);

-- ! insert into table, have to fail (salary < 20000)
INSERT INTO dbo.Lab9_Employee (FullName, DeptID, Salary)
SELECT N'Тест Тестов', DeptID, 10000
FROM dbo.Lab9_Department WHERE DeptName = N'IT';

-- ! update through the table (salary reduction > 50%, also error)
UPDATE dbo.Lab9_Employee
SET Salary = 10000
WHERE EmployeeID = 1;

-- update department through the view
UPDATE dbo.vLab9_Employee
SET DeptName = N'Отдел продаж'
WHERE EmployeeID = 2;

-- deletion through the view
DELETE FROM dbo.vLab9_Employee
WHERE EmployeeID = 3;


------- 1 to 1 view examples -------

-- insert through 1:1 view (insert employee and details)
INSERT INTO dbo.vLab9_Employee_1to1 (FullName, DeptID, Salary, Phone, Email)
VALUES (N'Тест Через 1к1', 1, 70000, N'+7-900-123-45-67', N'test1to1@example.com');

-- update through 1:1 view (both tables will be updated, plus AFTER trigger on salary)
UPDATE dbo.vLab9_Employee_1to1
SET Salary = Salary * 0.6,
    Phone  = N'+7-900-765-43-21'
WHERE EmployeeID = 1;

-- ! attempt to change EmployeeID (should fail with RAISERROR)
UPDATE dbo.vLab9_Employee_1to1
SET EmployeeID = 999
WHERE EmployeeID = 2;

-- deletion through 1:1 view (will delete both details and employee)
DELETE FROM dbo.vLab9_Employee_1to1
WHERE EmployeeID = 2;
