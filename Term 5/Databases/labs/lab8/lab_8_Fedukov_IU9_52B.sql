USE master;
GO

DROP DATABASE IF EXISTS LAB8;
GO
CREATE DATABASE LAB8;
GO
USE LAB8;

DROP PROCEDURE IF EXISTS dbo.usp_GetEmployeesCursor;
DROP PROCEDURE IF EXISTS dbo.usp_PrintHighSalaryEmployees;

DROP FUNCTION IF EXISTS dbo.udf_CalcAge;
DROP FUNCTION IF EXISTS dbo.udf_IsHighSalary;
DROP FUNCTION IF EXISTS dbo.udf_GetEmployeesWithAge;

DROP TABLE IF EXISTS dbo.LabEmployees;
GO

CREATE TABLE dbo.LabEmployees
(
    EmployeeID INT IDENTITY(1,1) CONSTRAINT PK_LabEmployees PRIMARY KEY,
    FirstName  NVARCHAR(50) NOT NULL,
    LastName   NVARCHAR(50) NOT NULL,
    BirthDate  DATE         NOT NULL,
    Salary     DECIMAL(18,2) NOT NULL
);
GO

INSERT INTO dbo.LabEmployees (FirstName, LastName, BirthDate, Salary)
VALUES 
    (N'Иван',   N'Иванов',   '1985-01-10', 60000),
    (N'Петр',   N'Петров',   '1990-05-20', 45000),
    (N'Сергей', N'Сергеев',  '1978-03-15', 80000),
    (N'Ольга',  N'Сидорова', '1995-11-30', 35000),
    (N'Анна',   N'Кузнецова','1988-07-07', 52000);
GO

-- 1. Stored procedure
CREATE PROCEDURE dbo.usp_GetEmployeesCursor
    @EmployeesCursor CURSOR VARYING OUTPUT
AS
BEGIN
    SET @EmployeesCursor = CURSOR LOCAL STATIC FOR
        SELECT 
            EmployeeID,
            FirstName,
            LastName,
            BirthDate,
            Salary
        FROM dbo.LabEmployees;

    OPEN @EmployeesCursor;
END;
GO

-- 2. Modify dbo.usp_GetEmployeesCursor to include age calculation

-- Required user-defined function
CREATE FUNCTION dbo.udf_CalcAge
(
    @BirthDate DATE
)
RETURNS INT
AS
BEGIN
    DECLARE @Age INT;
    SET @Age = DATEDIFF(YEAR, @BirthDate, GETDATE());

    -- if birthday haven't happened yet in this year, then subsctact 1 
    IF (DATEADD(YEAR, @Age, @BirthDate) > CAST(GETDATE() AS DATE))
        SET @Age = @Age - 1;

    RETURN @Age;
END;
GO

-- Altering dbo.usp_GetEmployeesCursor to use dbo.udf_CalcAge
ALTER PROCEDURE dbo.usp_GetEmployeesCursor
    @EmployeesCursor CURSOR VARYING OUTPUT
AS
BEGIN
    SET @EmployeesCursor = CURSOR LOCAL STATIC FOR
        SELECT 
            e.EmployeeID,
            e.FirstName,
            e.LastName,
            e.BirthDate,
            e.Salary,
            dbo.udf_CalcAge(e.BirthDate) AS Age
        FROM dbo.LabEmployees AS e;

    OPEN @EmployeesCursor;
END;
GO

-- 3. Create usp that calls dbo.usp_GetEmployeesCursor and unwinds resulting cursor

-- Required user-defined function for dbo.usp_PrintHighSalaryEmployees
CREATE FUNCTION dbo.udf_IsHighSalary
(
    @Salary DECIMAL(18,2)
)
RETURNS BIT
AS
BEGIN
    DECLARE @Result BIT;

    -- threshold
    IF @Salary >= 50000
        SET @Result = 1;
    ELSE
        SET @Result = 0;

    RETURN @Result;
END;
GO

-- Call usp_GetEmployeesCursor
CREATE PROCEDURE dbo.usp_PrintHighSalaryEmployees
AS
BEGIN
    DECLARE @cur CURSOR;

    -- Get cursor
    EXEC dbo.usp_GetEmployeesCursor @EmployeesCursor = @cur OUTPUT;

    DECLARE 
        @EmployeeID INT,
        @FirstName  NVARCHAR(50),
        @LastName   NVARCHAR(50),
        @BirthDate  DATE,
        @Salary     DECIMAL(18,2),
        @Age        INT;


    -- Get first
    FETCH NEXT FROM @cur 
        INTO @EmployeeID, @FirstName, @LastName, @BirthDate, @Salary, @Age;

    -- Iterate
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- Use dbo.udf_IsHighSalary
        IF dbo.udf_IsHighSalary(@Salary) = 1
        BEGIN
            PRINT N'Employee ' + @FirstName + N' ' + @LastName
                  + N', age ' + CAST(@Age AS NVARCHAR(10))
                  + N', salary ' + CAST(@Salary AS NVARCHAR(20));
        END;

        FETCH NEXT FROM @cur 
            INTO @EmployeeID, @FirstName, @LastName, @BirthDate, @Salary, @Age;
    END;

    CLOSE @cur;
    DEALLOCATE @cur;
