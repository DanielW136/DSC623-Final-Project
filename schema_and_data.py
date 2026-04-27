#!/usr/bin/env python3

import sqlite3
import os

# Remove previous db
if os.path.exists('vehicle_hire.db'):
    os.remove('vehicle_hire.db')

db_connect = sqlite3.connect('vehicle_hire.db')
cursor = db_connect.cursor()

# Enable foreign key enforcement
cursor.execute("PRAGMA foreign_keys = ON;")


# Schema

# Site
cursor.execute("""
    CREATE TABLE Site (
        siteNumber   INTEGER,
        phoneNumber  VARCHAR(20),
        faxNumber    VARCHAR(20),
        address      VARCHAR(200),
        PRIMARY KEY (siteNumber)
    );
""")

# Models
cursor.execute("""
    CREATE TABLE Models (
        model  VARCHAR(50),
        make   VARCHAR(50) NOT NULL,
        PRIMARY KEY (model)
    );
""")

# Client
cursor.execute("""
    CREATE TABLE Client (
        clientNumber   INTEGER,
        name           VARCHAR(100) NOT NULL,
        address        VARCHAR(200),
        phoneNumber    VARCHAR(20)  NOT NULL,
        DOB            DATE         NOT NULL,
        licenseNumber  VARCHAR(50)  NOT NULL UNIQUE,
        PRIMARY KEY (clientNumber)
    );
""")

#Staff
cursor.execute("""
    CREATE TABLE Staff (
        staffNumber  INTEGER,
        name         VARCHAR(100) NOT NULL,
        homeAddress  VARCHAR(200),
        phoneNumber  VARCHAR(20),
        DOB          DATE,
        sex          CHAR(1),
        startDate    DATE         NOT NULL,
        jobTitle     VARCHAR(50),
        salary       DECIMAL      NOT NULL,
        siteNumber   INTEGER,
        PRIMARY KEY (staffNumber),
        FOREIGN KEY (siteNumber) REFERENCES Site(siteNumber),
        CHECK (sex IN ('M', 'F')),
        CHECK (salary > 0)
    );
""")

#Vehicle
cursor.execute("""
    CREATE TABLE Vehicle (
        registrationNumber  VARCHAR(20),
        model               VARCHAR(50),
        engineSize          DECIMAL,
        capacity            INTEGER,
        currentMileage      INTEGER,
        dailyHireRate       DECIMAL NOT NULL,
        curLocation         VARCHAR(200),
        siteNumber          INTEGER,
        PRIMARY KEY (registrationNumber),
        FOREIGN KEY (model)      REFERENCES Models(model),
        FOREIGN KEY (siteNumber) REFERENCES Site(siteNumber),
        CHECK (dailyHireRate > 0),
        CHECK (currentMileage >= 0)
    );
""")

#Hire Agreement
cursor.execute("""
    CREATE TABLE HireAgreement (
        hireNumber                 INTEGER,
        clientNumber               INTEGER  NOT NULL,
        hireStartDate              DATE     NOT NULL,
        hireTerminationDate        DATE,
        vehicleRegistrationNumber  VARCHAR(20) NOT NULL,
        startMileage               INTEGER  NOT NULL,
        endMileage                 INTEGER,
        PRIMARY KEY (hireNumber),
        FOREIGN KEY (clientNumber)
            REFERENCES Client(clientNumber),
        FOREIGN KEY (vehicleRegistrationNumber)
            REFERENCES Vehicle(registrationNumber),
        CHECK (startMileage >= 0),
        CHECK (endMileage IS NULL OR endMileage >= startMileage),
        CHECK (hireTerminationDate IS NULL
               OR hireTerminationDate >= hireStartDate)
    );
""")





# Sample Data for transactions

