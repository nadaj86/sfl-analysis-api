from flask import Flask, request, jsonify, send_file
import spacy
import pandas as pd
from fpdf import FPDF

app = Flask(__name__)

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def analyze_text_sfl(text):
    """Analyzes text for SFL features: transitivity, mood, modality, etc."""
    doc = nlp(text)
    analysis = []
    counts = {"Actors": 0, "Processes": 0, "Circumstances": 0, "Modals": 0, "Nominalizations": 0}

    for token in doc:
        tag = ""
        if token.dep_ in ["nsubj", "nsubjpass"]:
            tag = "Actor"
            counts["Actors"] += 1
        elif token.pos_ in ["VERB"]:
            tag = "Process"
            counts["Processes"] += 1
        elif token.dep_ in ["prep", "pobj"]:
            tag = "Circumstance"
            counts["Circumstances"] += 1
        if token.pos_ == "AUX":
            counts["Modals"] += 1
        if token.pos_ == "NOUN" and token.text.endswith(("tion", "ment", "ance")):
            counts["Nominalizations"] += 1

        analysis.append({"word": token.text, "tag": tag})

    return analysis, counts

def generate_pdf(text, analysis, counts):
    """Generates a PDF report of the analysis."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="SFL Text Analysis Report", ln=True, align='C')
    pdf.ln(5)
    pdf.multi_cell(0, 7, text)
    pdf.ln(5)

    pdf.cell(200, 10, txt="Linguistic Analysis:", ln=True)
    for word in analysis:
        tag = word["tag"]
        if tag:
            pdf.cell(0, 7, f'{word["word"]} - {tag}', ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Summary Table:", ln=True)
    for k, v in counts.items():
        pdf.cell(0, 7, f'{k}: {v}', ln=True)

    pdf_file = "analysis_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    analysis, counts = analyze_text_sfl(text)
    pdf_file = generate_pdf(text, analysis, counts)

    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
