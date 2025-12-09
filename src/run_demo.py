# src/run_demo.py
import argparse
import json
from .extractor import extract_all_fields
from .validator import validate_extracted
from .router import route_claim

def run(pdf_path: str):
    print(f"Processing: {pdf_path}")
    extracted = extract_all_fields(pdf_path)
    validation = validate_extracted(extracted)
    routing = route_claim(extracted, validation)
    output = {
        "extractedFields": extracted,
        "validation": validation,
        "recommendedRoute": routing["route"],
        "reasoning": routing["reason"]
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process FNOL PDF and produce extraction + routing JSON.")
    parser.add_argument("pdf", help="Path to the FNOL PDF file", nargs='?', default="/mnt/data/ACORD-Automobile-Loss-Notice-12.05.16.pdf")
    args = parser.parse_args()
    run(args.pdf)
