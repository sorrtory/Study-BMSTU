USE Lab10;
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- READ COMMITTED

-- Read while another session sleeps
SELECT 'Session 2 reads' AS Msg, *
FROM Accounts;
