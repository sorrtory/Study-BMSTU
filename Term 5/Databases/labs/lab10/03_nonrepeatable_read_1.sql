USE Lab10;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- REPEATABLE READ

BEGIN TRAN;

-- First read of the balance
SELECT 'First read' AS Step, Balance
FROM Accounts
WHERE Id = 1;

-- Pause to allow another session to change data
WAITFOR DELAY '00:00:15';

-- Second read of the balance (after pause)
SELECT 'Second read' AS Step, Balance
FROM Accounts
WHERE Id = 1;

COMMIT TRAN;
