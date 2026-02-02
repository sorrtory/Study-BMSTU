USE master;
GO


-- rollback + drop
IF DB_ID('Lab10') IS NOT NULL
BEGIN
    ALTER DATABASE Lab10 SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Lab10;
END
GO


-- Create
CREATE DATABASE Lab10;
GO
USE Lab10;
GO

CREATE TABLE Accounts
(
    Id       INT PRIMARY KEY,
    Balance  INT
);

INSERT INTO Accounts(Id, Balance)
VALUES (1, 1000), (2, 2000);

CREATE TABLE Orders
(
    Id      INT IDENTITY PRIMARY KEY,
    Amount  INT
);

INSERT INTO Orders(Amount)
VALUES (50), (150), (300); -- Count > 100 = 2
GO
