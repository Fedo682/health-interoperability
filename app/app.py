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

# A patient only ever advances through these stages, never regresses.
STAGE_RANK = {
    "registered": 0,
    "admitted": 1,
    "tests_ordered": 2,
    "results_in": 3,
    "diagnosed": 4,
    "prescribed": 5,
}


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


def fetchone_dict(db_name, table, pid):
    conn = get_db(db_name)
    row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_gp_row(pid):
    return fetchone_dict("gp_clinic", "patients", pid)


def get_profile(profile_key):
    return next((d for d in diagnosis_catalog.DIAGNOSIS_CATALOG if d["key"] == profile_key), None)


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


def advance_status(pid, stage):
    conn = get_db("gp_clinic")
    cur = conn.execute("SELECT status FROM patients WHERE id=?", (pid,)).fetchone()
    if cur is not None and STAGE_RANK.get(stage, 0) > STAGE_RANK.get(cur["status"], 0):
        conn.execute("UPDATE patients SET status=? WHERE id=?", (stage, pid))
        conn.commit()
    conn.close()


def log_event(pid, channel, title, detail, source_system, dest_system, standard):
    conn = get_db("audit")
    conn.execute(
        "INSERT INTO events (patient_id, ts, channel, title, detail, source_system, dest_system, standard) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (pid, datetime.now().isoformat(timespec="seconds"), channel, title, detail,
         source_system, dest_system, standard),
    )
    conn.commit()
    conn.close()


