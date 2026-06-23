"""Channel 1: GP Clinic → Hospital ED
Structural:  flat dict (CSV-like row) → HL7 v2 ADT^A01 message
Syntactic:   pipe-delimited HL7 v2 segment encoding
Semantic:    local GP code → ICD-10
"""
from datetime import datetime

# Semantic mapping: local GP codes → ICD-10
LOCAL_TO_ICD10 = {
    "CP-01": ("I20.0",  "Unstable angina"),
    "CP-02": ("I20.9",  "Angina pectoris, unspecified"),
    "CP-03": ("I50.9",  "Heart failure, unspecified"),
    "HT-01": ("I10",    "Essential hypertension"),
    "CP-04": ("I47.9",  "Paroxysmal tachycardia, unspecified"),
    "CP-05": ("I21.9",  "Acute myocardial infarction, unspecified"),
    "RESP-01": ("J18.9",  "Pneumonia, unspecified organism"),
    "GI-01":   ("K35.80", "Unspecified acute appendicitis"),
    "DM-01":   ("E11.65", "Type 2 diabetes mellitus with hyperglycemia"),
}


def transform(patient: dict) -> dict:
    """
    patient: row from gp_clinic.patients
    Returns dict with:
      source_format  — label of input
      source_data    — human-readable source record
      transformation — description of each interoperability type
      hl7_message    — generated HL7 v2 ADT^A01 string
      icd10_code     — mapped ICD-10 code
      icd10_text     — mapped ICD-10 description
    """
    local_code = patient["local_diagnosis_code"]
    icd10_code, icd10_text = LOCAL_TO_ICD10.get(
        local_code, ("Z03.89", "Encounter for observation, no diagnosis found")
    )

    now = datetime.now().strftime("%Y%m%d%H%M%S")
    dob_compact = patient["dob"].replace("-", "")
    name_hl7 = patient["name"].replace(" ", "^")  # "Fadi^Halaweh"

    hl7 = (
        f"MSH|^~\\&|GP_CLINIC|AL-NOUR_CLINIC|HOSPITAL_ED|CITY_HOSPITAL|{now}||ADT^A01|MSG{patient['id']:04d}|P|2.5\r"
        f"PID|1||{patient['id']:06d}^^^GP_CLINIC||{name_hl7}||{dob_compact}|{patient['gender']}|||123 Main St^^Amman^^11180^JO\r"
        f"PV1|1|E|ED^01^A|||||||{patient['referred_to']}\r"
        f"DG1|1||{icd10_code}^{icd10_text}^ICD10|{icd10_text}||A\r"
    )

    source_data = (
        f"id:                  {patient['id']}\n"
        f"name:                {patient['name']}\n"
        f"dob:                 {patient['dob']}\n"
        f"gender:              {patient['gender']}\n"
        f"local_diagnosis_code:{local_code}\n"
        f"diagnosis_text:      {patient['diagnosis_text']}\n"
        f"referred_to:         {patient['referred_to']}"
    )

    return {
        "channel": "Channel 1 — GP Clinic → Hospital ED",
        "source_format": "GP Clinic flat record (CSV / SQLite row)",
        "source_data": source_data,
        "transformation": {
            "structural": "Flat CSV-style row converted to HL7 v2 ADT^A01 message with MSH / PID / PV1 / DG1 segments",
            "syntactic":  "Pipe-delimited HL7 v2.5 encoding with ^ component separator and \\r segment terminator",
            "semantic":   f"Local GP code '{local_code}' → ICD-10 code '{icd10_code}' ({icd10_text})",
        },
        "destination_format": "HL7 v2 ADT^A01 message",
        "destination_data": hl7,
        "icd10_code": icd10_code,
        "icd10_text": icd10_text,
    }
