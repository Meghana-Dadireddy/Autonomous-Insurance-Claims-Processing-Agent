# tests/test_pipeline.py
import os
from src.extractor import extract_all_fields
from src.validator import validate_extracted
from src.router import route_claim

DATA_PDF = "/mnt/data/ACORD-Automobile-Loss-Notice-12.05.16.pdf"

def test_pipeline_runs():
    assert os.path.exists(DATA_PDF), f"Sample PDF not found at {DATA_PDF}"
    extracted = extract_all_fields(DATA_PDF)
    # extracted should be a dict
    assert isinstance(extracted, dict)
    validation = validate_extracted(extracted)
    assert "missingFields" in validation and "inconsistencies" in validation
    routing = route_claim(extracted, validation)
    assert "route" in routing and "reason" in routing
