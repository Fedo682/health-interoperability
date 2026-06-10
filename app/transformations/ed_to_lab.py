"""Channel 2: Hospital ED → Laboratory
Structural:  internal ED admission dict → HL7 v2 ORM^O01 order message
Syntactic:   HL7 v2 segment structure
Semantic:    ED test name → LOINC code
"""
from datetime import datetime

# Semantic mapping: ED test name → LOINC
TEST_TO_LOINC = {
    "Troponin I":       ("10839-9",  "Troponin I [Mass/volume] in Serum or Plasma"),
    "CBC":              ("58410-2",  "CBC panel - Blood by Automated count"),
    "Lipid Panel":      ("57698-3",  "Lipid panel with direct LDL - Serum or Plasma"),
    "BMP":              ("51990-0",  "Basic metabolic panel - Blood"),
    "Cardiac Enzymes":  ("49506-3",  "Cardiac troponin panel"),
}

# Default ordered tests per cardiac presentation
DEFAULT_TESTS = ["Troponin I", "CBC", "Lipid Panel", "BMP"]


def transform(admission: dict) -> dict:
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    name_hl7 = admission["patient_name"].replace(" ", "^")
    dob_compact = admission["dob"].replace("-", "")

    segments = [
        f"MSH|^~\\&|HOSPITAL_ED|CITY_HOSPITAL|LABORATORY|LAB_SYSTEM|{now}||ORM^O01|ORD{admission['id']:04d}|P|2.5",
        f"PID|1||{admission['id']:06d}^^^HOSPITAL_ED||{name_hl7}||{dob_compact}|{admission['gender']}",
        f"PV1|1|E|ED^01^A|||{admission['attending_physician']}",
    ]

    loinc_rows = []
    for idx, test_name in enumerate(DEFAULT_TESTS, start=1):
        loinc_code, loinc_desc = TEST_TO_LOINC.get(test_name, ("00000-0", test_name))
        segments.append(
            f"OBR|{idx}|{admission['id']:04d}{idx}|{admission['id']:04d}{idx}A|"
            f"{loinc_code}^{loinc_desc}^LN|||{now}||||||||{admission['attending_physician']}|||STAT"
        )
        loinc_rows.append(f"  {test_name:20s} → LOINC {loinc_code}  ({loinc_desc})")

    hl7 = "\r".join(segments)

    source_data = (
        f"patient_name:        {admission['patient_name']}\n"
        f"dob:                 {admission['dob']}\n"
        f"gender:              {admission['gender']}\n"
        f"icd10_code:          {admission['icd10_code']}\n"
        f"diagnosis:           {admission['diagnosis_text']}\n"
        f"attending_physician: {admission['attending_physician']}\n"
        f"admission_date:      {admission['admission_date']}\n"
        f"tests_ordered:       {', '.join(DEFAULT_TESTS)}"
    )

    return {
        "channel": "Channel 2 — Hospital ED → Laboratory",
        "source_format": "Hospital ED admission record (SQLite row / internal JSON)",
        "source_data": source_data,
        "transformation": {
            "structural": "ED admission dict expanded with ordered tests → HL7 v2 ORM^O01 with MSH / PID / PV1 / OBR segments",
            "syntactic":  "HL7 v2.5 pipe-delimited encoding; each test becomes an OBR segment",
            "semantic":   "ED test names mapped to LOINC codes:\n" + "\n".join(loinc_rows),
        },
        "destination_format": "HL7 v2 ORM^O01 Lab Order message",
        "destination_data": hl7,
    }