END;
GO

-- 4. Modify dbo.usp_PrintHighSalaryEmployees to use table-valued function


-- table func (inline)
CREATE FUNCTION dbo.udf_GetEmployeesWithHighSalary()
RETURNS TABLE
AS
RETURN
(
    SELECT
        e.EmployeeID,
        e.FirstName,
        e.LastName,
        e.BirthDate,
        e.Salary,
        dbo.udf_CalcAge(e.BirthDate) AS Age
    FROM dbo.LabEmployees AS e
    WHERE dbo.udf_IsHighSalary(e.Salary) = 1
);
GO

-- table-valued function (multi-statement)
CREATE FUNCTION dbo.udf_GetEmployeesWithHighSalaryV2()
RETURNS @Result TABLE
(
    EmployeeID INT,
    FirstName NVARCHAR(50),
    LastName NVARCHAR(50),
    BirthDate DATE,
    Salary DECIMAL(18,2),
    Age INT
)
AS
BEGIN
    INSERT INTO @Result (EmployeeID, FirstName, LastName, BirthDate, Salary, Age)
    SELECT
        e.EmployeeID,
        e.FirstName,
        e.LastName,
        e.BirthDate,
        e.Salary,
        dbo.udf_CalcAge(e.BirthDate) AS Age
    FROM dbo.LabEmployees AS e
    WHERE dbo.udf_IsHighSalary(e.Salary) = 1;
    RETURN;
END;
GO

-- Modify dbo.usp_PrintHighSalaryEmployees to use table function (dbo.udf_GetEmployeesWithHighSalary)
ALTER PROCEDURE dbo.usp_PrintHighSalaryEmployees
AS
BEGIN
    DECLARE @cur CURSOR;

    -- Get cursor that selects from table function
    SET @cur = CURSOR LOCAL STATIC FOR
        SELECT 
            EmployeeID,
            FirstName,
            LastName,
            BirthDate,
            Salary,
            Age
        FROM dbo.udf_GetEmployeesWithHighSalary();  -- table func
    OPEN @cur;

    DECLARE 
        @EmployeeID INT,
        @FirstName  NVARCHAR(50),
        @LastName   NVARCHAR(50),
        @BirthDate  DATE,
        @Salary     DECIMAL(18,2),
        @Age        INT;


    -- Get first
    FETCH NEXT FROM @cur 
        INTO @EmployeeID, @FirstName, @LastName, @BirthDate, @Salary, @Age;

    -- Iterate
    WHILE @@FETCH_STATUS = 0
    BEGIN
        -- We do not need to check salary here, as table func already filters
        PRINT N'Employee ' + @FirstName + N' ' + @LastName
                + N', age ' + CAST(@Age AS NVARCHAR(10))
                + N', salary ' + CAST(@Salary AS NVARCHAR(20));

        FETCH NEXT FROM @cur 
            INTO @EmployeeID, @FirstName, @LastName, @BirthDate, @Salary, @Age;
    END;

    CLOSE @cur;
    DEALLOCATE @cur;
END;
GO

------------------------------------------------------------
-- Use cursor to print all employees

DECLARE @c CURSOR;
EXEC dbo.usp_GetEmployeesCursor @EmployeesCursor = @c OUTPUT;
DECLARE 
    @id INT,
    @fn NVARCHAR(50),
    @ln NVARCHAR(50),
    @bd DATE,
    @sal DECIMAL(18,2),
    @age INT;

FETCH NEXT FROM @c INTO @id, @fn, @ln, @bd, @sal, @age;

WHILE @@FETCH_STATUS = 0
BEGIN
    PRINT N'Employee: ' + @fn + N' ' + @ln
          + N', age ' + CAST(@age AS NVARCHAR(10))
          + N', salary ' + CAST(@sal AS NVARCHAR(20));

    FETCH NEXT FROM @c INTO @id, @fn, @ln, @bd, @sal, @age;
END;

CLOSE @c;
DEALLOCATE @c;

PRINT '---------------------------'

EXEC dbo.usp_PrintHighSalaryEmployees;