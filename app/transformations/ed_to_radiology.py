"""Channel 4: Hospital ED → Radiology
Structural:  ED admission JSON → DICOM-style metadata text (Key=Value)
Syntactic:   DICOM attribute tag format
Semantic:    local imaging request → SNOMED CT procedure code
"""
from datetime import datetime

# Semantic: ICD-10 diagnosis → SNOMED CT imaging procedure
ICD10_TO_SNOMED_PROCEDURE = {
    "I20.0":  ("399208008", "Plain chest X-ray",         "CR"),
    "I20.9":  ("399208008", "Plain chest X-ray",         "CR"),
    "I21.9":  ("399208008", "Plain chest X-ray",         "CR"),
    "I25.10": ("77477000",  "CT of thorax",              "CT"),
    "I10":    ("399208008", "Plain chest X-ray",         "CR"),
    "I47.2":  ("399208008", "Plain chest X-ray",         "CR"),
    "I47.9":  ("399208008", "Plain chest X-ray",         "CR"),
    "I50.9":  ("77477000",  "CT of thorax",              "CT"),
    "I20.1":  ("399208008", "Plain chest X-ray",         "CR"),
    "J18.9":  ("399208008", "Plain chest X-ray",         "CR"),
    "K35.80": ("169070000", "CT of abdomen and pelvis",  "CT"),
    "E11.65": ("399208008", "Plain chest X-ray",         "CR"),
}


def transform(admission: dict) -> dict:
    now = datetime.now()
    study_uid = f"1.2.840.10008.{admission['id']}.{now.strftime('%Y%m%d%H%M%S')}"
    snomed_code, procedure_name, modality = ICD10_TO_SNOMED_PROCEDURE.get(
        admission["icd10_code"],
        ("399208008", "Plain chest X-ray", "CR")
    )

    dicom_text = (
        f"(0008,0016) SOPClassUID                       = 1.2.840.10008.5.1.4.1.1.1\n"
        f"(0008,0020) StudyDate                         = {now.strftime('%Y%m%d')}\n"
        f"(0008,0030) StudyTime                         = {now.strftime('%H%M%S')}\n"
        f"(0008,0060) Modality                          = {modality}\n"
        f"(0008,1030) StudyDescription                  = {procedure_name}\n"
        f"(0008,103E) SeriesDescription                 = Cardiac workup — {admission['diagnosis_text']}\n"
        f"(0010,0010) PatientName                       = {admission['patient_name'].replace(' ', '^')}\n"
        f"(0010,0020) PatientID                         = {admission['id']:06d}\n"
        f"(0010,0030) PatientBirthDate                  = {admission['dob'].replace('-', '')}\n"
        f"(0010,0040) PatientSex                        = {admission['gender']}\n"
        f"(0020,000D) StudyInstanceUID                  = {study_uid}\n"
        f"(0032,1060) RequestedProcedureDescription     = {procedure_name}\n"
        f"(0040,0007) ScheduledProcedureStepDescription = {procedure_name} for {admission['icd10_code']}\n"
        f"(0008,0100) CodeValue (SNOMED CT)             = {snomed_code}\n"
        f"(0008,0104) CodeMeaning (SNOMED CT)           = {procedure_name}\n"
        f"(0040,A160) ReferringDiagnosis (ICD-10)       = {admission['icd10_code']} — {admission['diagnosis_text']}\n"
        f"(0008,0090) ReferringPhysicianName            = {admission['attending_physician'].replace(' ', '^')}\n"
    )

    source_data = (
        f"patient_name:        {admission['patient_name']}\n"
        f"dob:                 {admission['dob']}\n"
        f"gender:              {admission['gender']}\n"
        f"icd10_code:          {admission['icd10_code']}\n"
        f"diagnosis:           {admission['diagnosis_text']}\n"
        f"attending_physician: {admission['attending_physician']}\n"
        f"admission_date:      {admission['admission_date']}"
    )

    return {
        "channel": "Channel 4 — Hospital ED → Radiology",
        "source_format": "Hospital ED admission record (SQLite row / JSON)",
        "source_data": source_data,
        "transformation": {
            "structural": "JSON admission object → DICOM-style attribute dataset (Tag=Value pairs per DICOM PS 3.3)",
            "syntactic":  "DICOM attribute tag notation (gggg,eeee) with group/element numbering; modality and UIDs set appropriately",
            "semantic":   f"ICD-10 '{admission['icd10_code']}' ({admission['diagnosis_text']}) → SNOMED CT procedure '{snomed_code}' ({procedure_name}); modality set to {modality}",
        },
        "destination_format": "DICOM metadata (Key=Value text representation)",
        "destination_data": dicom_text,
        "snomed_code": snomed_code,
        "procedure_name": procedure_name,
        "modality": modality,
    }
