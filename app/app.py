import sqlite3
import os
import sys

from flask import Flask, render_template, redirect, url_for

# Allow importing transformations from sibling package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformations import gp_to_ed, ed_to_lab, lab_to_ed, ed_to_radiology, ed_to_pharmacy

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def get_db(name):
    path = os.path.join(DATA_DIR, f"{name}.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


# ── Home ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    conn = get_db("gp_clinic")
    patients = conn.execute("SELECT * FROM patients ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", patients=patients)


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
    return render_template("exchange.html", result=result, pid=pid, channel_num=1, next_channel=2)


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
    return render_template("exchange.html", result=result, pid=pid, channel_num=3, next_channel=4)


@app.route("/channel/4/<int:pid>")
def channel4(pid):
    conn = get_db("hospital_ed")
    row = conn.execute("SELECT * FROM admissions WHERE id=?", (pid,)).fetchone()
    conn.close()
    result = ed_to_radiology.transform(dict(row))
    return render_template("exchange.html", result=result, pid=pid, channel_num=4, next_channel=5)


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
    app.run(debug=True, port=5000)
