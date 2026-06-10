import sqlite3
import os

BASE = os.path.dirname(os.path.abspath(__file__))

PATIENTS = [
    ("Fadi Halaweh",    "1985-03-12", "M"),
    ("Ghassan Halaweh", "1978-07-24", "M"),
    ("Omar Taweel",     "1990-11-05", "M"),
    ("Tariq Khalil",    "1965-01-30", "M"),
    ("Omar Diebas",     "1972-09-18", "M"),
    ("Qais Alqrem",     "1988-04-22", "M"),
]

GP_DIAGNOSES = [
    ("CP-01", "Chest pain with exertion",          "Cardiology"),
    ("CP-02", "Chest tightness at rest",           "Cardiology"),
    ("CP-03", "Shortness of breath + chest pain",  "Cardiology"),
    ("HT-01", "Hypertension uncontrolled",         "Cardiology"),
    ("CP-04", "Palpitations and chest discomfort", "Cardiology"),
    ("CP-05", "Chest pain radiating to left arm",  "Cardiology"),
]

ED_DIAGNOSES = [
    ("I20.0", "Unstable angina",                        "Dr. Samira Nasser"),
    ("I21.9", "Acute myocardial infarction, unspecified","Dr. Khalid Mansour"),
    ("I25.10","Atherosclerotic heart disease",           "Dr. Samira Nasser"),
    ("I10",   "Essential hypertension",                  "Dr. Khalid Mansour"),
    ("I47.2", "Ventricular tachycardia",                 "Dr. Samira Nasser"),
    ("I20.1", "Angina pectoris with documented spasm",   "Dr. Khalid Mansour"),
]

LAB_TESTS = [
    ("10839-9", "Troponin I",          "0.08", "ng/mL", "<0.04",  "FINAL", "2026-06-10"),
    ("718-7",   "Hemoglobin",          "11.2", "g/dL",  "13.5-17.5","FINAL","2026-06-10"),
    ("2093-3",  "Total Cholesterol",   "245",  "mg/dL", "<200",   "FINAL", "2026-06-10"),
    ("2160-0",  "Creatinine",          "1.1",  "mg/dL", "0.7-1.2","FINAL", "2026-06-10"),
    ("6690-2",  "WBC",                 "11.5", "10^3/uL","4.5-11.0","FINAL","2026-06-10"),
    ("2823-3",  "Potassium",           "3.4",  "mEq/L", "3.5-5.0","FINAL", "2026-06-10"),
]

RADIOLOGY = [
    ("CR", "399208008", "Plain chest X-ray",
     "Cardiomegaly with mild pulmonary vascular congestion. No pneumothorax."),
    ("CR", "399208008", "Plain chest X-ray",
     "Mild cardiomegaly. Clear lung fields. No pleural effusion."),
    ("CT", "77477000",  "CT thorax",
     "No pulmonary embolism. Mild pericardial thickening noted."),
    ("CR", "399208008", "Plain chest X-ray",
     "Normal cardiac silhouette. Mild aortic calcification."),
    ("CT", "77477000",  "CT thorax",
     "Enlarged mediastinum. Recommend cardiac MRI for further evaluation."),
    ("CR", "399208008", "Plain chest X-ray",
     "Borderline cardiomegaly. No acute infiltrates."),
]

MEDICATIONS = [
    ("1191",   "Aspirin",      "75mg",   "Once daily",   "Dr. Samira Nasser"),
    ("41493",  "Atorvastatin", "40mg",   "Once at night","Dr. Khalid Mansour"),
    ("321064", "Metoprolol",   "50mg",   "Twice daily",  "Dr. Samira Nasser"),
    ("203150", "Lisinopril",   "10mg",   "Once daily",   "Dr. Khalid Mansour"),
    ("56795",  "Nitroglycerin","0.4mg",  "PRN chest pain","Dr. Samira Nasser"),
    ("308460", "Clopidogrel",  "75mg",   "Once daily",   "Dr. Khalid Mansour"),
]


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
            referred_to TEXT
        )
    """)
    for i, (name, dob, gender) in enumerate(PATIENTS):
        code, text, ref = GP_DIAGNOSES[i]
        c.execute("INSERT INTO patients VALUES (?,?,?,?,?,?,?)",
                  (i+1, name, dob, gender, code, text, ref))
    conn.commit()
    conn.close()
    print(f"  gp_clinic.db created ({len(PATIENTS)} patients)")


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
    for i, (name, dob, gender) in enumerate(PATIENTS):
        icd, diag, doc = ED_DIAGNOSES[i]
        c.execute("INSERT INTO admissions VALUES (?,?,?,?,?,?,?,?)",
                  (i+1, name, dob, gender, icd, diag, doc, "2026-06-10"))
    conn.commit()
    conn.close()
    print(f"  hospital_ed.db created ({len(PATIENTS)} admissions)")


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
    for i, (name, _, _) in enumerate(PATIENTS):
        loinc, test, val, unit, ref, status, date = LAB_TESTS[i]
        c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)",
                  (i+1, name, loinc, test, val, unit, ref, status, date))
    conn.commit()
    conn.close()
    print(f"  laboratory.db created ({len(PATIENTS)} orders)")


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
            report_date TEXT
        )
    """)
    for i, (name, _, _) in enumerate(PATIENTS):
        mod, snomed, proc, report = RADIOLOGY[i]
        c.execute("INSERT INTO requests VALUES (?,?,?,?,?,?,?)",
                  (i+1, name, mod, snomed, proc, report, "2026-06-10"))
    conn.commit()
    conn.close()
    print(f"  radiology.db created ({len(PATIENTS)} requests)")


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
    for i, (name, _, _) in enumerate(PATIENTS):
        rxnorm, drug, dose, freq, doc = MEDICATIONS[i]
        c.execute("INSERT INTO medications VALUES (?,?,?,?,?,?,?,?)",
                  (i+1, name, rxnorm, drug, dose, freq, doc, "2026-06-10"))
    conn.commit()
    conn.close()
    print(f"  pharmacy.db created ({len(PATIENTS)} medications)")


if __name__ == "__main__":
    print("Seeding databases...")
    create_gp_clinic()
    create_hospital_ed()
    create_laboratory()
    create_radiology()
    create_pharmacy()
    print("All databases ready.")