def get_events(pid):
    conn = get_db("audit")
    rows = conn.execute(
        "SELECT * FROM events WHERE patient_id=? ORDER BY ts ASC, id ASC", (pid,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_admission_diagnosis(pid, icd10_code, diagnosis_text):
    conn = get_db("hospital_ed")
    conn.execute(
        "UPDATE admissions SET icd10_code=?, diagnosis_text=? WHERE id=?",
        (icd10_code, diagnosis_text, pid),
    )
    conn.commit()
    conn.close()


# ── State machine: each step creates/fills the record it represents ──────────

def ensure_admission(pid):
    """Create the Hospital ED admission the first time the patient is sent there."""
    existing = fetchone_dict("hospital_ed", "admissions", pid)
    if existing:
        return existing

    gp = get_gp_row(pid)
    profile = get_profile(gp["profile_key"])
    today = datetime.now().strftime("%Y-%m-%d")

    insert_row("hospital_ed", "admissions",
               (pid, gp["name"], gp["dob"], gp["gender"], profile["icd10_code"], profile["icd10_text"],
                profile["physician"], today))
    advance_status(pid, "admitted")
    log_event(pid, "1", "Patient admitted to Hospital ED",
              f"GP code {gp['local_diagnosis_code']} → ICD-10 {profile['icd10_code']} ({profile['icd10_text']})",
              "GP Clinic", "Hospital ED", "HL7 v2 ADT^A01")
    return fetchone_dict("hospital_ed", "admissions", pid)


def ensure_lab_order(pid):
    """Place the lab order the first time Channel 2 is visited. Result starts empty."""
    existing = fetchone_dict("laboratory", "orders", pid)
    if existing:
        return existing

    gp = get_gp_row(pid)
    profile = get_profile(gp["profile_key"])

    insert_row("laboratory", "orders",
               (pid, gp["name"], profile["loinc_code"], profile["test_name"], "", "", "", "ORDERED", ""))
    advance_status(pid, "tests_ordered")
    log_event(pid, "2", "Lab tests ordered",
              f"{profile['test_name']} (LOINC {profile['loinc_code']}) ordered — awaiting result",
              "Hospital ED", "Laboratory", "HL7 v2 ORM^O01")
    return fetchone_dict("laboratory", "orders", pid)


def fill_lab_result(pid):
    """Return the lab result the first time Channel 3 is visited; idempotent after that."""
    order = ensure_lab_order(pid)
    if order["status"] == "FINAL":
        return order

    gp = get_gp_row(pid)
    profile = get_profile(gp["profile_key"])
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_db("laboratory")
    conn.execute(
        "UPDATE orders SET result_value=?, unit=?, reference_range=?, status=?, result_date=? WHERE id=?",
        (profile["result_value"], profile["unit"], profile["reference_range"], "FINAL", today, pid),
    )
    conn.commit()
    conn.close()
    advance_status(pid, "results_in")
    log_event(pid, "3", "Lab result returned",
              f"{profile['test_name']}: {profile['result_value']} {profile['unit']} (ref {profile['reference_range']})",
              "Laboratory", "Hospital ED", "HL7 v2 ORU^R01")
    return fetchone_dict("laboratory", "orders", pid)


def ensure_radiology_request(pid):
    """Place the radiology request the first time Channel 4 is visited. Report starts empty."""
    existing = fetchone_dict("radiology", "requests", pid)
    if existing:
        return existing

    gp = get_gp_row(pid)
    profile = get_profile(gp["profile_key"])

    insert_row("radiology", "requests",
               (pid, gp["name"], profile["modality"], profile["snomed_proc"], profile["proc_name"],
                "", "", "REQUESTED"))
    advance_status(pid, "tests_ordered")
    log_event(pid, "4", "Radiology imaging requested",
              f"{profile['proc_name']} ({profile['modality']}) requested — awaiting report",
              "Hospital ED", "Radiology", "DICOM Metadata")
    return fetchone_dict("radiology", "requests", pid)


def fill_radiology_report(pid):
    """Return the radiology report the first time Channel 6 is visited; idempotent after that."""
    req = ensure_radiology_request(pid)
    if req["status"] == "REPORTED":
        return req

    gp = get_gp_row(pid)
    profile = get_profile(gp["profile_key"])
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_db("radiology")
    conn.execute(
        "UPDATE requests SET report_text=?, report_date=?, status=? WHERE id=?",
        (profile["report"], today, "REPORTED", pid),
    )
    conn.commit()
    conn.close()
    advance_status(pid, "results_in")
    log_event(pid, "6", "Radiology report filed", profile["report"],
              "Radiology", "Hospital ED", "HL7 v2 ORU^R01")
    return fetchone_dict("radiology", "requests", pid)


def ensure_prescription(pid):
    """Issue (or re-issue, if the final diagnosis changed) the pharmacy prescription."""
    ed = ensure_admission(pid)
    rxnorm, drug, dose, frequency, _route = ed_to_pharmacy.ICD10_TO_MEDICATION.get(
        ed["icd10_code"], ("1191", "Aspirin", "75 mg", "1 tablet once daily", "oral")
    )

    existing = fetchone_dict("pharmacy", "medications", pid)
    if existing and existing["rxnorm_code"] == rxnorm:
        return existing

    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db("pharmacy")
    if existing:
        conn.execute(
            "UPDATE medications SET rxnorm_code=?, drug_name=?, dose=?, frequency=?, prescriber=?, order_date=? "
            "WHERE id=?",
            (rxnorm, drug, dose, frequency, ed["attending_physician"], today, pid),
        )
    else:
        conn.execute(
            "INSERT INTO medications VALUES (?,?,?,?,?,?,?,?)",
            (pid, ed["patient_name"], rxnorm, drug, dose, frequency, ed["attending_physician"], today),
        )
    conn.commit()
    conn.close()
    advance_status(pid, "prescribed")
    log_event(pid, "5", "Prescription issued" if not existing else "Prescription updated",
              f"{drug} {dose} — {frequency} (RxNorm {rxnorm}) for {ed['icd10_code']}",
              "Hospital ED", "Pharmacy", "FHIR R4")
    return fetchone_dict("pharmacy", "medications", pid)


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

    profile = get_profile(diagnosis_key)

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

    insert_row("gp_clinic", "patients",
               (new_id, name, dob, gender, profile["gp_code"], profile["gp_text"], profile["department"],
                diagnosis_key, "registered"))

    return redirect(url_for("patient", pid=new_id))


# ── Patient detail (GP record) ───────────────────────────────────────────────

@app.route("/patient/<int:pid>")
def patient(pid):
    p = get_gp_row(pid)
    if not p:
        return "Patient not found", 404
    ed = fetchone_dict("hospital_ed", "admissions", pid)
    lab = fetchone_dict("laboratory", "orders", pid)
    rad = fetchone_dict("radiology", "requests", pid)
    pharm = fetchone_dict("pharmacy", "medications", pid)
    done = set()
    if ed:
        done.add("1")
    if lab:
        done.add("2")
    if lab and lab["status"] == "FINAL":
        done.add("3")
    if rad:
        done.add("4")
    if rad and rad["status"] == "REPORTED":
        done.add("6")
    if STAGE_RANK.get(p["status"], 0) >= STAGE_RANK["diagnosed"]:
        done.add("Dx")
    if pharm:
        done.add("5")
    return render_template("patient.html", patient=p, done=done)


# ── Channel routes ────────────────────────────────────────────────────────────

@app.route("/channel/1/<int:pid>")
def channel1(pid):
    gp = get_gp_row(pid)
    if not gp:
        return "Patient not found", 404
    ensure_admission(pid)
    result = gp_to_ed.transform(gp)
    choice_channels = [(2, "Order Lab Tests"), (4, "Request Radiology Imaging")]
    return render_template("exchange.html", result=result, pid=pid, channel_num=1,
                            next_channel=None, choice_channels=choice_channels)


@app.route("/channel/2/<int:pid>")
def channel2(pid):
    ed = ensure_admission(pid)
    ensure_lab_order(pid)
    result = ed_to_lab.transform(ed)
    return render_template("exchange.html", result=result, pid=pid, channel_num=2, next_channel=3)


@app.route("/channel/3/<int:pid>")
def channel3(pid):
    order = fill_lab_result(pid)
    result = lab_to_ed.transform(order)
    return render_template("exchange.html", result=result, pid=pid, channel_num=3,
                            next_url=url_for("diagnosis", pid=pid), next_label="Doctor: Final Diagnosis")


@app.route("/channel/4/<int:pid>")
def channel4(pid):
    ed = ensure_admission(pid)
    ensure_radiology_request(pid)
    result = ed_to_radiology.transform(ed)
    return render_template("exchange.html", result=result, pid=pid, channel_num=4, next_channel=6)


@app.route("/channel/6/<int:pid>")
def channel6(pid):
    req = fill_radiology_report(pid)
    result = radiology_to_ed.transform(req)
    return render_template("exchange.html", result=result, pid=pid, channel_num=6,
                            next_url=url_for("diagnosis", pid=pid), next_label="Doctor: Final Diagnosis")


# ── Hospital doctor: final diagnosis ──────────────────────────────────────────

@app.route("/diagnosis/<int:pid>", methods=["GET"])
def diagnosis(pid):
    gp = get_gp_row(pid)
    if not gp:
        return "Patient not found", 404
    ed = ensure_admission(pid)
    lab = fetchone_dict("laboratory", "orders", pid)
    rad = fetchone_dict("radiology", "requests", pid)
    return render_template("diagnosis.html", pid=pid, ed=ed, lab=lab, rad=rad,
                            icd10_options=icd10_options())


@app.route("/diagnosis/<int:pid>", methods=["POST"])
def diagnosis_confirm(pid):
    icd10_code = request.form.get("icd10_code", "").strip()
    diagnosis_text = request.form.get("diagnosis_text", "").strip()
    if icd10_code:
        update_admission_diagnosis(pid, icd10_code, diagnosis_text)
        advance_status(pid, "diagnosed")
        log_event(pid, "Dx", "Final diagnosis confirmed",
                  f"ICD-10 {icd10_code} — {diagnosis_text}",
                  "Hospital ED", "Hospital ED", "Clinical decision")
    return redirect(url_for("channel5", pid=pid))


@app.route("/channel/5/<int:pid>")
def channel5(pid):
    ed = ensure_admission(pid)
    ensure_prescription(pid)
    result = ed_to_pharmacy.transform(ed)
    return render_template("exchange.html", result=result, pid=pid, channel_num=5, next_channel=None)


# ── All providers summary ─────────────────────────────────────────────────────

@app.route("/summary/<int:pid>")
def summary(pid):
    gp = get_gp_row(pid)
    if not gp:
        return "Patient not found", 404
    ed = fetchone_dict("hospital_ed", "admissions", pid)
    lab = fetchone_dict("laboratory", "orders", pid)
    rad = fetchone_dict("radiology", "requests", pid)
    pharm = fetchone_dict("pharmacy", "medications", pid)
    events = get_events(pid)
    return render_template("summary.html", gp=gp, ed=ed, lab=lab, rad=rad, pharm=pharm, pid=pid, events=events)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
