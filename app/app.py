import sqlite3
import os
import sys
from datetime import datetime

from flask import Flask, render_template, redirect, request, url_for

# Allow importing transformations from sibling package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformations import gp_to_ed, ed_to_lab, lab_to_ed, ed_to_radiology, radiology_to_ed, ed_to_pharmacy
import diagnosis_catalog

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def get_db(name):
    path = os.path.join(DATA_DIR, f"{name}.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def insert_row(db_name, table, values):
    conn = get_db(db_name)
    placeholders = ",".join("?" * len(values))
    conn.execute(f"INSERT INTO {table} VALUES ({placeholders})", values)
    conn.commit()
    conn.close()


def update_admission_diagnosis(pid, icd10_code, diagnosis_text):
    conn = get_db("hospital_ed")
    conn.execute(
        "UPDATE admissions SET icd10_code=?, diagnosis_text=? WHERE id=?",
        (icd10_code, diagnosis_text, pid),
    )
    conn.commit()
    conn.close()


def sync_prescription(pid, icd10_code):
    """Keep the persisted pharmacy record in step with the confirmed diagnosis so the
    summary view matches the live Channel 5 (ED→Pharmacy) prescription. Uses the same
    ICD-10→drug mapping the pharmacy transform uses, with the same fallback."""
    rxnorm, drug, dose, frequency, _route = ed_to_pharmacy.ICD10_TO_MEDICATION.get(
        icd10_code, ("1191", "Aspirin", "75 mg", "1 tablet once daily", "oral")
    )
    conn = get_db("pharmacy")
    conn.execute(
        "UPDATE medications SET rxnorm_code=?, drug_name=?, dose=?, frequency=? WHERE id=?",
        (rxnorm, drug, dose, frequency, pid),
    )
    conn.commit()
    conn.close()


def icd10_options():
    """Distinct (code, text) ICD-10 pairs from the diagnosis catalog, for the
    doctor's final-diagnosis dropdown. All have pharmacy mappings."""
    seen, options = set(), []
    for d in diagnosis_catalog.DIAGNOSIS_CATALOG:
        code = d["icd10_code"]
        if code not in seen:
            seen.add(code)
            options.append((code, d["icd10_text"]))
    return options


# ── Home ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    conn = get_db("gp_clinic")
    patients = conn.execute("SELECT * FROM patients ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", patients=patients)


# ── Add patient ───────────────────────────────────────────────────────────────

@app.route("/patient/new", methods=["GET"])
def new_patient_form():
    return render_template("add_patient.html", diagnoses=diagnosis_catalog.DIAGNOSIS_CATALOG, form={}, error=None)


@app.route("/patient/new", methods=["POST"])
def create_patient():
    name = request.form.get("name", "").strip()
    dob = request.form.get("dob", "").strip()
    gender = request.form.get("gender", "").strip()
    diagnosis_key = request.form.get("diagnosis_key", "").strip()

    profile = next((d for d in diagnosis_catalog.DIAGNOSIS_CATALOG if d["key"] == diagnosis_key), None)

    if not name or not dob or gender not in ("M", "F") or profile is None:
        return render_template(
            "add_patient.html",
            diagnoses=diagnosis_catalog.DIAGNOSIS_CATALOG,
            form={"name": name, "dob": dob, "gender": gender, "diagnosis_key": diagnosis_key},
            error="Please provide a name, date of birth, gender, and diagnosis.",
        ), 400

    conn = get_db("gp_clinic")
    new_id = (conn.execute("SELECT MAX(id) AS m FROM patients").fetchone()["m"] or 0) + 1
    conn.close()

    today = datetime.now().strftime("%Y-%m-%d")

    insert_row("gp_clinic", "patients",
               (new_id, name, dob, gender, profile["gp_code"], profile["gp_text"], profile["department"]))
    insert_row("hospital_ed", "admissions",
               (new_id, name, dob, gender, profile["icd10_code"], profile["icd10_text"], profile["physician"], today))
    insert_row("laboratory", "orders",
               (new_id, name, profile["loinc_code"], profile["test_name"], profile["result_value"],
                profile["unit"], profile["reference_range"], "FINAL", today))
    insert_row("radiology", "requests",
               (new_id, name, profile["modality"], profile["snomed_proc"], profile["proc_name"], profile["report"], today))
    insert_row("pharmacy", "medications",
               (new_id, name, profile["rxnorm"], profile["drug"], profile["dose"], profile["frequency"], profile["physician"], today))

    return redirect(url_for("patient", pid=new_id))


# ── Patient detail (GP record) ───────────────────────────────────────────────

@app.route("/patient/<int:pid>")
def patient(pid):
    conn = get_db("gp_clinic")
    p = conn.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not p:
        return "Patient not found", 404
    return render_template("patient.html", patient=dict(p))


# ── Channel routes ────────────────────────────────────────────────────────────

@app.route("/channel/1/<int:pid>")
def channel1(pid):
    conn = get_db("gp_clinic")
    row = conn.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    conn.close()
    result = gp_to_ed.transform(dict(row))
    choice_channels = [(2, "Order Lab Tests"), (4, "Request Radiology Imaging")]
    return render_template("exchange.html", result=result, pid=pid, channel_num=1,
                            next_channel=None, choice_channels=choice_channels)


@app.route("/channel/2/<int:pid>")
def channel2(pid):
    conn = get_db("hospital_ed")
    row = conn.execute("SELECT * FROM admissions WHERE id=?", (pid,)).fetchone()
    conn.close()
    result = ed_to_lab.transform(dict(row))
    return render_template("exchange.html", result=result, pid=pid, channel_num=2, next_channel=3)


@app.route("/channel/3/<int:pid>")
def channel3(pid):
    conn = get_db("laboratory")
    row = conn.execute("SELECT * FROM orders WHERE id=?", (pid,)).fetchone()
    conn.close()
    result = lab_to_ed.transform(dict(row))
    return render_template("exchange.html", result=result, pid=pid, channel_num=3,
                            next_url=url_for("diagnosis", pid=pid), next_label="Doctor: Final Diagnosis")


@app.route("/channel/4/<int:pid>")
def channel4(pid):
    conn = get_db("hospital_ed")
    row = conn.execute("SELECT * FROM admissions WHERE id=?", (pid,)).fetchone()
    conn.close()
    result = ed_to_radiology.transform(dict(row))
    return render_template("exchange.html", result=result, pid=pid, channel_num=4, next_channel=6)


@app.route("/channel/6/<int:pid>")
def channel6(pid):
    conn = get_db("radiology")
    row = conn.execute("SELECT * FROM requests WHERE id=?", (pid,)).fetchone()
    conn.close()
    result = radiology_to_ed.transform(dict(row))
    return render_template("exchange.html", result=result, pid=pid, channel_num=6,
                            next_url=url_for("diagnosis", pid=pid), next_label="Doctor: Final Diagnosis")


# ── Hospital doctor: final diagnosis ──────────────────────────────────────────

@app.route("/diagnosis/<int:pid>", methods=["GET"])
def diagnosis(pid):
    ed  = dict(get_db("hospital_ed").execute("SELECT * FROM admissions WHERE id=?", (pid,)).fetchone())
    lab = dict(get_db("laboratory").execute("SELECT * FROM orders WHERE id=?", (pid,)).fetchone())
    rad = dict(get_db("radiology").execute("SELECT * FROM requests WHERE id=?", (pid,)).fetchone())
    return render_template("diagnosis.html", pid=pid, ed=ed, lab=lab, rad=rad,
                            icd10_options=icd10_options())


@app.route("/diagnosis/<int:pid>", methods=["POST"])
def diagnosis_confirm(pid):
    icd10_code = request.form.get("icd10_code", "").strip()
    diagnosis_text = request.form.get("diagnosis_text", "").strip()
    if icd10_code:
        update_admission_diagnosis(pid, icd10_code, diagnosis_text)
        sync_prescription(pid, icd10_code)
    return redirect(url_for("channel5", pid=pid))


@app.route("/channel/5/<int:pid>")
def channel5(pid):
    conn = get_db("hospital_ed")
    row = conn.execute("SELECT * FROM admissions WHERE id=?", (pid,)).fetchone()
    conn.close()
    result = ed_to_pharmacy.transform(dict(row))
    return render_template("exchange.html", result=result, pid=pid, channel_num=5, next_channel=None)


# ── All providers summary ─────────────────────────────────────────────────────

@app.route("/summary/<int:pid>")
def summary(pid):
    gp   = dict(get_db("gp_clinic").execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone())
    ed   = dict(get_db("hospital_ed").execute("SELECT * FROM admissions WHERE id=?", (pid,)).fetchone())
    lab  = dict(get_db("laboratory").execute("SELECT * FROM orders WHERE id=?", (pid,)).fetchone())
    rad  = dict(get_db("radiology").execute("SELECT * FROM requests WHERE id=?", (pid,)).fetchone())
    pharm= dict(get_db("pharmacy").execute("SELECT * FROM medications WHERE id=?", (pid,)).fetchone())
    return render_template("summary.html", gp=gp, ed=ed, lab=lab, rad=rad, pharm=pharm, pid=pid)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
