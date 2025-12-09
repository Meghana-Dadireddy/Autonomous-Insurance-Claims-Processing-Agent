# src/validator.py
from typing import Dict, Any
from datetime import date
import re

MANDATORY_FIELDS = ["policy_number", "policyholder_name", "incident_date", "claim_type"]

def validate_extracted(extracted: Dict[str, Any]) -> Dict[str, Any]:
    missing = []
    inconsistencies = []
    investigation_flag = False

    # missing fields
    for f in MANDATORY_FIELDS:
        if not extracted.get(f):
            missing.append(f)

    # date checks
    incident_date = extracted.get("incident_date")
    if incident_date:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(incident_date)
            if dt.date() > date.today():
                inconsistencies.append("incident_date_in_future")
        except Exception:
            inconsistencies.append("incident_date_unparseable")

    # amount sanity
    amt = extracted.get("estimated_damage")
    if amt is not None:
        if amt < 0:
            inconsistencies.append("negative_estimated_damage")

    # contradiction: claim_type vs description keywords
    desc = extracted.get("description", "") or ""
    if desc:
        desc_lower = desc.lower()
        # If description has clear auto keywords but claim_type is not auto
        has_auto = any(k in desc_lower for k in ["collision", "rear", "front", "vehicle", "car", "truck", "automobile"])
        has_property = any(k in desc_lower for k in ["water", "flood", "roof", "leak", "fire", "burglary", "theft"])
        has_health = any(k in desc_lower for k in ["injury", "hurt", "hospital", "bleed", "medical", "fracture"])

        ct = (extracted.get("claim_type") or "").lower()
        if has_auto and ct and "auto" not in ct:
            inconsistencies.append("claim_type_mismatch_with_description_auto")
        if has_property and ct and "property" not in ct:
            inconsistencies.append("claim_type_mismatch_with_description_property")
        if has_health and ct and "health" not in ct and "injury" not in ct:
            inconsistencies.append("claim_type_mismatch_with_description_health")

        # Fraud / suspicious keywords
        if re.search(r"\b(staged|fraud|inconsistent|contradictory|false)\b", desc_lower):
            investigation_flag = True

    # contact phone plausibility
    phone = extracted.get("contact_phone")
    if phone:
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 7:
            inconsistencies.append("contact_phone_too_short")

    return {
        "missingFields": missing,
        "inconsistencies": inconsistencies,
        "investigation_flag": investigation_flag
    }
