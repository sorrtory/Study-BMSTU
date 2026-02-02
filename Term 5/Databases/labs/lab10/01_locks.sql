USE Lab10;

SELECT
    request_session_id,
    resource_type,
    resource_description,
    request_mode,
    request_status
FROM sys.dm_tran_locks
-- WHERE request_session_id IN (/* @@SPID 1 and 2 */);

-- To check current session
SELECT @@SPID AS MySessionId;
