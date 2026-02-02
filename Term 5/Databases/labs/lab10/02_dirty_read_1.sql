USE Lab10;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED; -- default

BEGIN TRAN;

-- Update
UPDATE Accounts
SET Balance = Balance - 500
WHERE Id = 1;

-- Read inside transaction
SELECT 'Session 1 inside transaction' AS Msg, *
FROM Accounts;

-- Pause 15 seconds
WAITFOR DELAY '00:00:15';

ROLLBACK TRAN;

-- Read after transaction rollback
SELECT 'Session 1 after rollback' AS Msg, *
FROM Accounts;
GO