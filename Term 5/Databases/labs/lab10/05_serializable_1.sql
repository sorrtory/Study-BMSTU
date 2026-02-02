USE Lab10;
GO

SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
GO

BEGIN TRAN;

-- Update Id = 1
UPDATE Accounts
SET Balance = Balance + 10
WHERE Id = 1;

-- Pause
WAITFOR DELAY '00:00:10';

-- Update Id = 2
UPDATE Accounts
SET Balance = Balance + 10
WHERE Id = 2;

COMMIT TRAN;
GO