cursor.executemany(
    "INSERT INTO Site VALUES (?, ?, ?, ?);",
    [
        (1, '305-555-0101', '305-555-0102', '100 Ocean Dr, Miami, FL'),
        (2, '305-555-0201', '305-555-0202', '500 Biscayne Blvd, Miami, FL'),
        (3, '407-555-0301', '407-555-0302', '200 Orange Ave, Orlando, FL'),
        (4, '813-555-0401', '813-555-0402', '300 Bayshore Blvd, Tampa, FL'),
        (5, '904-555-0501', '904-555-0502', '400 Riverside Dr, Jacksonville, FL'),
    ],
)

cursor.executemany(
    "INSERT INTO Models VALUES (?, ?);",
    [
        ('Civic',    'Honda'),
        ('Corolla',  'Toyota'),
        ('F-150',    'Ford'),
        ('Model 3',  'Tesla'),
        ('Wrangler', 'Jeep'),
    ],
)

cursor.executemany(
    "INSERT INTO Client VALUES (?, ?, ?, ?, ?, ?);",
    [
        (101, 'Alice Nguyen', '12 Palm St, Miami, FL', '305-111-1001', '1990-04-12', 'FL-DL-1001'),
        (102, 'Bob Martinez', '34 Coral Way, Miami, FL', '305-111-1002', '1985-08-23', 'FL-DL-1002'),
        (103, 'Carla Singh', '78 Sunset Ave, Orlando, FL',  '407-111-1003', '1992-11-05', 'FL-DL-1003'),
        (104, 'Diego Alvarez', '5 Bay St, Tampa, FL', '813-111-1004', '1978-02-19', 'FL-DL-1004'),
        (105, 'Evelyn Park', '90 River Rd, Jacksonville, FL', '904-111-1005', '1995-07-30', 'FL-DL-1005'),
    ],
)

cursor.executemany(
    "INSERT INTO Staff VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
    [
        (1, 'Sebastian Cruz', '1 Beach Rd, Miami, FL', '305-222-2001', '1988-03-15', 'M', '2018-06-01', 'Manager', 75000, 1),
        (2, 'Maria Lopez', '2 Palm Ln, Miami, FL', '305-222-2002', '1991-09-21', 'F', '2020-01-10', 'Sales Agent', 48000, 1),
        (3, 'James Chen', '3 Coral Ct, Miami, FL', '305-222-2003', '1986-12-04', 'M', '2017-03-22', 'Mechanic', 52000, 2),
        (4, 'Priya Patel', '4 Lake Dr, Orlando, FL', '407-222-2004', '1993-05-17', 'F', '2021-08-15', 'Sales Agent', 47000, 3),
        (5, 'Tom Reilly', '5 Bay Ave, Tampa, FL', '813-222-2005', '1980-10-30', 'M', '2015-11-02', 'Manager', 78000, 4),
    ],
)

cursor.executemany(
    "INSERT INTO Vehicle VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
    [
        ('FL-AAA-001', 'Civic', 1.8, 5, 22000, 45.00, 'Miami Lot A', 1),
        ('FL-AAA-002', 'Corolla', 1.8, 5, 18500, 42.00, 'Miami Lot A', 1),
        ('FL-BBB-003', 'F-150', 5.0, 3, 35000, 80.00, 'Miami Lot B', 2),
        ('FL-CCC-004', 'Model 3', 0.0, 5, 9000, 95.00,'Orlando Garage', 3),
        ('FL-DDD-005', 'Wrangler', 3.6, 4, 41000, 75.00, 'Tampa Yard', 4),
    ],
)

cursor.executemany(
    "INSERT INTO HireAgreement VALUES (?, ?, ?, ?, ?, ?, ?);",
    [
        # Active hires (today is 2026-04-27, no termination date yet)
        (1001, 101, '2026-04-20', None, 'FL-AAA-001', 22000, None),
        (1002, 103, '2026-04-15', None, 'FL-CCC-004', 9000, None),
        # Closed past hires
        (1003, 102, '2026-03-01', '2026-03-10', 'FL-BBB-003', 34000, 35000),
        (1004, 104, '2026-02-14', '2026-02-20', 'FL-DDD-005', 40500, 41000),
        (1005, 105, '2026-01-05', '2026-01-12', 'FL-AAA-002', 18000, 18500),
    ],
)

db_connect.commit()


