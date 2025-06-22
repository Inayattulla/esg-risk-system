import re
from collections import Counter

# Red-flag keywords (Environmental, Social, Governance)
risk_keywords = [
    # Environmental
    "pollution", "contamination", "spill", "leak", "emission", "toxic", "waste", 
    "dumping", "violation", "breach", "fine", "fined", "penalty", "cleanup", 
    "remediation", "liability", "damage", "harm", "destruction", "deforestation",
    "extinction", "endangered", "habitat loss", "carbon", "greenhouse", "climate",
    "flood", "drought", "storm", "wildfire", "temperature", "warming", "rising",
    "scarcity", "depletion", "shortage", "overuse", "unsustainable", "degradation",
    "non-compliance", "illegal", "unauthorized", "banned", "restricted", "hazardous",
    "dangerous", "risky", "unsafe", "uncontrolled",

    # Social
    "discrimination", "harassment", "abuse", "exploitation", "accident", "injury",
    "fatality", "death", "violence", "assault", "strike", "protest", "boycott",
    "dispute", "conflict", "unrest", "opposition", "lawsuit", "complaint",
    "allegation", "claim", "charged", "sued", "prosecuted", "child labor",
    "forced labor", "slavery", "trafficking", "underpaid", "unpaid", "overtime",
    "overwork", "exhaustion", "stress", "burnout", "turnover", "quit", "fired",
    "terminated", "laid off", "downsized", "restructured", "closure", "inequality",
    "unfair", "bias", "exclusion", "retaliation", "whistleblower", "hack", "stolen",
    "exposed", "compromised",

    # Governance
    "corruption", "bribery", "fraud", "embezzlement", "theft", "stealing", "misuse",
    "criminal", "arrested", "convicted", "sentenced", "sanctions", "investigation",
    "probe", "inquiry", "audit", "review", "examination", "scrutiny", "litigation",
    "court", "trial", "settlement", "judgment", "misconduct", "malpractice",
    "negligence", "failure", "default", "manipulation", "insider trading",
    "undisclosed", "hidden", "secret", "falsified", "misrepresented", "overstated",
    "understated", "concealed", "withheld", "resignation", "dismissed", "removed",
    "suspended", "replaced", "crisis", "scandal", "controversy", "accusation"
]

import spacy
import sys
import traceback
import os

def preprocess_text(text):
    try:
        # Check if extracted_text.txt exists
        if not os.path.exists("extracted_text.txt"):
            print("❌ Error: extracted_text.txt not found.")
            return None

        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            raw_text = f.read()

        print(f"📥 Loaded extracted_text.txt ({len(raw_text)} characters)")

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(raw_text)

        # Preprocess: lemmatize and remove stopwords/punctuation
        cleaned_tokens = [
            token.lemma_ for token in doc
            if not token.is_stop and not token.is_punct and not token.is_space
        ]

        cleaned_text = " ".join(cleaned_tokens)

        with open("cleaned_text.txt", "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print("✅ Preprocessed text saved to cleaned_text.txt")
        return cleaned_text

    except Exception as e:
        print("❌ Error in analyze_text.py:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None

# CLI usage
if __name__ == "__main__":
    result = preprocess_text()
    if result:
        print("🧠 Preprocessing successful.")
    else:
        print("❌ Preprocessing failed.")






