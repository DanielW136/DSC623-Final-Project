#!/usr/bin/env python3

import sqlite3
import pandas as pd

db_connect = sqlite3.connect('vehicle_hire.db')
cursor = db_connect.cursor()


# Prints the resulting query with a title
def show(sql, label):
    print(label)
    df = pd.read_sql_query(sql, db_connect)
    if df.empty:
        print("(no rows)")
    else:
        print(df.to_string(index=False))
    print("\n")

# Verify sample data
show("SELECT * FROM Site;", "Site (initial)")
show("SELECT * FROM Models;", "Models (initial)")
show("SELECT * FROM Client;", "Client (initial)")
show("SELECT * FROM Staff;", "Staff (initial)")
show("SELECT * FROM Vehicle;", "Vehicle (initial)")
show("SELECT * FROM HireAgreement;", "HireAgreement (initial)")


# Transaction 1
# Which staff members work at the site where a specific vehicle is located?
# Vehicle -> Site -> Staff.
q1 = """
    SELECT st.staffNumber, st.name, st.jobTitle, st.siteNumber
    FROM Vehicle v
    JOIN Staff st ON v.siteNumber = st.siteNumber
    WHERE v.registrationNumber = 'FL-AAA-001';
    """
show(q1, "T1: Staff at the site of vehicle FL-AAA-001")


# Transaction 2
# What is the address of the client who hired a specific vehicle on a given date?
# Client's address from hire agreement, given vehicleRegistrationNumber + hireStartDate.
q2 = """
    SELECT c.clientNumber, c.name, c.address
    FROM HireAgreement h
    JOIN Client c ON h.clientNumber = c.clientNumber
    WHERE h.vehicleRegistrationNumber = 'FL-AAA-001'
      AND h.hireStartDate = '2026-04-20';
"""
show(q2, "T2: Address of client who hired FL-AAA-001 on 2026-04-20")


# Transaction 3
# Vehicles currently allocated to the site where Sebastian works
# Staff -> Site -> Vehicle, then COUNT.
q3 = """
    SELECT st.name        AS staffName,
           st.siteNumber  AS siteNumber,
           COUNT(v.registrationNumber) AS vehicleCount
    FROM Staff st
    LEFT JOIN Vehicle v ON v.siteNumber = st.siteNumber
    WHERE st.name = 'Sebastian Cruz'
    GROUP BY st.staffNumber, st.name, st.siteNumber;
"""
show(q3, "T3: Vehicle count at Sebastian's site")


# Transaction 4
# What are the vehicle details (make and model) for all active hire agreements signed by a specific client?
# "Active" = hireTerminationDate IS NULL.
# HireAgreement -> Vehicle -> Models.
q4 = """
    SELECT h.hireNumber, h.vehicleRegistrationNumber, m.make, v.model, h.hireStartDate
    FROM HireAgreement h
    JOIN Vehicle v ON h.vehicleRegistrationNumber = v.registrationNumber
    JOIN Models m ON v.model = m.model
    WHERE h.clientNumber = 101
      AND h.hireTerminationDate IS NULL;
"""
show(q4, "T4: Make/model of active hires by client 101")


# Transaction 5
# What is the phone number of the site where a specific client’s rented vehicle was originally allocated?
# HireAgreement -> Vehicle -> Site.
q5 = """
    SELECT h.hireNumber, h.vehicleRegistrationNumber, s.siteNumber, s.phoneNumber AS sitePhoneNumber, s.address AS siteAddress
    FROM HireAgreement h
    JOIN Vehicle v ON h.vehicleRegistrationNumber = v.registrationNumber
    JOIN Site s ON v.siteNumber = s.siteNumber
    WHERE  h.clientNumber = 102;
"""
show(q5, "T5: Site phone for vehicles rented by client 102")


db_connect.commit()
db_connect.close()
