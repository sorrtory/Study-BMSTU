USE master;
GO
DROP DATABASE IF EXISTS LabDB;
GO

-- 1. Add new database
CREATE DATABASE LabDB
    ON PRIMARY
    (
        NAME = LabDB_primary,
        FILENAME = '/var/opt/mssql/data/LabDB_primary.mdf',
        SIZE = 10 MB,
        MAXSIZE = 100 MB,
        FILEGROWTH = 5 MB
        )
    LOG ON
    (
        NAME = LabDB_log,
        FILENAME = '/var/opt/mssql/data/LabDB_log.ldf',
        SIZE = 5 MB,
        MAXSIZE = 50 MB,
        FILEGROWTH = 5 MB
        );
GO

USE LabDB;
GO

-- 2. Add new table
CREATE TABLE Employees
(
    ID       INT IDENTITY (1,1) PRIMARY KEY,
    Name     NVARCHAR(50) NOT NULL,
    Position NVARCHAR(50),
    Salary   DECIMAL(10, 2)
);
GO

-- 3. Add new filegroup
ALTER DATABASE LabDB
    ADD FILEGROUP LabDB_FG;
GO

ALTER DATABASE LabDB
    ADD FILE
        (
            NAME = LabDB_secondary,
            FILENAME = '/var/opt/mssql/data/LabDB_secondary.ndf',
            SIZE = 10 MB,
            MAXSIZE = 100 MB,
            FILEGROWTH = 5 MB
            ) TO FILEGROUP LabDB_FG;
GO

-- 4. Set LabDB_FG to default filegroup
ALTER DATABASE LabDB
    MODIFY FILEGROUP LabDB_FG DEFAULT;
GO

-- 5. Second Table.
CREATE TABLE Projects
(
    ProjectID   INT IDENTITY (1,1) PRIMARY KEY,
    ProjectName NVARCHAR(100) NOT NULL,
    StartDate   DATE,
    Budget      DECIMAL(15, 2)
);
GO

-- 6. Move Projects to [PRIMARY] filegroup
-- https://www.sqlshack.com/how-to-move-tables-to-another-filegroup-of-a-sql-database/

-- Filegroup check
SELECT
    t.name AS TableName,
    fg.name AS FileGroupName
FROM sys.tables t
INNER JOIN sys.indexes i ON t.object_id = i.object_id
INNER JOIN sys.filegroups fg ON i.data_space_id = fg.data_space_id
WHERE i.index_id < 2; -- Clustered index or heap

-- Get Clustered ID table
SELECT name as IndexName
FROM sys.indexes
WHERE object_id = OBJECT_ID('dbo.Projects');

-- ! Have to put it here manually or use dynamic SQL to drop PK constraint
ALTER TABLE dbo.Projects
DROP CONSTRAINT [PK__Project__B2DCCBCE3D9783C3];

ALTER TABLE dbo.Projects
ADD CONSTRAINT PK_Projects PRIMARY KEY CLUSTERED (ProjectID)
ON [PRIMARY];
GO


-- Get back to primary filegroup
ALTER DATABASE LabDB
    MODIFY FILEGROUP [PRIMARY] DEFAULT;
GO

-- Remove file from filegroup
ALTER DATABASE LabDB
    REMOVE FILE LabDB_secondary;
GO

-- Remove filegroup
ALTER DATABASE LabDB
    REMOVE FILEGROUP LabDB_FG;
GO

-- 7. New schema
CREATE SCHEMA Company;
GO

-- Move Employees to Company
ALTER SCHEMA Company TRANSFER dbo.Employees;
GO

USE LabDB;
GO

-- Move Employees back to dto
ALTER SCHEMA dbo TRANSFER Company.Employees;
GO

-- Remove schema
DROP SCHEMA Company;
GO

-- Drop LabDB database
USE master;
DROP DATABASE LabDB;
GO