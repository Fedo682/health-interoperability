"""Channel 5: Hospital ED → Pharmacy
Structural:  ED admission + diagnosis → FHIR R4 MedicationRequest JSON
Syntactic:   FHIR RESTful JSON resource
Semantic:    diagnosis-driven drug selection → RxNorm code
"""
import json
from datetime import datetime

# Semantic: ICD-10 → (RxNorm, drug name, dose, frequency)
ICD10_TO_MEDICATION = {
    "I20.0":  ("1191",   "Aspirin",      "75 mg",    "1 tablet once daily",    "oral"),
    "I20.9":  ("56795",  "Nitroglycerin","0.4 mg",   "sublingual PRN chest pain","sublingual"),
    "I21.9":  ("308460", "Clopidogrel",  "75 mg",    "1 tablet once daily",    "oral"),
    "I25.10": ("41493",  "Atorvastatin", "40 mg",    "1 tablet once at night", "oral"),
    "I10":    ("203150", "Lisinopril",   "10 mg",    "1 tablet once daily",    "oral"),
    "I47.2":  ("321064", "Metoprolol",   "50 mg",    "1 tablet twice daily",   "oral"),
    "I47.9":  ("321064", "Metoprolol",   "50 mg",    "1 tablet twice daily",   "oral"),
    "I50.9":  ("203150", "Lisinopril",   "10 mg",    "1 tablet once daily",    "oral"),
    "I20.1":  ("1191",   "Aspirin",      "75 mg",    "1 tablet once daily",    "oral"),
}


def transform(admission: dict) -> dict:
    now = datetime.now().isoformat() + "Z"
    rxnorm, drug, dose, frequency, route = ICD10_TO_MEDICATION.get(
        admission["icd10_code"],
        ("1191", "Aspirin", "75 mg", "1 tablet once daily", "oral")
    )

    fhir_resource = {
        "resourceType": "MedicationRequest",
        "id": f"med-req-{admission['id']:04d}",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": rxnorm,
                    "display": drug
                }
            ],
            "text": drug
        },
        "subject": {
            "reference": f"Patient/{admission['id']:06d}",
            "display": admission["patient_name"]
        },
        "authoredOn": now,
        "requester": {
            "reference": f"Practitioner/doc-{admission['id']:03d}",
            "display": admission["attending_physician"]
        },
        "reasonCode": [
            {
                "coding": [
                    {
                        "system": "http://hl7.org/fhir/sid/icd-10",
                        "code": admission["icd10_code"],
                        "display": admission["diagnosis_text"]
                    }
                ]
            }
        ],
        "dosageInstruction": [
            {
                "text": frequency,
                "route": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "26643006" if route == "oral" else "37839007",
                            "display": "Oral route" if route == "oral" else "Sublingual route"
                        }
                    ]
                },
                "doseAndRate": [
                    {
                        "doseQuantity": {
                            "value": dose.split()[0],
                            "unit": dose.split()[1] if len(dose.split()) > 1 else "mg",
                            "system": "http://unitsofmeasure.org"
                        }
                    }
                ]
            }
        ],
        "dispenseRequest": {
            "quantity": {
                "value": 30,
                "unit": "tablet",
                "system": "http://unitsofmeasure.org"
            },
            "expectedSupplyDuration": {
                "value": 30,
                "unit": "days"
            }
        }
    }

    source_data = (
        f"patient_name:        {admission['patient_name']}\n"
        f"icd10_code:          {admission['icd10_code']}\n"
        f"diagnosis:           {admission['diagnosis_text']}\n"
        f"attending_physician: {admission['attending_physician']}\n"
        f"admission_date:      {admission['admission_date']}"
    )

    return {
        "channel": "Channel 5 — Hospital ED → Pharmacy",
        "source_format": "Hospital ED admission record (SQLite row / JSON)",
        "source_data": source_data,
        "transformation": {
            "structural": "ED admission dict → FHIR R4 MedicationRequest JSON resource with all required fields",
            "syntactic":  "FHIR RESTful JSON; resource type, status, intent, coding, dosage, and dispense sections per HL7 FHIR R4 spec",
            "semantic":   f"ICD-10 '{admission['icd10_code']}' ({admission['diagnosis_text']}) → RxNorm '{rxnorm}' ({drug} {dose}); route coded in SNOMED CT",
        },
        "destination_format": "FHIR R4 MedicationRequest (JSON)",
        "destination_data": json.dumps(fhir_resource, indent=2),
        "rxnorm_code": rxnorm,
        "drug_name": drug,
        "dose": dose,
    }
