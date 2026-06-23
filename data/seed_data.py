"""Seeds the 5 provider databases + an audit log.

Unlike the old version, only the GP Clinic record is populated upfront.
Hospital ED / Laboratory / Radiology / Pharmacy tables are created EMPTY:
those rows are produced on demand as the patient is walked through the
interoperability channels in app.py (ensure_admission, ensure_lab_order,
fill_lab_result, etc.), so the demo proves the system actually does the
work rather than displaying pre-baked answers.

diagnosis_catalog.py is the single source of clinical truth: each seeded
patient references a profile_key, and every downstream record is derived
from that profile when its step actually fires.
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app"))
import diagnosis_catalog

BASE = os.path.dirname(os.path.abspath(__file__))

# (name, dob, gender, profile_key) — profile_key must exist in DIAGNOSIS_CATALOG
PATIENTS = [
    ("Fadi Halaweh",    "1985-03-12", "M", "chest_pain_exertion"),
    ("Ghassan Halaweh", "1978-07-24", "M", "chest_pain_radiating"),
    ("Omar Taweel",     "1990-11-05", "M", "pneumonia"),
    ("Tariq Khalil",    "1965-01-30", "M", "hypertension"),
    ("Omar Diebas",     "1972-09-18", "M", "appendicitis"),
    ("Qais Alqrem",     "1988-04-22", "M", "diabetes"),
]


def _profile(key):
    profile = next((d for d in diagnosis_catalog.DIAGNOSIS_CATALOG if d["key"] == key), None)
    if profile is None:
        raise ValueError(f"Unknown diagnosis_catalog key: {key}")
    return profile


def create_gp_clinic():
    path = os.path.join(BASE, "gp_clinic.db")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS patients")
    c.execute("""
        CREATE TABLE patients (
            id INTEGER PRIMARY KEY,
            name TEXT,
            dob TEXT,
            gender TEXT,
            local_diagnosis_code TEXT,
            diagnosis_text TEXT,
            referred_to TEXT,
            profile_key TEXT,
            status TEXT
        )
    """)
    for i, (name, dob, gender, key) in enumerate(PATIENTS):
        p = _profile(key)
        c.execute("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?)",
                   (i + 1, name, dob, gender, p["gp_code"], p["gp_text"], p["department"],
                    key, "registered"))
    conn.commit()
    conn.close()
    print(f"  gp_clinic.db created ({len(PATIENTS)} patients, all 'registered')")


def create_hospital_ed():
    path = os.path.join(BASE, "hospital_ed.db")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS admissions")
    c.execute("""
        CREATE TABLE admissions (
            id INTEGER PRIMARY KEY,
            patient_name TEXT,
            dob TEXT,
            gender TEXT,
            icd10_code TEXT,
            diagnosis_text TEXT,
            attending_physician TEXT,
            admission_date TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("  hospital_ed.db created (empty — admissions are created when Channel 1 fires)")


def create_laboratory():
    path = os.path.join(BASE, "laboratory.db")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS orders")
    c.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            patient_name TEXT,
            loinc_code TEXT,
            test_name TEXT,
            result_value TEXT,
            unit TEXT,
            reference_range TEXT,
            status TEXT,
            result_date TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("  laboratory.db created (empty — orders are created when Channel 2 fires)")


def create_radiology():
    path = os.path.join(BASE, "radiology.db")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS requests")
    c.execute("""
        CREATE TABLE requests (
            id INTEGER PRIMARY KEY,
            patient_name TEXT,
            modality TEXT,
            snomed_procedure_code TEXT,
            procedure_name TEXT,
            report_text TEXT,
            report_date TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("  radiology.db created (empty — requests are created when Channel 4 fires)")


def create_pharmacy():
    path = os.path.join(BASE, "pharmacy.db")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS medications")
    c.execute("""
        CREATE TABLE medications (
            id INTEGER PRIMARY KEY,
            patient_name TEXT,
            rxnorm_code TEXT,
            drug_name TEXT,
            dose TEXT,
            frequency TEXT,
            prescriber TEXT,
            order_date TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("  pharmacy.db created (empty — prescriptions are created when Channel 5 fires)")


def create_audit():
    path = os.path.join(BASE, "audit.db")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS events")
    c.execute("""
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            ts TEXT,
            channel TEXT,
            title TEXT,
            detail TEXT,
            source_system TEXT,
            dest_system TEXT,
            standard TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("  audit.db created (empty — populated as real events fire)")


if __name__ == "__main__":
    print("Seeding databases...")
    create_gp_clinic()
    create_hospital_ed()
    create_laboratory()
    create_radiology()
    create_pharmacy()
    create_audit()
    print("All databases ready. Patients start at 'registered' — walk the channels to build their record.")
