const pptxgen = require("pptxgenjs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
pres.title = "COMP3342 Health Interoperability";
pres.author = "Group [GROUP NUMBER]";

const PHOTOS = path.join(__dirname, "member_photos");

// ── Color palette ──────────────────────────────────────────────────────────
const C = {
  navy:      "1E3A8A",
  blue:      "1E40AF",
  blueLight: "3B82F6",
  teal:      "0D9488",
  tealLight: "CCFBF1",
  amber:     "D97706",
  amberLight:"FEF3C7",
  purple:    "7C3AED",
  orange:    "EA580C",
  green:     "059669",
  red:       "DC2626",
  white:     "FFFFFF",
  offWhite:  "F8FAFC",
  slate:     "475569",
  slateLight:"E2E8F0",
  dark:      "0F172A",
};

// ── Reusable helpers ───────────────────────────────────────────────────────
const W = 13.3, H = 7.5;

function darkBg(slide) {
  slide.background = { color: C.dark };
}

function lightBg(slide) {
  slide.background = { color: "F0F4F8" };
}

function addHeader(slide, title, subtitle, accentColor = C.blueLight) {
  // Top accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 0.07, fill: { color: accentColor }, line: { color: accentColor }
  });
  slide.addText(title, {
    x: 0.4, y: 0.18, w: W - 0.8, h: 0.55,
    fontSize: 22, bold: true, color: C.dark, fontFace: "Calibri", margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.4, y: 0.72, w: W - 0.8, h: 0.3,
      fontSize: 11, color: C.slate, fontFace: "Calibri", margin: 0
    });
  }
  // Divider
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.06, w: W - 0.8, h: 0.02,
    fill: { color: C.slateLight }, line: { color: C.slateLight }
  });
}

function addFooter(slide, text = "COMP3342 — Health Systems Interoperability & Integration") {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: H - 0.35, w: W, h: 0.35, fill: { color: C.dark }, line: { color: C.dark }
  });
  slide.addText(text, {
    x: 0.4, y: H - 0.32, w: W - 0.8, h: 0.28,
    fontSize: 9, color: "94A3B8", fontFace: "Calibri", margin: 0
  });
}

function card(slide, x, y, w, h, fillColor = C.white, borderColor = C.slateLight) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: fillColor },
    line: { color: borderColor, width: 0.5 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 }
  });
}

function accentCard(slide, x, y, w, h, accent) {
  card(slide, x, y, w, h);
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.06, h,
    fill: { color: accent }, line: { color: accent }
  });
}

