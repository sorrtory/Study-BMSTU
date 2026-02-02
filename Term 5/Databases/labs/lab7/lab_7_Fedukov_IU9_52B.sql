USE master;
GO

DROP DATABASE IF EXISTS LAB7;
GO
CREATE DATABASE LAB7;
GO
USE LAB7;

GO
DROP VIEW IF EXISTS AuthorBooksStats;
GO

-- 1. Create tables

CREATE TABLE Authors (
    AuthorID INT PRIMARY KEY,
    Name NVARCHAR(100),
    Country NVARCHAR(50)
);

CREATE TABLE Books (
    BookID INT PRIMARY KEY,
    Title NVARCHAR(255),
    AuthorID INT FOREIGN KEY REFERENCES Authors(AuthorID),
    Price DECIMAL(10,2) NOT NULL DEFAULT 0,
    PublishedYear INT
);
GO

-- TEST DATA
INSERT INTO Authors VALUES 
(1, 'Ivan Ivanov', 'Russia'),
(2, 'Anna Petrova', 'Kazakstan'),
(3, 'John Smith', 'USA');

INSERT INTO Books VALUES
(1, 'Programming for Beginners', 1, 1500.50, 2022),
(2, 'The Art of Design', 2, 1800.00, 2023),
(3, 'Databases', 1, 2100.75, 2021);
GO

-- 1. VIEW
CREATE VIEW CheapBooks AS
SELECT Title, Price
FROM Books
WHERE Price < 2000;
GO

-- 2. VIEW WITH JOIN
CREATE VIEW BookDetails AS
SELECT 
    b.Title,
    a.Name AS AuthorName,
    b.Price,
    b.PublishedYear
FROM Books b
INNER JOIN Authors a ON b.AuthorID = a.AuthorID;
GO


-- [S0003][1902] Line 1: Cannot create more than one clustered index on table 'Books'. Drop the existing clustered index 'PK__Books__3DE0C227081FB576' before creating another.
-- CREATE CLUSTERED INDEX IX_Books_AuthorID
-- ON Books(AuthorID)
-- GO

-- 3. INDEX WITH INCLUDED COLUMNS
CREATE INDEX IX_Books_AuthorID
ON Books(AuthorID) -- build index by AuthorID. Speeds up searches by AuthorID
INCLUDE (Title, Price); -- put Title and Price in the index. Avoid lookups in the table
GO


-- Select
SELECT Title, Price
FROM Books
WHERE AuthorID = 1; -- Without included columns, SQL Server would need to look up Title and Price in the table
GO

-- 4. INDEXED VIEW (requires SCHEMABINDING)
CREATE VIEW AuthorBooksStats
WITH SCHEMABINDING
AS
SELECT 
    a.AuthorID,
    a.Name,
    COUNT_BIG(*) AS BooksCount,
    SUM(ISNULL(b.Price, 0)) AS TotalPrice
FROM dbo.Authors a
JOIN dbo.Books b ON a.AuthorID = b.AuthorID
GROUP BY a.AuthorID, a.Name;
GO


-- Error: [S0001][1940] Line 1: Cannot create index on view 'AuthorBooksStats'. It does not have a unique clustered index.
-- Create non-clustered index (requires unique clustered index first)
-- CREATE UNIQUE NONCLUSTERED INDEX IX_AuthorStats2
-- ON AuthorBooksStats(Name);
-- GO

-- Create clustered index for view
CREATE UNIQUE CLUSTERED INDEX IX_AuthorStats
ON AuthorBooksStats(AuthorID);
GO

-- Select
SELECT * FROM AuthorBooksStats WHERE AuthorID = 1;
GO

-- Create non-clustered index (requires unique clustered index first)
CREATE UNIQUE NONCLUSTERED INDEX IX_AuthorStats2 
ON AuthorBooksStats(Name);
GO

-- Select
SELECT * FROM AuthorBooksStats WHERE Name = 'Ivan Ivanov';


-- Views
SELECT * FROM CheapBooks;
SELECT * FROM BookDetails;
SELECT * FROM AuthorBooksStats;