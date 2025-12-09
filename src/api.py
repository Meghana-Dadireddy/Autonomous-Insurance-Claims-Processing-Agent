# src/api.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import tempfile
import shutil
from .extractor import extract_all_fields
from .validator import validate_extracted
from .router import route_claim

app = FastAPI(title="Autonomous FNOL Processor (Lite)")

@app.post("/process-fnol")
async def process_fnol(file: UploadFile = File(...)):
    # Save to a temp file then process
    suffix = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + suffix) as tmp:
        tmp_path = tmp.name
        contents = await file.read()
        tmp.write(contents)
    try:
        extracted = extract_all_fields(tmp_path)
        validation = validate_extracted(extracted)
        routing = route_claim(extracted, validation)
        result = {
            "extractedFields": extracted,
            "validation": validation,
            "recommendedRoute": routing["route"],
            "reasoning": routing["reason"]
        }
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
