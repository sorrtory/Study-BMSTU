
---------------------------------------------------------------
-- 1. CREATE DATABASE
---------------------------------------------------------------
CREATE DATABASE LAB11
ON PRIMARY
(
    NAME = N'LAB11_Data',
    FILENAME = N'/var/opt/mssql/data/LAB11_Data.mdf',
    SIZE = 20MB,
    FILEGROWTH = 10MB
)
LOG ON
(
    NAME = N'LAB11_Log',
    FILENAME = N'/var/opt/mssql/data/LAB11_Log.ldf',
    SIZE = 10MB,
    FILEGROWTH = 5MB
);
GO

USE LAB11;
GO

---------------------------------------------------------------
-- 2. CREATE TABLES
---------------------------------------------------------------

-------------------------
-- 2.1 Doctor
-------------------------
CREATE TABLE dbo.Doctor
(
    doctor_id      INT IDENTITY(1,1) NOT NULL,
    email          NVARCHAR(255)     NOT NULL,
    name           NVARCHAR(200)     NOT NULL,
    specialization NVARCHAR(200)     NOT NULL,
    phone_number   NVARCHAR(20)      NULL,
    status         NVARCHAR(20)      NOT NULL
        CONSTRAINT DF_Doctor_Status DEFAULT ('ACTIVE'),

    CONSTRAINT PK_Doctor PRIMARY KEY (doctor_id),
    CONSTRAINT UQ_Doctor_Email UNIQUE (email),
    CONSTRAINT CHK_Doctor_Status CHECK (status IN ('ACTIVE', 'INACTIVE'))
);
GO

-------------------------
-- 2.2 Patient
-------------------------
CREATE TABLE dbo.Patient
(
    insurance_number  VARCHAR(20)    NOT NULL,
    name              NVARCHAR(200)  NOT NULL,
    phone_number      VARCHAR(20)    NOT NULL,
    email             NVARCHAR(255)  NOT NULL,
    date_of_birth     DATE           NULL,
    home_address      NVARCHAR(300)  NULL,
    emergency_contact NVARCHAR(300)  NULL,
    status            NVARCHAR(20)   NOT NULL
        CONSTRAINT DF_Patient_Status DEFAULT('ACTIVE'),

    CONSTRAINT PK_Patient PRIMARY KEY (insurance_number),
    CONSTRAINT UQ_Patient_Phone UNIQUE (phone_number),
    CONSTRAINT UQ_Patient_Email UNIQUE (email),
    CONSTRAINT CHK_Patient_Status CHECK (status IN ('ACTIVE', 'INACTIVE'))
);
GO

-------------------------
-- 2.3 Appointment
-------------------------
CREATE TABLE dbo.Appointment
(
    appointment_id INT IDENTITY(1,1) NOT NULL,
    schedule_date  DATETIME2(0)      NOT NULL,
    doctor_id      INT               NOT NULL,
    patient_id     VARCHAR(20)       NULL,
    address        NVARCHAR(300)     NULL,
    room_number    NVARCHAR(20)      NULL,
    examination    NVARCHAR(400)     NULL,
    status         NVARCHAR(20)      NOT NULL
        CONSTRAINT DF_Appointment_Status DEFAULT('SCHEDULED'),

    CONSTRAINT PK_Appointment PRIMARY KEY (appointment_id),
    -- Alternate key: schedule_date + doctor_id
    CONSTRAINT UQ_Appointment_DoctorDate UNIQUE (schedule_date, doctor_id),

    CONSTRAINT CHK_Appointment_Status CHECK (status IN ('SCHEDULED', 'DONE', 'CANCELLED'))
);
GO

