"""Channel 6: Radiology → Hospital ED
Structural:  DICOM study + free-text report → HL7 v2 ORU^R01 result message
Syntactic:   HL7 v2 OBX segments (one coded, one narrative)
Semantic:    SNOMED CT procedure code carried through as the coded finding
"""
from datetime import datetime


def transform(radiology_request: dict) -> dict:
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    name_hl7 = radiology_request["patient_name"].replace(" ", "^")

    hl7 = (
        f"MSH|^~\\&|RADIOLOGY|IMAGING_CENTRE|HOSPITAL_ED|CITY_HOSPITAL|{now}||ORU^R01|RAD{radiology_request['id']:04d}|P|2.5\r"
        f"PID|1||{radiology_request['id']:06d}^^^IMAGING_CENTRE||{name_hl7}\r"
        f"OBR|1|{radiology_request['id']:04d}|{radiology_request['id']:04d}A|"
        f"{radiology_request['snomed_procedure_code']}^{radiology_request['procedure_name']}^SCT|||{now}\r"
        f"OBX|1|CWE|{radiology_request['snomed_procedure_code']}^{radiology_request['procedure_name']}^SCT||"
        f"{radiology_request['snomed_procedure_code']}^{radiology_request['procedure_name']}^SCT|||||F|||{now}\r"
        f"OBX|2|TX|IMPRESSION^Radiology Impression^L||{radiology_request['report_text']}|||||F|||{now}\r"
    )

    source_data = (
        f"patient_name:          {radiology_request['patient_name']}\n"
        f"modality:              {radiology_request['modality']}\n"
        f"snomed_procedure_code: {radiology_request['snomed_procedure_code']}\n"
        f"procedure_name:        {radiology_request['procedure_name']}\n"
        f"report_text:           {radiology_request['report_text']}\n"
        f"report_date:           {radiology_request['report_date']}"
    )

    return {
        "channel": "Channel 6 — Radiology → Hospital ED",
        "source_format": "Radiology DICOM study + report (SQLite row / JSON)",
        "source_data": source_data,
        "transformation": {
            "structural": "DICOM study + free-text report → HL7 v2 ORU^R01 with MSH / PID / OBR / OBX segments",
            "syntactic":  "HL7 v2.5 pipe-delimited; coded finding in OBX-1 (CWE), narrative impression in OBX-2 (TX)",
            "semantic":   f"SNOMED CT procedure '{radiology_request['snomed_procedure_code']}' ({radiology_request['procedure_name']}) carried through as the coded result returned to the ordering physician",
        },
        "destination_format": "HL7 v2 ORU^R01 Result message",
        "destination_data": hl7,
    }
