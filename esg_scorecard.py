import spacy
import pandas as pd
from datetime import datetime
import re
from collections import Counter
import traceback
import sys
import os
import textwrap

# Refactored to be importable as a module
def generate_esg_scorecard(text, return_analysis_data=False):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text.lower())

    esg_risk_keywords = {
        "Environmental": {
            "pollution": 2, "emission": 2, "toxic": 3, "waste": 1, "contamination": 3,
            "leak": 2, "climate": 2, "greenhouse": 2, "scarcity": 2, "depletion": 2,
            "deforestation": 3, "carbon": 2, "spill": 2, "violation": 2, "fine": 1,
            "fined": 1, "penalty": 2, "cleanup": 1, "remediation": 1, "liability": 2,
            "harm": 2, "destruction": 3, "extinction": 3, "endangered": 2, "habitat loss": 3,
            "flood": 2, "drought": 2, "storm": 2, "wildfire": 3, "temperature": 1,
            "warming": 2, "rising": 1, "shortage": 2, "overuse": 1, "unsustainable": 2,
            "degradation": 3, "non-compliance": 2, "illegal": 3, "unauthorized": 2,
            "banned": 2, "restricted": 1, "hazardous": 3, "dangerous": 3, "risky": 2,
            "unsafe": 2, "uncontrolled": 3
        },
        "Social": {
            "harassment": 3, "abuse": 3, "discrimination": 3, "accident": 2, "injury": 2,
            "fatality": 3, "death": 3, "violence": 3, "assault": 3, "strike": 1,
            "protest": 1, "boycott": 1, "dispute": 2, "conflict": 2, "unrest": 2,
            "opposition": 1, "lawsuit": 2, "complaint": 2, "allegation": 2, "claim": 1,
            "charged": 2, "sued": 2, "prosecuted": 3, "child labor": 3, "forced labor": 3,
            "slavery": 3, "trafficking": 3, "underpaid": 2, "unpaid": 2, "overtime": 1,
            "overwork": 1, "exhaustion": 1, "stress": 1, "burnout": 1, "turnover": 1,
            "quit": 1, "fired": 2, "terminated": 2, "laid off": 2, "downsized": 1,
            "restructured": 1, "closure": 1, "inequality": 2, "unfair": 2, "bias": 2,
            "exclusion": 2, "retaliation": 3, "whistleblower": 2, "breach": 2, "hack": 3,
            "stolen": 3, "exposed": 2, "compromised": 2
        },
        "Governance": {
            "corruption": 3, "bribery": 3, "fraud": 3, "embezzlement": 3, "theft": 3,
            "stealing": 3, "misuse": 2, "criminal": 3, "prosecuted": 3, "charged": 3,
            "arrested": 3, "convicted": 3, "sentenced": 3, "sanctions": 3,
            "investigation": 2, "probe": 2, "inquiry": 2, "audit": 1, "review": 1,
            "examination": 1, "scrutiny": 1, "litigation": 2, "court": 2, "trial": 2,
            "settlement": 1, "judgment": 2, "misconduct": 3, "malpractice": 3,
            "negligence": 3, "failure": 2, "default": 2, "manipulation": 3,
            "insider trading": 3, "conflict": 2, "undisclosed": 3, "hidden": 2,
            "secret": 2, "falsified": 3, "misrepresented": 2, "overstated": 2,
            "understated": 2, "concealed": 3, "withheld": 2, "resignation": 1,
            "dismissed": 2, "removed": 2, "suspended": 2, "replaced": 1, "crisis": 3,
            "scandal": 3, "controversy": 2, "accusation": 2
        }
    }

    lemmas = [token.lemma_ for token in doc]
    category_weighted_scores, category_total_counts = {}, {}
    total_weighted_score = 0
    total_keyword_matches = 0
    analysis_data = []

    for category, keywords in esg_risk_keywords.items():
        weighted_score, total_count, matched_keywords = 0, 0, 0
        for kw, severity in keywords.items():
            count = text.count(kw) if " " in kw else lemmas.count(nlp(kw)[0].lemma_)
            weighted_score += count * severity
            total_count += count
            matched_keywords += 1 if count > 0 else 0

        category_weighted_scores[category] = weighted_score
        category_total_counts[category] = total_count
        total_weighted_score += weighted_score
        total_keyword_matches += total_count
        analysis_data.append({
            "Category": category,
            "Total ESG Terms Matched": total_count,
            "Weighted ESG Risk Score": weighted_score,
            "Unique Keywords Matched": matched_keywords,
            "Total Keywords in Dictionary": len(keywords)
        })

    for entry in analysis_data:
        entry["Risk Percentage (%)"] = round((entry["Weighted ESG Risk Score"] / total_weighted_score) * 100, 2) if total_weighted_score else 0
        entry["Term Percentage (%)"] = round((entry["Total ESG Terms Matched"] / total_keyword_matches) * 100, 2) if total_keyword_matches else 0

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    company_name = "Unknown"
    match = re.search(r"(?:company\\s*name\\s*[:\-]?\\s*|^)([A-Z][a-zA-Z&,\.\s]+(?:Inc|Ltd|Corporation|Corp|LLC|Group|Co\\.|Limited))", text, re.IGNORECASE)
    if match:
        company_name = match.group(1).strip()

    sentence_risk_scores = [(sum(severity * sent.text.lower().count(kw)
        for cat in esg_risk_keywords.values() for kw, severity in cat.items()), sent.text.strip())
        for sent in doc.sents]
    highest_risk_sentence_raw = max(sentence_risk_scores, key=lambda x: x[0])[1] if sentence_risk_scores else "Not Found"

    def summarize_sentence(text, word_limit=30):
        words = text.split()
        return " ".join(words[:word_limit]) + ("..." if len(words) > word_limit else "")

    highest_risk_sentence = summarize_sentence(highest_risk_sentence_raw)

    def categorize_risk(pct):
        return "High" if pct > 60 else "Medium" if pct > 30 else "Low"

    category_risks = {entry["Category"]: categorize_risk(entry["Risk Percentage (%)"]) for entry in analysis_data}
    company_risk = "High Risk" if "High" in category_risks.values() else "Medium Risk" if "Medium" in category_risks.values() else "Low Risk"

    top_keywords = Counter(lemmas).most_common(10)
    top_terms = ", ".join([kw for kw, _ in top_keywords if kw in [k for cat in esg_risk_keywords.values() for k in cat]])
    dominant_category = max(category_weighted_scores.items(), key=lambda x: x[1])[0]

    summary = f"""📄 Company ESG Risk Summary Report
=====================================
🏢 Company Name       : {company_name}
🕒 Date of Analysis   : {timestamp}
📊 Total ESG Terms    : {total_keyword_matches}
⚖️  Total Weighted ESG Score : {total_weighted_score}
🔍 Final ESG Risk Level      : {company_risk}

📌 Summary Insights:
- The document shows **{total_keyword_matches}** ESG-related terms.
- Based on weighted analysis, the company is flagged as **{company_risk}**.
- ESG concerns are especially strong in the **{dominant_category}** category.
- Top relevant ESG terms include: {top_terms or 'N/A'}

🚨 Highlighted Risky Statement (truncated):
\"{highest_risk_sentence}\"
"""
    return summary, analysis_data  # ⬅️ Return both if requested

# CLI usage
if __name__ == "__main__":
    try:
        if not os.path.exists("extracted_text.txt"):
            raise FileNotFoundError("extracted_text.txt not found.")

        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            text = f.read()

        summary = generate_esg_scorecard(text)
        with open("company_esg_risk_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)

        print("✅ ESG Risk Summary generated successfully!")
        print(summary)

    except Exception as e:
        print("❌ Error in esg_scorecard.py:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