-------------------------
-- 2.4 Prescription
-------------------------
CREATE TABLE dbo.Prescription
(
    prescription_id     INT IDENTITY(1,1) NOT NULL,
    prescription_number NVARCHAR(50)      NOT NULL,
    doctor_id           INT               NOT NULL,
    patient_id          VARCHAR(20)       NOT NULL,
    prescribe_date      DATE              NOT NULL,
    recommendations     NVARCHAR(1000)    NOT NULL,
    drug_name           NVARCHAR(200)     NOT NULL,
    dosage              NVARCHAR(100)     NOT NULL,
    frequency           NVARCHAR(100)     NOT NULL,
    duration            NVARCHAR(100)     NOT NULL,

    CONSTRAINT PK_Prescription PRIMARY KEY (prescription_id),
    -- Alternate key: (prescription_number, doctor_id)
    CONSTRAINT UQ_Prescription_Number_Doctor UNIQUE (prescription_number, doctor_id)
);
GO

-------------------------
-- 2.5 Assay
-------------------------
CREATE TABLE dbo.Assay
(
    assay_id        INT IDENTITY(1,1) NOT NULL,
    assay_number    NVARCHAR(50)      NOT NULL,
    patient_id      VARCHAR(20)       NOT NULL,
    doctor_id       INT               NULL,
    test_date       DATE              NOT NULL,
    sample_type     NVARCHAR(100)     NOT NULL,
    results         NVARCHAR(2000)    NULL,
    status          NVARCHAR(20)      NOT NULL
        CONSTRAINT DF_Assay_Status DEFAULT('PENDING'),
    reference_range NVARCHAR(200)     NULL,
    is_urgent       BIT               NOT NULL
        CONSTRAINT DF_Assay_IsUrgent DEFAULT(0),

    CONSTRAINT PK_Assay PRIMARY KEY (assay_id),
    -- Alternate key: (assay_number, patient_id)
    CONSTRAINT UQ_Assay_Number_Patient UNIQUE (assay_number, patient_id),
    CONSTRAINT CHK_Assay_Status CHECK (status IN ('PENDING', 'DONE', 'CANCELLED'))
);
GO

---------------------------------------------------------------
-- 3. FOREIGN KEYS
---------------------------------------------------------------
ALTER TABLE dbo.Appointment
ADD CONSTRAINT FK_Appointment_Doctor
    FOREIGN KEY (doctor_id)
    REFERENCES dbo.Doctor(doctor_id)
    ON UPDATE CASCADE
    ON DELETE NO ACTION;

ALTER TABLE dbo.Appointment
ADD CONSTRAINT FK_Appointment_Patient
    FOREIGN KEY (patient_id)
    REFERENCES dbo.Patient(insurance_number)
    ON UPDATE CASCADE
    ON DELETE SET NULL;

ALTER TABLE dbo.Prescription
ADD CONSTRAINT FK_Prescription_Doctor
    FOREIGN KEY (doctor_id)
    REFERENCES dbo.Doctor(doctor_id)
    ON UPDATE CASCADE
    ON DELETE NO ACTION;

ALTER TABLE dbo.Prescription
ADD CONSTRAINT FK_Prescription_Patient
    FOREIGN KEY (patient_id)
    REFERENCES dbo.Patient(insurance_number)
    ON UPDATE CASCADE
    ON DELETE NO ACTION;

ALTER TABLE dbo.Assay
ADD CONSTRAINT FK_Assay_Patient
    FOREIGN KEY (patient_id)
    REFERENCES dbo.Patient(insurance_number)
    ON UPDATE CASCADE
    ON DELETE NO ACTION;

