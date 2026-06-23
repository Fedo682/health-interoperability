"""Channel 3: Laboratory → Hospital ED
Structural:  lab SQLite result → HL7 v2 ORU^R01 result message
Syntactic:   HL7 v2 OBX segments per result
Semantic:    abnormal result value → SNOMED CT finding
"""
from datetime import datetime

# Semantic: LOINC test + abnormal flag → SNOMED CT finding
LOINC_TO_SNOMED = {
    "10839-9": ("414916001", "Elevated troponin I (finding)"),
    "718-7":   ("271737000", "Anemia (disorder)"),
    "2093-3":  ("13644009",  "Hypercholesterolemia (disorder)"),
    "2160-0":  ("44054006",  "Diabetes mellitus type 2 (finding)"),  # creatinine elevated
    "6690-2":  ("414850009", "Leukocytosis (finding)"),
    "2823-3":  ("43339004",  "Hypokalemia (disorder)"),
    "58410-2": ("271737000", "Anemia (disorder)"),
    "57698-3": ("13644009",  "Hypercholesterolemia (disorder)"),
    "51990-0": ("444244002", "Metabolic panel abnormal (finding)"),
    "49506-3": ("414916001", "Elevated troponin (finding)"),
    "2345-7":  ("80394007",  "Hyperglycemia (disorder)"),
}


def _abnormal_flag(result_value: str, reference_range: str) -> str:
    """Simple flag: H=high, L=low, N=normal."""
    try:
        val = float(result_value)
        parts = reference_range.replace("<", "0-").replace(">", "").split("-")
        if len(parts) == 2:
            lo, hi = float(parts[0]), float(parts[1])
            if val > hi:
                return "H"
            if val < lo:
                return "L"
    except Exception:
        pass
    return "N"


def transform(lab_order: dict) -> dict:
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    name_hl7 = lab_order["patient_name"].replace(" ", "^")
    flag = _abnormal_flag(lab_order["result_value"], lab_order["reference_range"])

    snomed_code, snomed_text = LOINC_TO_SNOMED.get(
        lab_order["loinc_code"], ("404684003", "Clinical finding (finding)")
    )

    hl7 = (
        f"MSH|^~\\&|LABORATORY|LAB_SYSTEM|HOSPITAL_ED|CITY_HOSPITAL|{now}||ORU^R01|RES{lab_order['id']:04d}|P|2.5\r"
        f"PID|1||{lab_order['id']:06d}^^^LAB_SYSTEM||{name_hl7}\r"
        f"OBR|1|{lab_order['id']:04d}|{lab_order['id']:04d}A|{lab_order['loinc_code']}^{lab_order['test_name']}^LN|||{now}\r"
        f"OBX|1|NM|{lab_order['loinc_code']}^{lab_order['test_name']}^LN||{lab_order['result_value']}|"
        f"{lab_order['unit']}|{lab_order['reference_range']}|{flag}|||{lab_order['status']}|||{now}\r"
        f"OBX|2|CWE|{snomed_code}^{snomed_text}^SCT||{snomed_code}^{snomed_text}^SCT\r"
    )

    source_data = (
        f"patient_name:    {lab_order['patient_name']}\n"
        f"loinc_code:      {lab_order['loinc_code']}\n"
        f"test_name:       {lab_order['test_name']}\n"
        f"result_value:    {lab_order['result_value']} {lab_order['unit']}\n"
        f"reference_range: {lab_order['reference_range']}\n"
        f"status:          {lab_order['status']}\n"
        f"result_date:     {lab_order['result_date']}"
    )

    return {
        "channel": "Channel 3 — Laboratory → Hospital ED",
        "source_format": "Laboratory result record (SQLite row / JSON)",
        "source_data": source_data,
        "transformation": {
            "structural": "Lab result dict → HL7 v2 ORU^R01 with MSH / PID / OBR / OBX segments",
            "syntactic":  "HL7 v2.5 pipe-delimited; numeric result in OBX-5, units in OBX-6, range in OBX-7, flag in OBX-8",
            "semantic":   f"LOINC '{lab_order['loinc_code']}' ({lab_order['test_name']}) → SNOMED CT '{snomed_code}' — {snomed_text}",
        },
        "destination_format": "HL7 v2 ORU^R01 Result message",
        "destination_data": hl7,
        "abnormal_flag": flag,
        "snomed_code": snomed_code,
        "snomed_text": snomed_text,
    }