function channelBadge(slide, x, y, num, label, color) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.36, h: 0.36,
    fill: { color }, line: { color },
    shadow: { type: "outer", blur: 4, offset: 1, angle: 135, color: "000000", opacity: 0.2 }
  });
  slide.addText(String(num), {
    x, y, w: 0.36, h: 0.36,
    fontSize: 13, bold: true, color: C.white, align: "center", valign: "middle",
    fontFace: "Calibri", margin: 0
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 1 — Title
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  darkBg(s);

  // Left accent stripe
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: H, fill: { color: C.blue }, line: { color: C.blue }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.18, y: 0, w: 0.06, h: H, fill: { color: C.teal }, line: { color: C.teal }
  });

  // Course tag
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 0.55, w: 1.6, h: 0.32,
    fill: { color: C.blue }, line: { color: C.blue }
  });
  s.addText("COMP3342", {
    x: 0.6, y: 0.55, w: 1.6, h: 0.32,
    fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle",
    fontFace: "Calibri", charSpacing: 3, margin: 0
  });

  s.addText("Health Systems", {
    x: 0.55, y: 1.1, w: 11, h: 0.9,
    fontSize: 52, bold: true, color: C.white, fontFace: "Calibri",
    charSpacing: -1, margin: 0
  });
  s.addText("Interoperability", {
    x: 0.55, y: 1.95, w: 11, h: 0.9,
    fontSize: 52, bold: true, color: C.blueLight, fontFace: "Calibri",
    charSpacing: -1, margin: 0
  });
  s.addText("& Integration", {
    x: 0.55, y: 2.78, w: 11, h: 0.7,
    fontSize: 38, bold: false, color: "94A3B8", fontFace: "Calibri", margin: 0
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 3.65, w: 4.5, h: 0.03, fill: { color: C.teal }, line: { color: C.teal }
  });

  s.addText("Cardiac Emergency Patient Journey\nDemonstrating Structural, Syntactic & Semantic Interoperability\nAcross 5 Healthcare Providers & 5 Integration Channels", {
    x: 0.55, y: 3.82, w: 8.5, h: 1.1,
    fontSize: 13, color: "CBD5E1", fontFace: "Calibri", lineSpacingMultiple: 1.4, margin: 0
  });

  // Standards badges
  const stds = ["HL7 v2", "FHIR R4", "DICOM", "ICD-10", "LOINC", "SNOMED CT", "RxNorm"];
  stds.forEach((std, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.55 + col * 1.6, y: 5.15 + row * 0.42, w: 1.45, h: 0.32,
      fill: { color: C.navy }, line: { color: C.blue }
    });
    s.addText(std, {
      x: 0.55 + col * 1.6, y: 5.15 + row * 0.42, w: 1.45, h: 0.32,
      fontSize: 9, bold: true, color: C.blueLight, align: "center", valign: "middle",
      fontFace: "Calibri", margin: 0
    });
  });

  s.addText("Group [GROUP NUMBER]  •  June 17, 2026", {
    x: 0.55, y: H - 0.55, w: 6, h: 0.3,
    fontSize: 10, color: "64748B", fontFace: "Calibri", margin: 0
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 2 — Group Members
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  lightBg(s);
  addHeader(s, "Group Members", "COMP3342 Project Team", C.blue);
  addFooter(s);

  const members = [
    { name: "Tariq Makho",   file: "Tariq_Makho.jpg",   ext: "jpg", task: "Scenario Design\n& Timeline" },
    { name: "Omar Diebas",   file: "Omar_Diebas.jpg",   ext: "jpg", task: "Dataset Creation\n& Databases" },
    { name: "Qais Alqarem",  file: "Qais_Alqarem.jpg",  ext: "jpg", task: "Interoperability\nChannels 1 & 2" },
    { name: "Omar Taweel",   file: "Omar_Taweel.jpg",   ext: "jpg", task: "Channels 3, 4 & 5\n& Transformations" },
    { name: "Fadi Halaweh",  file: "Fadi_Halaweh.png",  ext: "png", task: "Demo Application\n& Report" },
  ];

  const totalW = 13.3 - 0.8;
  const cardW = totalW / 5;
  const startX = 0.4;
  const startY = 1.3;

  members.forEach((m, i) => {
    const x = startX + i * cardW;
    card(s, x, startY, cardW - 0.15, 5.5);

    // Photo circle background
    s.addShape(pres.shapes.OVAL, {
      x: x + (cardW - 0.15) / 2 - 0.9, y: startY + 0.25,
      w: 1.8, h: 1.8,
      fill: { color: C.slateLight }, line: { color: C.slateLight }
    });

    // Photo
    s.addImage({
      path: path.join(PHOTOS, m.file),
      x: x + (cardW - 0.15) / 2 - 0.9, y: startY + 0.25,
      w: 1.8, h: 1.8,
      rounding: true,
      sizing: { type: "cover", w: 1.8, h: 1.8 }
    });

    // Name
    s.addText(m.name, {
      x: x + 0.1, y: startY + 2.2,
      w: cardW - 0.35, h: 0.42,
      fontSize: 12, bold: true, color: C.dark, align: "center",
      fontFace: "Calibri", margin: 0
    });

    // Role/task
    s.addText(m.task, {
      x: x + 0.1, y: startY + 2.62,
      w: cardW - 0.35, h: 0.65,
      fontSize: 9.5, color: C.slate, align: "center", lineSpacingMultiple: 1.3,
      fontFace: "Calibri", margin: 0
    });

    // Color dot
    const dotColors = [C.blue, C.purple, C.teal, C.orange, C.green];
    s.addShape(pres.shapes.OVAL, {
      x: x + (cardW - 0.15) / 2 - 0.18, y: startY + 3.4,
      w: 0.36, h: 0.36,
      fill: { color: dotColors[i] }, line: { color: dotColors[i] }
    });
    s.addText(String(i + 1), {
      x: x + (cardW - 0.15) / 2 - 0.18, y: startY + 3.4,
      w: 0.36, h: 0.36,
      fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle",
      fontFace: "Calibri", margin: 0
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 3 — Scenario
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  lightBg(s);
  addHeader(s, "Patient Scenario", "Cardiac Emergency — Fadi Halaweh (DOB: 1985-03-12)", C.blue);
  addFooter(s);

  // Story box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.22, w: W - 0.8, h: 1.02,
    fill: { color: "EFF6FF" }, line: { color: "BFDBFE" }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.22, w: 0.06, h: 1.02,
    fill: { color: C.blue }, line: { color: C.blue }
  });
  s.addText([
    { text: "Fadi Halaweh", options: { bold: true, color: C.blue } },
    { text: ", 41-year-old male, presents at Al-Nour GP Clinic with chest pain radiating to the left arm (local code: ", options: { color: C.dark } },
    { text: "CP-05", options: { bold: true, color: C.amber } },
    { text: "). His GP refers him immediately to the Hospital Emergency Department. The ED orders urgent cardiac labs and imaging, then prescribes medication. Each handoff requires data exchange between systems using different standards and terminologies.", options: { color: C.dark } },
  ], {
    x: 0.6, y: 1.26, w: W - 1.1, h: 0.96,
    fontSize: 11.5, fontFace: "Calibri", lineSpacingMultiple: 1.5, valign: "middle", margin: 0
  });

  // Provider cards
  const providers = [
    { label: "1. GP Clinic",    sub: "Al-Nour Clinic\nSQLite DB", color: C.blue,   icon: "GP" },
    { label: "2. Hospital ED",  sub: "City Hospital\nSQLite DB",  color: C.purple, icon: "ED" },
    { label: "3. Laboratory",   sub: "Central Lab\nSQLite DB",    color: C.teal,   icon: "LAB" },
    { label: "4. Radiology",    sub: "Imaging Centre\nSQLite DB", color: C.orange, icon: "RAD" },
    { label: "5. Pharmacy",     sub: "City Pharmacy\nSQLite DB",  color: C.green,  icon: "RX" },
  ];

  const pW = (W - 0.8) / 5;
  providers.forEach((p, i) => {
    const x = 0.4 + i * pW;
    const y = 2.44;

    card(s, x, y, pW - 0.14, 2.5);

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: pW - 0.14, h: 0.5,
      fill: { color: p.color }, line: { color: p.color }
    });
    s.addText(p.icon, {
      x, y, w: pW - 0.14, h: 0.5,
      fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle",
      fontFace: "Calibri", charSpacing: 2, margin: 0
    });
    s.addText(p.label, {
      x: x + 0.08, y: y + 0.58, w: pW - 0.3, h: 0.42,
      fontSize: 10, bold: true, color: C.dark, align: "center",
      fontFace: "Calibri", margin: 0
    });
    s.addText(p.sub, {
      x: x + 0.08, y: y + 0.98, w: pW - 0.3, h: 0.55,
      fontSize: 8.5, color: C.slate, align: "center", lineSpacingMultiple: 1.3,
      fontFace: "Calibri", margin: 0
    });

    if (i < 4) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: x + pW - 0.18, y: y + 1.08, w: 0.12, h: 0.03,
        fill: { color: C.slateLight }, line: { color: C.slateLight }
      });
    }
  });

  // 3 types summary
  const types = [
    { label: "Structural", desc: "Different data formats converted\n(CSV → HL7, JSON → FHIR, etc.)", color: "DBEAFE", text: C.blue },
    { label: "Syntactic", desc: "Encoding & structure rules\n(HL7 v2 pipes, FHIR JSON, DICOM tags)", color: "D1FAE5", text: C.teal },
    { label: "Semantic", desc: "Terminology mapping\n(ICD-10, LOINC, SNOMED CT, RxNorm)", color: "FEF3C7", text: C.amber },
  ];
  types.forEach((t, i) => {
    card(s, 0.4 + i * 4.3, 5.1, 4.15, 1.1, t.color, t.color);
    s.addText(t.label + " Interoperability", {
      x: 0.55 + i * 4.3, y: 5.18, w: 3.85, h: 0.32,
      fontSize: 11, bold: true, color: t.text, fontFace: "Calibri", margin: 0
    });
    s.addText(t.desc, {
      x: 0.55 + i * 4.3, y: 5.5, w: 3.85, h: 0.6,
      fontSize: 9.5, color: C.dark, fontFace: "Calibri", lineSpacingMultiple: 1.35, margin: 0
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 4 — Data Exchange Timeline
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  lightBg(s);
  addHeader(s, "Data Exchange Timeline", "5 interoperability points — source, destination, and data type at each", C.teal);
  addFooter(s);

  const rows = [
    { ch: 1, from: "GP Clinic",   to: "Hospital ED", data: "Patient demographics + diagnosis", std: "HL7 v2 ADT^A01", term: "ICD-10",    color: C.blue },
    { ch: 2, from: "Hospital ED", to: "Laboratory",   data: "Lab order (Troponin, CBC, Lipid panel)", std: "HL7 v2 ORM^O01", term: "LOINC",     color: C.purple },
    { ch: 3, from: "Laboratory",  to: "Hospital ED",  data: "Lab results with flags",          std: "HL7 v2 ORU^R01", term: "SNOMED CT", color: C.teal },
    { ch: 4, from: "Hospital ED", to: "Radiology",    data: "Imaging request (chest X-ray)",   std: "DICOM Metadata", term: "SNOMED CT", color: C.orange },
    { ch: 5, from: "Hospital ED", to: "Pharmacy",     data: "Medication order (Aspirin 75mg)", std: "FHIR R4 MedicationRequest", term: "RxNorm", color: C.green },
  ];

  const rY = 1.22;
  const rH = 0.9;
  const gap = 0.08;

  rows.forEach((r, i) => {
    const y = rY + i * (rH + gap);

    card(s, 0.4, y, W - 0.8, rH);
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y, w: 0.06, h: rH, fill: { color: r.color }, line: { color: r.color }
    });

    // Channel circle
    s.addShape(pres.shapes.OVAL, {
      x: 0.6, y: y + 0.27, w: 0.36, h: 0.36,
      fill: { color: r.color }, line: { color: r.color }
    });
    s.addText(String(r.ch), {
      x: 0.6, y: y + 0.27, w: 0.36, h: 0.36,
      fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle",
      fontFace: "Calibri", margin: 0
    });

    // From → To
    s.addText(r.from, { x: 1.12, y: y + 0.12, w: 2.2, h: 0.3, fontSize: 11, bold: true, color: C.dark, fontFace: "Calibri", margin: 0 });
    s.addText("→", { x: 3.32, y: y + 0.12, w: 0.3, h: 0.3, fontSize: 13, color: r.color, align: "center", fontFace: "Calibri", margin: 0 });
    s.addText(r.to,   { x: 3.62, y: y + 0.12, w: 2.2, h: 0.3, fontSize: 11, bold: true, color: C.dark, fontFace: "Calibri", margin: 0 });

    // Data type
    s.addText(r.data, { x: 1.12, y: y + 0.52, w: 4.6, h: 0.28, fontSize: 9.5, color: C.slate, fontFace: "Calibri", margin: 0 });

    // Standard badge
    s.addShape(pres.shapes.RECTANGLE, {
      x: 6.1, y: y + 0.22, w: 3.4, h: 0.36,
      fill: { color: C.dark }, line: { color: r.color }
    });
    s.addText(r.std, { x: 6.1, y: y + 0.22, w: 3.4, h: 0.36, fontSize: 9.5, bold: true, color: r.color, align: "center", valign: "middle", fontFace: "Calibri", margin: 0 });

    // Terminology
    s.addShape(pres.shapes.RECTANGLE, {
      x: 9.7, y: y + 0.22, w: 3.0, h: 0.36,
      fill: { color: C.amberLight }, line: { color: C.amber }
    });
    s.addText(r.term, { x: 9.7, y: y + 0.22, w: 3.0, h: 0.36, fontSize: 9.5, bold: true, color: C.amber, align: "center", valign: "middle", fontFace: "Calibri", margin: 0 });
  });

  // Column headers
  s.addText("Channel  From → To", { x: 0.55, y: 1.05, w: 5.4, h: 0.18, fontSize: 8, color: C.slate, fontFace: "Calibri", bold: true, charSpacing: 1, margin: 0 });
  s.addText("Standard",           { x: 6.1,  y: 1.05, w: 3.4, h: 0.18, fontSize: 8, color: C.slate, fontFace: "Calibri", bold: true, charSpacing: 1, align: "center", margin: 0 });
  s.addText("Terminology",        { x: 9.7,  y: 1.05, w: 3.0, h: 0.18, fontSize: 8, color: C.slate, fontFace: "Calibri", bold: true, charSpacing: 1, align: "center", margin: 0 });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 5 — Datasets
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  lightBg(s);
  addHeader(s, "Simulated Datasets", "5 SQLite databases — each with different structure, content, and terminology", C.purple);
  addFooter(s);

  const dbs = [
    {
      name: "gp_clinic.db", color: C.blue,
      table: "patients",
      fields: ["id", "name", "dob", "gender", "local_diagnosis_code", "diagnosis_text", "referred_to"],
      sample: ["1", "Fadi Halaweh", "1985-03-12", "M", "CP-05", "Chest pain, left arm", "Cardiology"],
      term: "Local GP codes (CP-01…)"
    },
    {
      name: "hospital_ed.db", color: C.purple,
      table: "admissions",
      fields: ["id", "patient_name", "icd10_code", "diagnosis_text", "attending_physician", "admission_date"],
      sample: ["1", "Fadi Halaweh", "I21.9", "Acute myocardial infarction", "Dr. Khalid Mansour", "2026-06-10"],
      term: "ICD-10 (I20.0, I21.9…)"
    },
    {
      name: "laboratory.db", color: C.teal,
      table: "orders",
      fields: ["id", "patient_name", "loinc_code", "test_name", "result_value", "unit", "reference_range", "status"],
      sample: ["1", "Fadi Halaweh", "10839-9", "Troponin I", "0.08", "ng/mL", "<0.04", "FINAL"],
      term: "LOINC (10839-9, 718-7…)"
    },
    {
      name: "radiology.db", color: C.orange,
      table: "requests",
      fields: ["id", "patient_name", "modality", "snomed_procedure_code", "procedure_name", "report_text"],
      sample: ["1", "Fadi Halaweh", "CR", "399208008", "Plain chest X-ray", "Cardiomegaly noted…"],
      term: "SNOMED CT (399208008)"
    },
    {
      name: "pharmacy.db", color: C.green,
      table: "medications",
      fields: ["id", "patient_name", "rxnorm_code", "drug_name", "dose", "frequency", "prescriber"],
      sample: ["1", "Fadi Halaweh", "1191", "Aspirin", "75mg", "Once daily", "Dr. Khalid Mansour"],
      term: "RxNorm (1191, 308460…)"
    },
  ];

  const cW = (W - 0.8) / 5;
  dbs.forEach((db, i) => {
    const x = 0.4 + i * cW;
    card(s, x, 1.22, cW - 0.12, 5.65);

    // Header
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.22, w: cW - 0.12, h: 0.62,
      fill: { color: db.color }, line: { color: db.color }
    });
    s.addText(db.name, {
      x: x + 0.06, y: 1.22, w: cW - 0.24, h: 0.38,
      fontSize: 9, bold: true, color: C.white, align: "center", valign: "bottom",
      fontFace: "Calibri", margin: 0
    });
    s.addText("table: " + db.table, {
      x: x + 0.06, y: 1.58, w: cW - 0.24, h: 0.22,
      fontSize: 7.5, color: "BFDBFE", align: "center",
      fontFace: "Calibri", margin: 0
    });

    // Fields
    s.addText("FIELDS", {
      x: x + 0.1, y: 1.93, w: cW - 0.28, h: 0.2,
      fontSize: 7, bold: true, color: C.slate, charSpacing: 1,
      fontFace: "Calibri", margin: 0
    });
    db.fields.forEach((f, fi) => {
      s.addText("→ " + f, {
        x: x + 0.1, y: 2.13 + fi * 0.25, w: cW - 0.28, h: 0.24,
        fontSize: 8, color: C.dark, fontFace: "Calibri", margin: 0
      });
    });

    // Terminology
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.08, y: 5.5, w: cW - 0.28, h: 0.28,
      fill: { color: C.amberLight }, line: { color: C.amber }
    });
    s.addText(db.term, {
      x: x + 0.08, y: 5.5, w: cW - 0.28, h: 0.28,
      fontSize: 7.5, bold: true, color: C.amber, align: "center", valign: "middle",
      fontFace: "Calibri", margin: 0
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper: Channel detail slide (Slides 6–10)
// ═══════════════════════════════════════════════════════════════════════════
function channelSlide(num, title, subtitle, accentColor, srcLabel, srcData, dstLabel, dstData, structural, syntactic, semantic) {
  const s = pres.addSlide();
  lightBg(s);
  addHeader(s, `Channel ${num}: ${title}`, subtitle, accentColor);
  addFooter(s);

  // Channel badge
  s.addShape(pres.shapes.RECTANGLE, {
    x: W - 1.1, y: 0.1, w: 0.75, h: 0.35,
    fill: { color: accentColor }, line: { color: accentColor }
  });
  s.addText(`CH ${num}`, {
    x: W - 1.1, y: 0.1, w: 0.75, h: 0.35,
    fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle",
    fontFace: "Calibri", margin: 0
  });

  // Source / Destination boxes
  const boxY = 1.2;
  // Source
  card(s, 0.4, boxY, 5.5, 2.55, "EFF6FF", "BFDBFE");
  s.addText("SOURCE", {
    x: 0.55, y: boxY + 0.1, w: 1.5, h: 0.22,
    fontSize: 7, bold: true, color: C.blue, charSpacing: 2,
    fontFace: "Calibri", margin: 0
  });
  s.addText(srcLabel, {
    x: 0.55, y: boxY + 0.3, w: 5.2, h: 0.28,
    fontSize: 10, bold: true, color: C.dark, fontFace: "Calibri", margin: 0
  });
  s.addText(srcData, {
    x: 0.5, y: boxY + 0.62, w: 5.35, h: 1.82,
    fontSize: 8, color: C.dark, fontFace: "Consolas", lineSpacingMultiple: 1.5,
    valign: "top", margin: 0
  });

  // Arrow
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.1, y: boxY + 1.15, w: 0.9, h: 0.03,
    fill: { color: accentColor }, line: { color: accentColor }
  });
  s.addText("→", {
    x: 6.0, y: boxY + 0.95, w: 1.1, h: 0.42,
    fontSize: 20, bold: true, color: accentColor, align: "center",
    fontFace: "Calibri", margin: 0
  });

  // Destination
  card(s, 7.2, boxY, 5.7, 2.55, "F0FDF4", "BBF7D0");
  s.addText("DESTINATION", {
    x: 7.35, y: boxY + 0.1, w: 2.0, h: 0.22,
    fontSize: 7, bold: true, color: C.green, charSpacing: 2,
    fontFace: "Calibri", margin: 0
  });
  s.addText(dstLabel, {
    x: 7.35, y: boxY + 0.3, w: 5.4, h: 0.28,
    fontSize: 10, bold: true, color: C.dark, fontFace: "Calibri", margin: 0
  });
  s.addText(dstData, {
    x: 7.2, y: boxY + 0.62, w: 5.55, h: 1.82,
    fontSize: 7.5, color: C.dark, fontFace: "Consolas", lineSpacingMultiple: 1.45,
    valign: "top", margin: 0
  });

  // Transformation blocks
  const tY = 3.94;
  const blocks = [
    { label: "STRUCTURAL", desc: structural, bg: "DBEAFE", border: C.blue,   text: C.blue },
    { label: "SYNTACTIC",  desc: syntactic,  bg: "D1FAE5", border: C.teal,   text: C.teal },
    { label: "SEMANTIC",   desc: semantic,   bg: "FEF3C7", border: C.amber,  text: C.amber },
  ];
  const bW = (W - 0.8) / 3;
  blocks.forEach((b, i) => {
    const bX = 0.4 + i * (bW + 0.04);
    card(s, bX, tY, bW - 0.04, 2.12, b.bg, b.border);
    s.addShape(pres.shapes.RECTANGLE, { x: bX, y: tY, w: 0.05, h: 2.12, fill: { color: b.border }, line: { color: b.border } });
    s.addText(b.label, {
      x: bX + 0.14, y: tY + 0.1, w: bW - 0.3, h: 0.26,
      fontSize: 8, bold: true, color: b.text, charSpacing: 2,
      fontFace: "Calibri", margin: 0
    });
    s.addText(b.desc, {
      x: bX + 0.14, y: tY + 0.38, w: bW - 0.3, h: 1.62,
      fontSize: 9.5, color: C.dark, fontFace: "Calibri",
      lineSpacingMultiple: 1.45, valign: "top", margin: 0
    });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDES 6–10 — Channels 1–5
// ═══════════════════════════════════════════════════════════════════════════
channelSlide(1,
  "GP Clinic → Hospital ED",
  "HL7 v2 ADT^A01  |  ICD-10 terminology mapping",
  C.blue,
  "GP Clinic — Flat SQLite record",
  "id:                  000001\nname:                Fadi Halaweh\ndob:                 1985-03-12\ngender:              M\nlocal_diagnosis_code: CP-05\ndiagnosis_text:      Chest pain radiating to left arm\nreferred_to:         Cardiology",
  "Hospital ED — HL7 v2 ADT^A01 message",
  "MSH|^~\\&|GP_CLINIC|AL-NOUR|HOSPITAL_ED|CITY_HOSP|...|ADT^A01\nPID|1||000001^^^GP_CLINIC||Fadi^Halaweh||19850312|M\nPV1|1|E|ED^01^A|||||||Cardiology\nDG1|1||I21.9^Acute myocardial infarction^ICD10|...|A",
  "Flat CSV-style SQLite row → HL7 v2 ADT^A01 message with MSH, PID, PV1, DG1 segments",
  "Pipe-delimited HL7 v2.5 encoding; ^ component separator; \\r segment terminator",
  "Local GP code 'CP-05' → ICD-10 'I21.9' (Acute myocardial infarction, unspecified)"
);

channelSlide(2,
  "Hospital ED → Laboratory",
  "HL7 v2 ORM^O01  |  LOINC terminology mapping",
  C.purple,
  "Hospital ED — Internal admission record (JSON)",
  "patient_name:        Fadi Halaweh\nicd10_code:          I21.9\ndiagnosis:           Acute myocardial infarction\nattending_physician: Dr. Khalid Mansour\ntests_ordered:       Troponin I, CBC, Lipid Panel, BMP",
  "Laboratory — HL7 v2 ORM^O01 order message",
  "MSH|^~\\&|HOSPITAL_ED|CITY_HOSP|LABORATORY|LAB_SYS|...|ORM^O01\nPID|1||000001|||Fadi^Halaweh||19850312|M\nPV1|1|E|ED^01^A|||Dr. Khalid Mansour\nOBR|1||0001A|10839-9^Troponin I^LN|||...|||STAT\nOBR|2||0001B|58410-2^CBC panel^LN|||...|||STAT",
  "ED admission dict with ordered tests → HL7 v2 ORM^O01; each test becomes an OBR segment",
  "HL7 v2.5 pipe-delimited; OBR-4 holds LOINC code^name^LN; priority STAT in OBR-27",
  "ED test name 'Troponin I' → LOINC '10839-9'; 'CBC' → LOINC '58410-2'"
);

channelSlide(3,
  "Laboratory → Hospital ED",
  "HL7 v2 ORU^R01  |  SNOMED CT terminology mapping",
  C.teal,
  "Laboratory — SQLite result record",
  "patient_name:    Fadi Halaweh\nloinc_code:      10839-9\ntest_name:       Troponin I\nresult_value:    0.08  ng/mL\nreference_range: <0.04\nstatus:          FINAL\nresult_date:     2026-06-10",
  "Hospital ED — HL7 v2 ORU^R01 result message",
  "MSH|^~\\&|LABORATORY|LAB_SYS|HOSPITAL_ED|...|ORU^R01\nPID|1||000001^^^LAB||Fadi^Halaweh\nOBR|1|0001|0001A|10839-9^Troponin I^LN|||...\nOBX|1|NM|10839-9^Troponin I^LN||0.08|ng/mL|<0.04|H|||FINAL\nOBX|2|CWE|414916001^Elevated troponin^SCT",
  "Lab SQLite result → HL7 v2 ORU^R01; numeric result in OBX-5; SNOMED finding in second OBX",
  "HL7 v2.5 OBX segments: OBX-6 units, OBX-7 reference range, OBX-8 abnormal flag (H/L/N)",
  "LOINC '10839-9' (Troponin I) + abnormal value → SNOMED CT '414916001' (Elevated troponin finding)"
);

channelSlide(4,
  "Hospital ED → Radiology",
  "DICOM Metadata  |  SNOMED CT procedure coding",
  C.orange,
  "Hospital ED — Admission record (JSON)",
  "patient_name:        Fadi Halaweh\ndob:                 1985-03-12\nicd10_code:          I21.9\ndiagnosis:           Acute myocardial infarction\nattending_physician: Dr. Khalid Mansour",
  "Radiology — DICOM attribute dataset (Key=Value)",
  "(0008,0060) Modality          = CR\n(0008,1030) StudyDescription   = Plain chest X-ray\n(0010,0010) PatientName        = Fadi^Halaweh\n(0010,0020) PatientID          = 000001\n(0010,0030) PatientBirthDate   = 19850312\n(0008,0100) CodeValue (SNOMED) = 399208008\n(0008,0104) CodeMeaning        = Plain chest X-ray",
  "JSON admission → DICOM-style attribute dataset; (gggg,eeee) tag notation per DICOM PS 3.3",
  "DICOM attribute tag format with group/element numbers; Modality, UIDs, and PatientName set per DICOM standard",
  "ICD-10 'I21.9' (Acute MI) → SNOMED CT procedure '399208008' (Plain chest X-ray); modality = CR"
);

channelSlide(5,
  "Hospital ED → Pharmacy",
  "FHIR R4 MedicationRequest  |  RxNorm drug coding",
  C.green,
  "Hospital ED — Admission record (JSON)",
  "patient_name:        Fadi Halaweh\nicd10_code:          I21.9\ndiagnosis:           Acute myocardial infarction\nattending_physician: Dr. Khalid Mansour\nadmission_date:      2026-06-10",
  "Pharmacy — FHIR R4 MedicationRequest (JSON)",
  '{\n  "resourceType": "MedicationRequest",\n  "status": "active",\n  "medicationCodeableConcept": {\n    "coding": [{ "system": "...rxnorm",\n      "code": "308460",\n      "display": "Clopidogrel" }]\n  },\n  "dosageInstruction": [{\n    "text": "1 tablet once daily",\n    "route": { "coding": [{"code":"26643006"}] }\n  }]\n}',
  "ED admission dict → FHIR R4 MedicationRequest JSON resource with medicationCodeableConcept, subject, requester, reasonCode, dosageInstruction",
  "FHIR RESTful JSON; resource type, status, intent, coding per HL7 FHIR R4 spec; route coded in SNOMED CT (26643006 = oral)",
  "ICD-10 'I21.9' (Acute MI) → RxNorm '308460' (Clopidogrel 75mg once daily); oral route = SNOMED 26643006"
);

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 11 — Interoperability Framework
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  lightBg(s);
  addHeader(s, "Interoperability Framework", "Complete data exchange architecture across all providers", C.navy);
  addFooter(s);

  // Central patient box
  card(s, W/2 - 1.1, 2.8, 2.2, 0.8, "EFF6FF", C.blue);
  s.addShape(pres.shapes.RECTANGLE, { x: W/2-1.1, y: 2.8, w: 0.06, h: 0.8, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText("PATIENT\nFadi Halaweh", {
    x: W/2 - 1.0, y: 2.82, w: 2.05, h: 0.76,
    fontSize: 9, bold: true, color: C.blue, align: "center", valign: "middle",
    lineSpacingMultiple: 1.3, fontFace: "Calibri", margin: 0
  });

  // Provider boxes and connections
  const nodes = [
    { label: "GP Clinic",   x: 0.5,  y: 2.9,  color: C.blue,   ch: "CH 1", arrow: "right" },
    { label: "Hospital ED", x: 4.6,  y: 1.3,  color: C.purple, ch: "",     arrow: "" },
    { label: "Laboratory",  x: 9.2,  y: 1.3,  color: C.teal,   ch: "CH 2/3", arrow: "" },
    { label: "Radiology",   x: 9.2,  y: 4.5,  color: C.orange, ch: "CH 4", arrow: "" },
    { label: "Pharmacy",    x: 4.6,  y: 4.5,  color: C.green,  ch: "CH 5", arrow: "" },
  ];

  nodes.forEach((n) => {
    card(s, n.x, n.y, 2.5, 0.75, n.color === C.purple ? "EDE9FE" : n.color === C.teal ? "CCFBF1" : n.color === C.orange ? "FFF7ED" : n.color === C.green ? "ECFDF5" : "EFF6FF", n.color);
    s.addShape(pres.shapes.RECTANGLE, { x: n.x, y: n.y, w: 0.06, h: 0.75, fill: { color: n.color }, line: { color: n.color } });
    s.addText(n.label, { x: n.x + 0.12, y: n.y, w: 2.35, h: 0.75, fontSize: 11, bold: true, color: C.dark, valign: "middle", fontFace: "Calibri", margin: 0 });
  });

  // Hospital ED is central — draw arrows (simplified lines)
  const edX = 4.6, edY = 1.3;
  // GP→ED
  s.addShape(pres.shapes.RECTANGLE, { x: 3.1, y: 3.18, w: 1.5, h: 0.04, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText("CH1 HL7 ADT", { x: 3.0, y: 2.96, w: 1.7, h: 0.22, fontSize: 7.5, color: C.blue, align: "center", fontFace: "Calibri", margin: 0 });
  // ED→Lab
  s.addShape(pres.shapes.RECTANGLE, { x: 7.1, y: 1.62, w: 2.1, h: 0.04, fill: { color: C.purple }, line: { color: C.purple } });
  s.addText("CH2 HL7 ORM", { x: 7.1, y: 1.42, w: 2.1, h: 0.22, fontSize: 7.5, color: C.purple, align: "center", fontFace: "Calibri", margin: 0 });
  // Lab→ED
  s.addShape(pres.shapes.RECTANGLE, { x: 7.1, y: 1.72, w: 2.1, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("CH3 HL7 ORU", { x: 7.1, y: 1.76, w: 2.1, h: 0.22, fontSize: 7.5, color: C.teal, align: "center", fontFace: "Calibri", margin: 0 });
  // ED→Radiology
  s.addShape(pres.shapes.RECTANGLE, { x: 7.1, y: 4.82, w: 2.1, h: 0.04, fill: { color: C.orange }, line: { color: C.orange } });
  s.addText("CH4 DICOM", { x: 7.1, y: 4.62, w: 2.1, h: 0.22, fontSize: 7.5, color: C.orange, align: "center", fontFace: "Calibri", margin: 0 });
  // ED→Pharmacy
  s.addShape(pres.shapes.RECTANGLE, { x: 5.3, y: 4.82, w: 1.6, h: 0.04, fill: { color: C.green }, line: { color: C.green } });
  s.addText("CH5 FHIR R4", { x: 5.3, y: 4.62, w: 1.6, h: 0.22, fontSize: 7.5, color: C.green, align: "center", fontFace: "Calibri", margin: 0 });

  // Stats row
  const stats = [
    { v: "5", l: "Healthcare\nProviders" },
    { v: "5", l: "Integration\nChannels" },
    { v: "6", l: "Simulated\nPatients" },
    { v: "4", l: "Standards\nUsed" },
    { v: "5", l: "SQLite\nDatabases" },
  ];
  stats.forEach((st, i) => {
    card(s, 0.4 + i * 2.5, 6.1, 2.35, 0.9, C.dark, C.navy);
    s.addText(st.v, { x: 0.4 + i * 2.5, y: 6.1, w: 0.7, h: 0.9, fontSize: 28, bold: true, color: C.blueLight, align: "center", valign: "middle", fontFace: "Calibri", margin: 0 });
    s.addText(st.l, { x: 1.1 + i * 2.5, y: 6.2, w: 1.55, h: 0.7, fontSize: 9, color: "94A3B8", valign: "middle", lineSpacingMultiple: 1.3, fontFace: "Calibri", margin: 0 });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 12 — Demo
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  darkBg(s);

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 0.07, fill: { color: C.teal }, line: { color: C.teal }
  });

  s.addText("LIVE DEMO", {
    x: 0.6, y: 1.2, w: W - 1.2, h: 0.7,
    fontSize: 48, bold: true, color: C.white, fontFace: "Calibri", charSpacing: 8, margin: 0
  });
  s.addText("Health Interoperability Demo Application", {
    x: 0.6, y: 1.9, w: W - 1.2, h: 0.45,
    fontSize: 18, color: "94A3B8", fontFace: "Calibri", margin: 0
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 2.5, w: 3.5, h: 0.04, fill: { color: C.teal }, line: { color: C.teal }
  });

  const steps = [
    { n: "1", t: "Open the dashboard", d: "localhost:5000 — all 6 patients listed" },
    { n: "2", t: "Select Fadi Halaweh", d: "View his GP record (local code CP-05)" },
    { n: "3", t: "Channel 1: Send to Hospital ED", d: "Watch CP-05 → ICD-10 I21.9 in HL7 ADT^A01" },
    { n: "4", t: "Channel 2: Order Lab Tests", d: "Troponin I → LOINC 10839-9 in HL7 ORM^O01" },
    { n: "5", t: "Channel 3: Receive Lab Results", d: "Result 0.08 ng/mL → SNOMED 414916001 in ORU^R01" },
    { n: "6", t: "Channels 4 & 5", d: "DICOM imaging request + FHIR R4 MedicationRequest" },
  ];

  steps.forEach((st, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.6 + col * 6.1;
    const y = 2.75 + row * 1.2;

    card(s, x, y, 5.8, 1.05, "1E293B", "334155");
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.15, y: y + 0.34, w: 0.36, h: 0.36,
      fill: { color: C.teal }, line: { color: C.teal }
    });
    s.addText(st.n, { x: x + 0.15, y: y + 0.34, w: 0.36, h: 0.36, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri", margin: 0 });
    s.addText(st.t, { x: x + 0.62, y: y + 0.1, w: 5.0, h: 0.3, fontSize: 11, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
    s.addText(st.d, { x: x + 0.62, y: y + 0.42, w: 5.0, h: 0.52, fontSize: 9.5, color: "94A3B8", fontFace: "Calibri", margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: H - 0.35, w: W, h: 0.35, fill: { color: "1E293B" }, line: { color: "1E293B" }
  });
  s.addText("COMP3342 — Health Systems Interoperability & Integration", {
    x: 0.4, y: H - 0.32, w: W - 0.8, h: 0.28,
    fontSize: 9, color: "475569", fontFace: "Calibri", margin: 0
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 13 — Conclusion
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  darkBg(s);

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 0.07, fill: { color: C.blue }, line: { color: C.blue }
  });

  s.addText("Conclusion", {
    x: 0.6, y: 0.55, w: W - 1.2, h: 0.65,
    fontSize: 36, bold: true, color: C.white, fontFace: "Calibri", charSpacing: -0.5, margin: 0
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.3, w: 3.0, h: 0.04, fill: { color: C.blueLight }, line: { color: C.blueLight }
  });

  const points = [
    { icon: "✔", text: "Developed a realistic multi-provider healthcare scenario (Cardiac Emergency) with 6 simulated patients across 5 SQLite databases" },
    { icon: "✔", text: "Demonstrated structural interoperability: flat records → HL7 v2, FHIR R4, and DICOM formats" },
    { icon: "✔", text: "Demonstrated syntactic interoperability: correct encoding rules for HL7 v2 pipe delimiters, FHIR JSON, and DICOM tag notation" },
    { icon: "✔", text: "Demonstrated semantic interoperability: ICD-10, LOINC, SNOMED CT, and RxNorm terminology mappings across all 5 channels" },
    { icon: "✔", text: "Built a live Python/Flask demo application showing before-and-after transformation at each data exchange point" },
  ];

  points.forEach((p, i) => {
    card(s, 0.6, 1.52 + i * 0.88, W - 1.2, 0.78, "1E293B", "334155");
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.52 + i * 0.88, w: 0.05, h: 0.78, fill: { color: C.blueLight }, line: { color: C.blueLight } });
    s.addText(p.text, {
      x: 0.82, y: 1.56 + i * 0.88, w: W - 1.55, h: 0.7,
      fontSize: 11, color: "CBD5E1", fontFace: "Calibri", lineSpacingMultiple: 1.4, valign: "middle", margin: 0
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: H - 0.35, w: W, h: 0.35, fill: { color: "1E293B" }, line: { color: "1E293B" }
  });
  s.addText("COMP3342 — Health Systems Interoperability & Integration  •  Group [GROUP NUMBER]  •  June 17, 2026", {
    x: 0.4, y: H - 0.32, w: W - 0.8, h: 0.28,
    fontSize: 9, color: "475569", fontFace: "Calibri", margin: 0
  });
}

// ─── Save ───────────────────────────────────────────────────────────────────
const outPath = path.join(__dirname, "..", "COMP3342_Presentation.pptx");
pres.writeFile({ fileName: outPath }).then(() => {
  console.log("✓ Saved:", outPath);
}).catch(err => {
  console.error("Error:", err);
  process.exit(1);
});