ALTER TABLE dbo.Assay
ADD CONSTRAINT FK_Assay_Doctor
    FOREIGN KEY (doctor_id)
    REFERENCES dbo.Doctor(doctor_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;
GO

---------------------------------------------------------------
-- 4. DDL: ADD / ALTER COLUMNS
---------------------------------------------------------------
-- Add new optional column to Patient
ALTER TABLE dbo.Patient
ADD middle_name NVARCHAR(100) NULL;
GO

-- Change data type/size of phone_number
ALTER TABLE dbo.Patient
ALTER COLUMN phone_number VARCHAR(30) NOT NULL;
GO

-- ALTER TABLE / DROP object example
-- DROP INDEX IX_Appointment_DoctorDate ON dbo.Appointment;
-- DROP VIEW dbo.vw_DoctorAppointments;
-- GO

---------------------------------------------------------------
-- 5. VIEWS and INDEXES
---------------------------------------------------------------

-------------------------
-- 5.1 Simple view
-------------------------
CREATE VIEW dbo.vw_DoctorAppointments
AS
SELECT
    d.doctor_id,
    d.name          AS doctor_name,
    d.specialization,
    a.appointment_id,
    a.schedule_date,
    a.status        AS appointment_status,
    p.insurance_number AS patient_insurance,
    p.name          AS patient_name
FROM dbo.Doctor      AS d
INNER JOIN dbo.Appointment AS a ON a.doctor_id = d.doctor_id
LEFT  JOIN dbo.Patient    AS p ON p.insurance_number = a.patient_id;
GO

-------------------------
-- 5.2 Aggregated view
-------------------------
CREATE VIEW dbo.vw_DoctorStats
AS
SELECT
    d.doctor_id,
    d.name AS doctor_name,
    COUNT(a.appointment_id) AS total_appointments
FROM dbo.Doctor d
LEFT JOIN dbo.Appointment a ON a.doctor_id = d.doctor_id
GROUP BY d.doctor_id, d.name;
GO

-------------------------
-- 5.3 INDEXES
-------------------------
-- Nonclustered index for typical appointment search by doctor and date
CREATE NONCLUSTERED INDEX IX_Appointment_DoctorDate
ON dbo.Appointment(doctor_id, schedule_date);

-- Index for urgent assays only
CREATE NONCLUSTERED INDEX IX_Assay_Urgent
ON dbo.Assay (test_date)
WHERE is_urgent = 1;
GO

---------------------------------------------------------------
-- 6. STORED PROCEDURES
---------------------------------------------------------------

-------------------------
-- 6.1 Insert appointment
-------------------------
CREATE PROCEDURE dbo.usp_AddAppointment
    @schedule_date DATETIME2(0),
    @doctor_id     INT,
    @patient_id    VARCHAR(20) = NULL,
    @address       NVARCHAR(300) = NULL,
    @room_number   NVARCHAR(20) = NULL,
    @examination   NVARCHAR(400) = NULL,
    @status        NVARCHAR(20) = 'SCHEDULED'
AS
BEGIN
    INSERT INTO dbo.Appointment
        (schedule_date, doctor_id, patient_id, address, room_number, examination, status)
    VALUES
        (@schedule_date, @doctor_id, @patient_id, @address, @room_number, @examination, @status);

    SELECT SCOPE_IDENTITY() AS new_appointment_id;
END;
GO

-------------------------
-- 6.2 Get patient history
-------------------------
CREATE PROCEDURE dbo.usp_GetPatientHistory
    @insurance_number VARCHAR(20)
AS
BEGIN
    -- Appointments
    SELECT
        'APPOINTMENT' AS record_type,
        a.appointment_id,
        a.schedule_date,
        d.name AS doctor_name,
        a.status,
        a.examination
    FROM dbo.Appointment a
    INNER JOIN dbo.Doctor d ON d.doctor_id = a.doctor_id
    WHERE a.patient_id = @insurance_number

    UNION ALL

    -- Prescriptions
    SELECT
        'PRESCRIPTION' AS record_type,
        p.prescription_id,
        CAST(p.prescribe_date AS DATETIME2(0)),
        d2.name AS doctor_name,
        NULL AS status,
        p.drug_name + N' (' + p.dosage + N')' AS examination
    FROM dbo.Prescription p
    INNER JOIN dbo.Doctor d2 ON d2.doctor_id = p.doctor_id
    WHERE p.patient_id = @insurance_number

    ORDER BY record_type, schedule_date;
END;
GO

---------------------------------------------------------------
-- 7. FUNCTIONS
---------------------------------------------------------------

-------------------------
-- 7.1 Scalar function: patient age
-------------------------
CREATE FUNCTION dbo.ufn_GetPatientAge
(
    @insurance_number VARCHAR(20)
)
RETURNS INT
AS
BEGIN
    DECLARE @dob DATE;
    DECLARE @age INT;

    SELECT @dob = date_of_birth
    FROM dbo.Patient
    WHERE insurance_number = @insurance_number;

    IF @dob IS NULL
        RETURN NULL;

    SET @age = DATEDIFF(YEAR, @dob, GETDATE());
    IF DATEADD(YEAR, @age, @dob) > CAST(GETDATE() AS DATE)
        SET @age = @age - 1;

    RETURN @age;
END;
GO

-------------------------
-- 7.2 Inline TVF: scheduled appointments for doctor
-------------------------
CREATE FUNCTION dbo.ufn_GetScheduledAppointmentsForDoctor
(
    @doctor_id INT
)
RETURNS TABLE
AS
RETURN
(
    SELECT
        a.appointment_id,
        a.schedule_date,
        a.status,
        p.name AS patient_name
    FROM dbo.Appointment a
    LEFT JOIN dbo.Patient p ON p.insurance_number = a.patient_id
    WHERE a.doctor_id = @doctor_id
      AND a.status = 'SCHEDULED'
);
GO

---------------------------------------------------------------
-- 8. TRIGGER
---------------------------------------------------------------

-------------------------
-- 8.1 Prevent appointments in the past
-------------------------
CREATE TRIGGER dbo.trg_Appointment_PreventPast
ON dbo.Appointment
AFTER INSERT, UPDATE
AS
BEGIN
    -- If any inserted/updated row is scheduled in the past, rollback
    IF EXISTS (
        SELECT 1
        FROM inserted i
        WHERE i.schedule_date < SYSDATETIME() AND i.status = 'SCHEDULED'
    )
    BEGIN
        RAISERROR('Cannot create or update appointment in the past.', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;
GO

---------------------------------------------------------------
-- 9. SAMPLE DATA (DML INSERT)
---------------------------------------------------------------

-------------------------
-- 9.1 Insert Doctors
-------------------------
INSERT INTO dbo.Doctor (email, name, specialization, phone_number, status)
VALUES
('house@example.com',     N'Gregory House',   N'Diagnostics',  '100-000-001', 'ACTIVE'),
('who13@example.com',     N'Unknown Doctor', N'Therapist',    '100-000-002', 'ACTIVE'),
('surgeon@example.com',   N'Miranda Bailey', N'Surgeon',      '100-000-003', 'INACTIVE');

-------------------------
-- 9.2 Insert Patients
-------------------------
INSERT INTO dbo.Patient (insurance_number, name, phone_number, email, date_of_birth, home_address, emergency_contact, status)
VALUES
('INS-001', N'John Smith',   '200-000-001', 'john.smith@example.com', '1985-01-15', N'City A', N'Wife', 'ACTIVE'),
('INS-002', N'Alice Brown',  '200-000-002', 'alice.b@example.com',    '1990-05-20', N'City B', N'Husband', 'ACTIVE'),
('INS-003', N'Bob Miller',   '200-000-003', 'bob.m@example.com',      '1975-09-10', N'City C', N'Son', 'INACTIVE');

-------------------------
-- 9.3 Insert Appointments (INSERT VALUES)
-------------------------
INSERT INTO dbo.Appointment (schedule_date, doctor_id, patient_id, address, room_number, examination, status)
VALUES
(DATEADD(DAY, 1,  CAST(GETDATE() AS DATE)), 1, 'INS-001', N'Hospital A', '101', N'Check-up', 'SCHEDULED'),
(DATEADD(DAY, 2,  CAST(GETDATE() AS DATE)), 2, 'INS-002', N'Hospital A', '102', N'Consultation', 'SCHEDULED'),
(DATEADD(DAY, -1, CAST(GETDATE() AS DATE)), 1, 'INS-003', N'Hospital A', '101', N'Old visit', 'DONE');

-------------------------
-- 9.4 Insert Prescriptions
-------------------------
INSERT INTO dbo.Prescription
    (prescription_number, doctor_id, patient_id, prescribe_date, recommendations, drug_name, dosage, frequency, duration)
VALUES
('RX-001', 1, 'INS-001', CAST(GETDATE() AS DATE), N'Take after food', N'Ibuprofen', N'200mg', N'3 times a day', N'5 days'),
('RX-002', 2, 'INS-002', DATEADD(DAY, -10, CAST(GETDATE() AS DATE)), N'Before sleep', N'Melatonin', N'3mg', N'Once a day', N'10 days');

-------------------------
-- 9.5 Insert Assays (INSERT...SELECT example)
-------------------------
-- Insert one urgent assay per active patient for doctor 1
INSERT INTO dbo.Assay
    (assay_number, patient_id, doctor_id, test_date, sample_type, results, status, reference_range, is_urgent)
SELECT
    'AS-' + insurance_number,
    insurance_number,
    1,
    CAST(GETDATE() AS DATE),
    N'Blood',
    NULL,
    'PENDING',
    N'Normal',
    1
FROM dbo.Patient
WHERE status = 'ACTIVE';
GO

---------------------------------------------------------------
-- 10. DML: UPDATE and DELETE examples
---------------------------------------------------------------

-------------------------
-- 10.1 UPDATE example
-------------------------
-- Mark past appointments as DONE if still SCHEDULED
UPDATE dbo.Appointment
SET status = 'DONE'
WHERE status = 'SCHEDULED'
  AND schedule_date < SYSDATETIME();

-------------------------
-- 10.2 DELETE example
-------------------------
-- Delete cancelled appointments older than 30 days
DELETE FROM dbo.Appointment
WHERE status = 'CANCELLED'
  AND schedule_date < DATEADD(DAY, -30, SYSDATETIME());
GO

---------------------------------------------------------------
-- 11. SELECT QUERIES
---------------------------------------------------------------

-------------------------
-- 11.1 DISTINCT (remove duplicates)
-------------------------
-- Unique list of doctor specializations
SELECT DISTINCT d.specialization
FROM dbo.Doctor AS d;
-- (DISTINCT used for removing duplicates)

-------------------------
-- 11.2 Aliases for tables and columns
-------------------------
SELECT
    d.doctor_id      AS DoctorId,
    d.name           AS DoctorName,
    COUNT(a.appointment_id) AS AppointmentCount
FROM dbo.Doctor AS d
LEFT JOIN dbo.Appointment AS a
    ON a.doctor_id = d.doctor_id
GROUP BY d.doctor_id, d.name
ORDER BY AppointmentCount DESC;

-------------------------
-- 11.3 JOIN types
-------------------------

-- INNER JOIN: only appointments that have both doctor and patient
SELECT
    a.appointment_id,
    a.schedule_date,
    d.name AS DoctorName,
    p.name AS PatientName
FROM dbo.Appointment AS a
INNER JOIN dbo.Doctor   AS d ON d.doctor_id = a.doctor_id
INNER JOIN dbo.Patient  AS p ON p.insurance_number = a.patient_id;

-- LEFT JOIN: all doctors, even without appointments
SELECT
    d.doctor_id,
    d.name AS DoctorName,
    a.appointment_id,
    a.schedule_date
FROM dbo.Doctor AS d
LEFT JOIN dbo.Appointment AS a
    ON a.doctor_id = d.doctor_id
ORDER BY d.doctor_id, a.schedule_date;

-- RIGHT JOIN: all appointments, even if doctor is missing (theoretically)
SELECT
    d.doctor_id,
    d.name AS DoctorName,
    a.appointment_id,
    a.schedule_date
FROM dbo.Doctor AS d
RIGHT JOIN dbo.Appointment AS a
    ON a.doctor_id = d.doctor_id;

-- FULL OUTER JOIN: union of doctors and appointments with possible gaps
SELECT
    d.doctor_id,
    d.name AS DoctorName,
    a.appointment_id,
    a.schedule_date
FROM dbo.Doctor AS d
FULL OUTER JOIN dbo.Appointment AS a
    ON a.doctor_id = d.doctor_id;

-------------------------
-- 11.4 Conditions: NULL / LIKE / BETWEEN / IN / EXISTS
-------------------------

-- NULL: appointments without specified patient
SELECT *
FROM dbo.Appointment AS a
WHERE a.patient_id IS NULL;

-- LIKE: patients whose name starts with 'A'
SELECT *
FROM dbo.Patient AS p
WHERE p.name LIKE N'A%';

-- BETWEEN: appointments in date interval
DECLARE @fromDate DATE = DATEADD(DAY, -1, CAST(GETDATE() AS DATE));
DECLARE @toDate   DATE = DATEADD(DAY, 7,  CAST(GETDATE() AS DATE));

SELECT a.*
FROM dbo.Appointment AS a
WHERE a.schedule_date BETWEEN @fromDate AND @toDate;

-- IN: doctors with specific specializations
SELECT d.*
FROM dbo.Doctor AS d
WHERE d.specialization IN (N'Therapist', N'Diagnostics');

-- EXISTS (correlated subquery): patients having at least one prescription
SELECT p.*
FROM dbo.Patient AS p
WHERE EXISTS (
    SELECT 1
    FROM dbo.Prescription AS pr
    WHERE pr.patient_id = p.insurance_number
);

-------------------------
-- 11.5 ORDER BY ASC and DESC
-------------------------

-- ASC: nearest appointments first
SELECT a.appointment_id, a.schedule_date, a.status
FROM dbo.Appointment AS a
ORDER BY a.schedule_date ASC;

-- DESC: latest prescriptions first
SELECT pr.prescription_id, pr.prescribe_date, pr.drug_name
FROM dbo.Prescription AS pr
ORDER BY pr.prescribe_date DESC;

-------------------------
-- 11.6 GROUP BY + HAVING + aggregates (COUNT / AVG / SUM / MIN / MAX)
-------------------------
-- Per-patient prescription statistics
SELECT
    pr.patient_id,
    COUNT(*)                                    AS TotalPrescriptions,      -- COUNT
    MIN(pr.prescribe_date)                     AS FirstPrescriptionDate,    -- MIN
    MAX(pr.prescribe_date)                     AS LastPrescriptionDate,     -- MAX
    AVG(DATEDIFF(DAY, pr.prescribe_date, GETDATE())) AS AvgDaysSince,      -- AVG
    SUM(CASE WHEN pr.drug_name IS NOT NULL THEN 1 ELSE 0 END) AS SumOfDrugs -- SUM on expression
FROM dbo.Prescription AS pr
GROUP BY pr.patient_id
HAVING COUNT(*) >= 1;

-------------------------
-- 11.7 UNION / UNION ALL / EXCEPT / INTERSECT
-------------------------

-- UNION: names of all distinct persons (doctors + patients)
SELECT name
FROM dbo.Doctor
UNION               -- removes duplicates
SELECT name
FROM dbo.Patient;

-- UNION ALL: same but keeps duplicates
SELECT name
FROM dbo.Doctor
UNION ALL           -- keeps duplicates
SELECT name
FROM dbo.Patient;

-- EXCEPT: doctor names that are not patient names
SELECT name
FROM dbo.Doctor
EXCEPT
SELECT name
FROM dbo.Patient;

-- INTERSECT: people who are both doctor and patient (by name)
SELECT name
FROM dbo.Patient
INTERSECT
SELECT name
FROM dbo.Doctor;

-------------------------
-- 11.8 Nested (sub)queries
-------------------------

-- Subquery in FROM (derived table)
SELECT
    x.doctor_id,
    x.total_appointments
FROM
(
    SELECT
        a.doctor_id,
        COUNT(*) AS total_appointments
    FROM dbo.Appointment AS a
    GROUP BY a.doctor_id
) AS x
WHERE x.total_appointments > 0;

-- Subquery in SELECT + scalar function usage
SELECT
    p.insurance_number,
    p.name,
    dbo.ufn_GetPatientAge(p.insurance_number) AS Age,
    (
        SELECT COUNT(*)
        FROM dbo.Appointment AS a
        WHERE a.patient_id = p.insurance_number
    ) AS AppointmentCount
FROM dbo.Patient AS p;
GO
