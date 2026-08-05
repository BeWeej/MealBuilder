# app.py
import streamlit as st
import sqlite3
from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="Voedingsplanner", layout="wide")

def haal_voedingsmiddelen():
    con = sqlite3.connect("voeding.db")
    con.row_factory = sqlite3.Row
    rijen = con.execute(
        "SELECT naam, groep, gewicht, eiwit, kh, vet FROM voedingsmiddelen ORDER BY groep, naam"
    ).fetchall()
    con.close()
    return [dict(r) for r in rijen]

voeding = {v["naam"]: v for v in haal_voedingsmiddelen()}

VAKJES = ["Ontbijt", "Lunch", "Avondeten", "Tussendoortje 1", "Tussendoortje 2"]

if "plan" not in st.session_state:
    st.session_state.plan = {v: [] for v in VAKJES}
if "selectie" not in st.session_state:
    st.session_state.selectie = None

st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    text-align: left;
    border: 1px solid #444;
    border-radius: 6px;
    background: #262730;
    color: #fafafa;
    padding: 8px 12px;
    margin-bottom: 4px;
}
div.stButton > button:hover { border-color: #888; background: #33343f; }
div.stButton > button p { color: #fafafa; }
</style>
""", unsafe_allow_html=True)

st.title("Voedingsplanner")

# Hulpfunctie: geef alle waarden van een blokje bij het gekozen gewicht
def waarden(b):
    v = voeding[b["naam"]]
    g = b["gewicht"]
    kcal = g / v["gewicht"] * 100        # gram -> kcal
    factor = g / 100                      # macro's staan per 100 g
    return {
        "kcal": kcal,
        "eiwit": v["eiwit"] * factor,
        "kh": v["kh"] * factor,
        "vet": v["vet"] * factor,
    }

links, rechts = st.columns([1, 2])

#
#print report in pdf 
def maak_pdf(plan):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20*mm, bottomMargin=20*mm,
        leftMargin=18*mm, rightMargin=18*mm,
    )
    styles = getSampleStyleSheet()
    titel_stijl = ParagraphStyle(
        "Titel", parent=styles["Title"], fontSize=20, spaceAfter=4,
    )
    vak_stijl = ParagraphStyle(
        "Vak", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#333333"), spaceBefore=10, spaceAfter=4,
    )
    elems = []

    elems.append(Paragraph("Voedingsplan", titel_stijl))
    elems.append(Paragraph(date.today().strftime("%d-%m-%Y"), styles["Normal"]))
    elems.append(Spacer(1, 8*mm))

    dag = {"kcal": 0, "eiwit": 0, "kh": 0, "vet": 0}

    for vak in VAKJES:
        blokjes = plan[vak]
        elems.append(Paragraph(vak, vak_stijl))

        if not blokjes:
            elems.append(Paragraph("<i>leeg</i>", styles["Normal"]))
            continue

        data = [["Item", "Gewicht", "kcal", "Eiwit", "KH", "Vet"]]
        subtot = {"kcal": 0, "eiwit": 0, "kh": 0, "vet": 0}
        for b in blokjes:
            w = waarden(b)
            for k in subtot:
                subtot[k] += w[k]
                dag[k] += w[k]
            data.append([
                b["naam"],
                f"{b['gewicht']:.0f} g",
                f"{w['kcal']:.0f}",
                f"{w['eiwit']:.0f} g",
                f"{w['kh']:.0f} g",
                f"{w['vet']:.0f} g",
            ])
        data.append([
            "Totaal", "",
            f"{subtot['kcal']:.0f}",
            f"{subtot['eiwit']:.0f} g",
            f"{subtot['kh']:.0f} g",
            f"{subtot['vet']:.0f} g",
        ])

        tabel = Table(data, colWidths=[70*mm, 22*mm, 18*mm, 20*mm, 18*mm, 18*mm])
        tabel.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#262730")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eeeeee")),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elems.append(tabel)

    # Dagtotaal
    elems.append(Spacer(1, 10*mm))
    dagdata = [
        ["Dagtotaal", "kcal", "Eiwit", "KH", "Vet"],
        ["", f"{dag['kcal']:.0f}", f"{dag['eiwit']:.0f} g",
         f"{dag['kh']:.0f} g", f"{dag['vet']:.0f} g"],
    ]
    dagtabel = Table(dagdata, colWidths=[70*mm, 25*mm, 25*mm, 22*mm, 22*mm])
    dagtabel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0e1117")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
    ]))
    elems.append(dagtabel)

    doc.build(elems)
    buffer.seek(0)
    return buffer

# --- Linkerkolom ---
with links:
    st.subheader("Voedingsmiddelen per 100 kcal")

    # Filter op groep
    groepen = ["Alle"] + sorted({v["groep"] for v in voeding.values()})
    gekozen_groep = st.selectbox("Groep", groepen)

    if st.session_state.selectie:
        v = voeding[st.session_state.selectie]
        basis = v["gewicht"]
        st.caption(f"**{st.session_state.selectie}** — {basis:.0f} g = 100 kcal")

        opties = {
            f"{basis*0.5:.0f} g": basis * 0.5,
            f"{basis:.0f} g": basis,
            f"{basis*2:.0f} g": basis * 2,
        }
        keuze_label = st.radio("Kies portie", list(opties.keys()), horizontal=True)
        gekozen_gewicht = opties[keuze_label]

        eigen = st.number_input("of eigen gewicht (g)", min_value=0.0, value=0.0, step=5.0)
        if eigen > 0:
            gekozen_gewicht = eigen

        st.session_state.gekozen_gewicht = gekozen_gewicht

    with st.container(height=380):
        for naam, v in voeding.items():
            if gekozen_groep != "Alle" and v["groep"] != gekozen_groep:
                continue
            actief = st.session_state.selectie == naam
            label = f"{naam}  —  {v['gewicht']:.0f} g"
            if st.button(label, key=f"item_{naam}", use_container_width=True,
                         type="primary" if actief else "secondary"):
                st.session_state.selectie = naam
                st.rerun()
# --- Rechterkolom ---
with rechts:
    st.subheader("Maaltijden")
    for vak in VAKJES:
        blokjes = st.session_state.plan[vak]
        tot = {"kcal": 0, "eiwit": 0, "kh": 0, "vet": 0}
        for b in blokjes:
            w = waarden(b)
            for k in tot:
                tot[k] += w[k]

        with st.container(border=True):
            titel = (f"**{vak}**  —  {tot['kcal']:.0f} kcal  ·  "
                     f"Proteïnen {tot['eiwit']:.0f}g  ·  Koolhydraten {tot['kh']:.0f}g  ·  Vet {tot['vet']:.0f}g")
            if st.button(titel, key=f"vak_{vak}", use_container_width=True):
                if st.session_state.selectie:
                    st.session_state.plan[vak].append({
                        "naam": st.session_state.selectie,
                        "gewicht": st.session_state.gekozen_gewicht,
                    })
                    st.rerun()

            if not blokjes:
                st.caption("leeg — selecteer een item, kies portie, klik hierboven")
            for idx, b in enumerate(blokjes):
                w = waarden(b)
                c1, c2 = st.columns([8, 1])
                c1.write(
                    f"{b['naam']}  ·  {b['gewicht']:.0f} g  ·  {w['kcal']:.0f} kcal  ·  "
                    f"E {w['eiwit']:.0f}g · KH {w['kh']:.0f}g · V {w['vet']:.0f}g"
                )
                if c2.button("✕", key=f"del_{vak}_{idx}"):
                    st.session_state.plan[vak].pop(idx)
                    st.rerun()

# --- Dagtotaal ---
alle = [b for lst in st.session_state.plan.values() for b in lst]
dag = {"kcal": 0, "eiwit": 0, "kh": 0, "vet": 0}
for b in alle:
    w = waarden(b)
    for k in dag:
        dag[k] += w[k]

st.divider()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Dagtotaal kcal", f"{dag['kcal']:.0f}")
m2.metric("Eiwit", f"{dag['eiwit']:.0f} g")
m3.metric("Koolhydraten", f"{dag['kh']:.0f} g")
m4.metric("Vet", f"{dag['vet']:.0f} g")

#print report button 
st.divider()
st.download_button(
    "📄 Download plan als PDF",
    data=maak_pdf(st.session_state.plan),
    file_name=f"voedingsplan_{date.today().isoformat()}.pdf",
    mime="application/pdf",
)




