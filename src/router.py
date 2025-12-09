# src/router.py
from typing import Tuple, Dict, Any

FAST_TRACK_THRESHOLD = 25000  # currency units (₹) as per brief

def route_claim(extracted: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
    # Priority-based routing decisions with simple explanations
    if validation.get("missingFields"):
        return {
            "route": "Manual Review",
            "reason": "Missing mandatory fields: " + ", ".join(validation.get("missingFields"))
        }

    if validation.get("investigation_flag"):
        return {
            "route": "Investigation",
            "reason": "Suspicious keywords found in description; investigation flagged."
        }

    claim_type = (extracted.get("claim_type") or "").lower()
    if "injury" in claim_type or "health" in claim_type:
        return {
            "route": "Specialist Queue",
            "reason": "Claim indicates injury/medical; send to specialist queue."
        }

    amt = extracted.get("estimated_damage")
    if amt is not None:
        if amt < FAST_TRACK_THRESHOLD:
            return {
                "route": "Fast-track",
                "reason": f"Estimated damage {amt} < {FAST_TRACK_THRESHOLD} and no critical inconsistencies."
            }
        else:
            return {
                "route": "Manual Review",
                "reason": f"Estimated damage {amt} >= {FAST_TRACK_THRESHOLD} — manual review required."
            }

    # default fallback
    return {
        "route": "Manual Review",
        "reason": "Insufficient information to route automatically."
    }
