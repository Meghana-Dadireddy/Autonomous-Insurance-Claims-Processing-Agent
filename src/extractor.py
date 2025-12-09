# src/extractor.py
import re
from dateutil import parser as dateparser
from .utils import read_pdf_text, normalize_amount, split_lines
from typing import Dict, Any, Optional

# Patterns for common fields on ACORD and FNOL forms.
FIELD_PATTERNS = {
    "policy_number": [r"Policy\s*Number[:\s]*([A-Z0-9\-\/]+)", r"POLICY\s*NUMBER[:\s]*([A-Z0-9\-\/]+)", r"Policy No[:\s]*([A-Z0-9\-\/]+)"],
    "policyholder_name": [r"Name\s*of\s*Insured[:\s]*([A-Za-z ,.'\-\(\)]+)", r"Insured[:\s]*([A-Za-z ,.'\-\(\)]+)", r"NAME\s*OF\s*INSURED[:\s]*([A-Za-z ,.'\-\(\)]+)"],
    "claim_type": [r"Type\s*of\s*Loss[:\s]*([A-Za-z ]+)", r"Claim\s*Type[:\s]*([A-Za-z ]+)", r"LOSS\s*TYPE[:\s]*([A-Za-z ]+)"],
    "incident_date": [r"Date\s*of\s*Loss[:\s]*([0-9A-Za-z\-/\,\s]+)", r"Date\s*of\s*Loss[:\s]*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})", r"Date\s*of\s*Accident[:\s]*([0-9A-Za-z\-/\,\s]+)"],
    "contact_phone": [r"Phone[:\s]*([\+\d\(\)\-\s]{7,})", r"Contact\s*Phone[:\s]*([\+\d\(\)\-\s]{7,})", r"Phone Number[:\s]*([\+\d\(\)\-\s]{7,})"],
    "estimated_damage": [r"Estimated\s*Loss[:\s]*([\d\.,\s₹$]+)", r"Estimate\s*of\s*Loss[:\s]*([\d\.,\s₹$]+)", r"Amount\s*of\s*Loss[:\s]*([\d\.,\s₹$]+)"],
    "location": [r"Location[:\s]*([A-Za-z0-9, \-]+)", r"Place[:\s]*([A-Za-z0-9, \-]+)"],
    "description": [r"Description[:\s]*(.+)"],  # fallback - greedy, we'll trim
}

def find_first(patterns, text):
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()
    return None

def parse_date(raw: Optional[str]):
    if not raw:
        return None
    try:
        dt = dateparser.parse(raw, dayfirst=False, fuzzy=True)
        return dt.date().isoformat()
    except Exception:
        return None

def extract_all_fields(pdf_path: str) -> Dict[str, Any]:
    text = read_pdf_text(pdf_path)
    lines = split_lines(text)
    # Quick heuristic: join lines with separator for multi-line search
    joined = "\n".join(lines)

    extracted = {}

    # first pass: regex patterns
    for field, patterns in FIELD_PATTERNS.items():
        raw = find_first(patterns, joined)
        extracted[field] = raw

    # if description missing, try capturing nearby lines labeled 'Description' or the 'Narrative' area
    if not extracted.get("description"):
        for i, line in enumerate(lines):
            if re.search(r"Description|Narrative|Details", line, re.IGNORECASE):
                # collect next 1-3 lines as description
                desc = " ".join(lines[i:i+4])
                extracted["description"] = desc
                break

    # normalize amounts & dates
    extracted["estimated_damage"] = normalize_amount(extracted.get("estimated_damage"))
    extracted["incident_date"] = parse_date(extracted.get("incident_date"))

    # If claim_type not found, attempt to infer from description keywords
    if not extracted.get("claim_type") and extracted.get("description"):
        desc = extracted["description"].lower()
        if any(k in desc for k in ["collision", "rear", "front", "vehicle", "car", "truck", "automobile"]):
            extracted["claim_type"] = "Auto"
        elif any(k in desc for k in ["water", "flood", "leak", "roof", "fire", "burglary", "theft"]):
            extracted["claim_type"] = "Property"
        elif any(k in desc for k in ["injury", "hurt", "hospital", "medical"]):
            extracted["claim_type"] = "Health"
        else:
            extracted["claim_type"] = None

    # policy number heuristics: if not found, search for typical ACORD field style words
    if not extracted.get("policy_number"):
        m = re.search(r"\b[A-Z0-9]{4,}\b", joined)
        if m:
            extracted["policy_number"] = m.group(0)

    # minimal cleanup
    for k, v in list(extracted.items()):
        if isinstance(v, str):
            extracted[k] = v.strip()

    # keep raw text sample for debugging
    extracted["_raw_text_snippet"] = "\n".join(lines[:30])
    return extracted
