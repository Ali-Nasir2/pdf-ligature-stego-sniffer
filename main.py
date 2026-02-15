import streamlit as st
import tempfile
from core.analyzer import analyze_pdf
import jinja2
import base64
import unicodedata
import matplotlib.pyplot as plt
import io
import fitz 

# -------------------------------------------------------
# ---------- Streamlit Page & Global Styling ------------
# -------------------------------------------------------

st.set_page_config(page_title="PDF Ligature Stego Sniffer", layout="wide")

st.markdown("""
    <style>
        body { background-color: #f3f6fa; }

        .main-title {
            text-align: center; 
            font-size: 3em; 
            color: #005f99; 
            font-weight: 700; 
            padding-bottom: 0.3em;
        }

        .sub-header {
            color: #005f99;
            font-size: 1.8em;
            font-weight: 600;
            margin-top: 1.5em;
            padding-bottom: 5px;
            border-bottom: 2px solid #cfe4f2;
        }

        .info-card {
            background: #ffffff;
            padding: 18px 22px;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
            border-left: 5px solid #cfe4f2;
            margin-bottom: 1.2em;
        }

        .metric-value {
            font-size: 1.4em; 
            font-weight: 700; 
            color: #005f99;
        }

        .metric-label {
            font-size: 0.95em;
            color: #444;
        }

        .download-btn {
            background-color: #005f99 !important;
            color: white !important;
            padding: 0.7em 1.2em !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🔍 PDF Ligature Stego Sniffer</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Upload a PDF file to analyze", type=["pdf"])

# -------------------------------------------------------
# ----------------- Helper Functions --------------------
# -------------------------------------------------------

def plot_suspicious_heatmap(suspicious):
    xs, ys, labels = [], [], []
    for s in suspicious:
        x, y = s.get("position", (None, None))
        if x is not None and y is not None:
            xs.append(x)
            ys.append(y)
            char = s.get("character", "")
            cp = s.get("codepoint", "")
            labels.append(f"{char} ({cp})" if char.strip() else cp)

    if not xs:
        return None

    plt.figure(figsize=(8, 6))
    plt.hexbin(xs, ys, gridsize=40, cmap='Reds', mincnt=1)
    plt.scatter(xs, ys, s=20, alpha=0.6)
    plt.gca().invert_yaxis()
    plt.xlabel("X position")
    plt.ylabel("Y position")
    plt.title("Suspicious Character Heatmap")
    plt.colorbar(label="Density")

    for i in range(len(xs)):
        plt.annotate(labels[i], (xs[i], ys[i]), fontsize=7, ha='center')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf

def get_heatmap_base64(suspicious):
    buf = plot_suspicious_heatmap(suspicious)
    if buf:
        return base64.b64encode(buf.getvalue()).decode()
    return None

def flag_suspicious_pdf_objects(pdf_path):
    """
    Same logic as run_analyzer: scan raw PDF objects and flag suspicious ones.
    """
    suspicious_objects = []
    doc = fitz.open(pdf_path)
    for obj_num in range(1, doc.xref_length()):
        try:
            obj_str = doc.xref_object(obj_num)
            # Flag objects containing non-ASCII bytes or suspicious keywords
            if any(b > 127 for b in obj_str.encode(errors='ignore')) or b'/JBIG2Decode' in obj_str.encode():
                suspicious_objects.append({
                    "object_number": obj_num,
                    "preview": obj_str[:80]
                })
        except Exception:
            continue
    doc.close()
    return suspicious_objects

# -------------------------------------------------------
# ------------------ HTML Report Maker ------------------
# -------------------------------------------------------

def generate_html_report(result, heatmap_b64=None, suspicious_objects=None):
    summary = result["summary"]
    risk = result.get("risk_score", {})
    suspicious = result.get("suspicious", [])
    font_characters = result.get("font_characters", {})


    score_breakdown = [
        {"name": k.replace("_", " ").title(), "score": v.get("score", 0)}
        for k, v in risk.get("breakdown", {}).items()
    ]

    # Filters
    def unicodename(c): return unicodedata.name(c, "UNKNOWN")
    def ord_filter(c): return ord(c)
    def format_codepoint(v): return f"{v:04X}"

    env = jinja2.Environment(loader=jinja2.BaseLoader())
    env.filters.update({
        'unicodename': unicodename,
        'ord': ord_filter,
        'format_codepoint': format_codepoint
    })

    # ---------------- FINAL PROFESSIONAL TEMPLATE ----------------
    template_str = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>PDF Ligature Stego Sniffer – Report</title>

    <style>
        :root {
            --primary: #005f99;
            --primary-light: #e8f4fb;
            --danger: #d9534f;
            --success: #5cb85c;
            --warning: #e0a800;
            --bg: #f3f6fa;
        }

        body {
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
            background: var(--bg);
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 1000px;
            margin: 2em auto;
            background: #fff;
            padding: 2.5em 3em;
            border-radius: 14px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        }

        h1 {
            text-align: center;
            color: var(--primary);
            margin-bottom: 1em;
        }

        h2 {
            color: var(--primary);
            border-left: 5px solid var(--primary);
            padding-left: 10px;
            margin-top: 2em;
        }

        .summary-banner {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 1em;
            background: var(--primary-light);
            padding: 1.4em 1.8em;
            border-radius: 10px;
            margin-bottom: 2em;
        }

        .stat {
            font-size: 1.1em;
            font-weight: 600;
            color: var(--primary);
        }

        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            color: white;
            font-weight: bold;
        }

        .badge.high { background: #c82333; }
        .badge.medium { background: #e0a800; }
        .badge.low { background: #2d8f4e; }

        .card {
            background: #fafafa;
            border-radius: 12px;
            padding: 1.7em 2em;
            margin-top: 1.8em;
            border-left: 5px solid var(--primary-light);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1em;
        }
        th {
            background: var(--primary-light);
            padding: 8px;
            color: var(--primary);
        }
        td {
            background: #fff;
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        tr:nth-child(even) td { background: #f8fbff; }

        .heatmap-img {
            width: 100%;
            border-radius: 10px;
            margin-top: 1em;
        }

        .invisible-char {
            background: #fff3cd;
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: bold;
            color: var(--danger);
        }

        .suspicious {
            color: var(--danger);
            font-weight: 600;
        }
    </style>
</head>

<body>
<div class="container">

    <h1>🔍 PDF Ligature Stego Sniffer – Report</h1>

    <!-- Summary Block -->
    <div class="summary-banner">
        <div class="stat">📝 <b>Total Characters:</b> {{total_chars}}</div>
        <div class="stat">🔤 <b>Fonts Used:</b> {{fonts_used}}</div>
        <div class="stat">🚩 <b>Suspicious Characters:</b> {{suspicious_count}}</div>
        <div class="stat">⚠️ <b>Risk Level:</b>
            <span class="badge {% if risk_level == 'HIGH' %}high{% elif risk_level == 'MEDIUM' %}medium{% else %}low{% endif %}">
                {{risk_level}}
            </span>
        </div>
    </div>

    <!-- General Info -->
    <div class="card">
        <h2>General Information</h2>
        <ul>
            <li><b>Mixed Scripts Detected:</b> {{mixed_scripts_hint}}</li>
            <li><b>Zero-width Characters:</b> {{zero_width_count}}</li>
            <li><b>RTL Marks:</b> {{rtl_marks_count}}</li>
        </ul>
    </div>

    <!-- Risk Assessment -->
    <div class="card">
        <h2>Risk Assessment</h2>
        <p><b>Total Score:</b> {{total_score}} / 100</p>
        <ul>
            {% for factor in score_breakdown %}
            <li><b>{{factor.name}}:</b> {{factor.score}} points</li>
            {% endfor %}
        </ul>
    </div>

    <!-- Byte-Level Object Forensics -->
    <div class="card">
        <h2>Byte-Level Object Forensics</h2>
        {% if suspicious_objects %}
            <ul>
            {% for obj in suspicious_objects %}
                <li>
                    <b>Object #{{obj.object_number}}</b>
                    <pre>{{obj.preview}}</pre>
                </li>
            {% endfor %}
            </ul>
        {% else %}
            <p style="color:var(--success);"><b>No suspicious PDF objects detected.</b></p>
        {% endif %}
    </div>

    <!-- Heatmap -->
    <div class="card">
        <h2>Suspicious Character Heatmap</h2>
        {% if heatmap_b64 %}
            <img class="heatmap-img" src="data:image/png;base64,{{heatmap_b64}}">
        {% else %}
            <p>No suspicious characters found.</p>
        {% endif %}
    </div>

    <!-- Font Character Table -->
    <div class="card">
        <h2>Font–Character Usage</h2>
        {% if font_characters %}
            {% for font, chars in font_characters.items() %}
            <h3>{{font}}</h3>
            <table>
                <tr><th>Character</th><th>Count</th></tr>
                {% for char, count in chars.items() %}
                <tr>
                    <td>
                        {% set cp = char|ord|format_codepoint %}
                        {% set uname = char|unicodename %}
                        {% if uname.startswith("ARABIC") or uname.startswith("LATIN") or uname.startswith("DIGIT") %}
                            {{char}} [U+{{cp}} {{uname}}]
                        {% else %}
                            <span class="invisible-char">U+{{cp}} {{uname}}</span>
                        {% endif %}
                    </td>
                    <td>{{count}}</td>
                </tr>
                {% endfor %}
            </table>
            <p><b>Unique Characters:</b> {{chars|length}}</p>
            {% endfor %}
        {% else %}
            <p>No font data available.</p>
        {% endif %}
    </div>

    <!-- Suspicious Characters -->
    <div class="card">
        <h2>Suspicious Characters</h2>
        {% if suspicious %}
            <ul>
                {% for s in suspicious %}
                <li class="suspicious">Page {{s.page}}:
                    <b>{{s.codepoint}}</b> ({{s.name}}) — Font: {{s.fontname}}, Pos: {{s.position}}
                </li>
                {% endfor %}
            </ul>
        {% else %}
            <p style="color:var(--success);"><b>No suspicious characters detected.</b></p>
        {% endif %}
    </div>

       
</div>
</body>
</html>
"""

    template = env.from_string(template_str)
    return template.render(
        total_chars=summary["total_chars"],
        fonts_used=", ".join([f[0] for f in summary.get("fonts_used_top", [])]),
        mixed_scripts_hint=summary["mixed_scripts_hint"],
        zero_width_count=summary["zero_width_count"],
        rtl_marks_count=summary["rtl_marks_count"],
        suspicious_count=summary["suspicious_count"],
        total_score=risk.get("total_score", 0),
        risk_level=risk.get("risk_level", "Unknown"),
        score_breakdown=score_breakdown,
        suspicious=suspicious,
        font_characters=font_characters,
        heatmap_b64=heatmap_b64,
        suspicious_objects=suspicious_objects or [],

    )

# -------------------------------------------------------
# --------------------- Main Logic ----------------------
# -------------------------------------------------------

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_file.read())
        pdf_path = tmp_pdf.name

    st.success("✅ PDF uploaded successfully!")

    result = analyze_pdf(pdf_path)
    summary = result["summary"]
    risk = result.get("risk_score", {})

    # ALSO compute byte-level objects for this PDF
    suspicious_objects = flag_suspicious_pdf_objects(pdf_path)

    # Stat Cards
    st.markdown("<div class='sub-header'>📊 Quick PDF Summary</div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
        <div class='info-card'>
            <div class='metric-value'>{summary['total_chars']}</div>
            <div class='metric-label'>Total Characters</div>
        </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
        <div class='info-card'>
            <div class='metric-value'>{", ".join([f[0] for f in summary.get("fonts_used_top", [])])}</div>
            <div class='metric-label'>Fonts Used</div>
        </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
        <div class='info-card'>
            <div class='metric-value'>{summary['suspicious_count']}</div>
            <div class='metric-label'>Suspicious Characters</div>
        </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
        <div class='info-card'>
            <div class='metric-value' style='color:{ "#d9534f" if risk.get("risk_level") in ["HIGH", "MEDIUM"] else "#5cb85c" }'>
                {risk.get("risk_level", "Unknown")}
            </div>
            <div class='metric-label'>Risk Level</div>
        </div>
    """, unsafe_allow_html=True)

    # Generate Report
    st.markdown("<div class='sub-header'>📥 Generate Full HTML Report</div>", unsafe_allow_html=True)

    heatmap_b64 = get_heatmap_base64(result.get("suspicious", []))
    html_report = generate_html_report(result, heatmap_b64, suspicious_objects)

    if st.button("Download HTML Report"):
        b64 = base64.b64encode(html_report.encode()).decode()
        st.markdown(
            f'<a class="download-btn" href="data:text/html;base64,{b64}" download="pdf_stego_report.html">Download Report</a>',
            unsafe_allow_html=True
        )

else:
    st.info("👆 Please upload a PDF file to begin analysis.")
