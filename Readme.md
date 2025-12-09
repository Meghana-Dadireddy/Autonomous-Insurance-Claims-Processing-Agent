Autonomous Insurance Claims Processing Agent (Lite Version)

1. From the FNOL (First Notice of Loss) documents given I have noticed the fields that are going to be extracted using an agent. 
2. Listed all fields needed: policy info, incident info, involved parties, asset details, claim type, attachments, and initial estimates.
3. Designed the Workflow – Break the process into steps: input → validation → estimation → classification → record creation → next actions.
4. Implemented Data handling for parsing the information needed from the FNOL forms using Python.
5. The implementation of api.py mainly exposes the pipeline as a service as it receives FNOL forms, runs them through the extractor and validator, and returns the structured FNOL data. It converts the final Python data into JSON for API responses, but the actual field formatting comes from the extractor/router.
6. Used validator.py for handling data inconsistencies and missing fields, this makes routing (router.py)  workflow come under certain circumstances. Checks extracted data against expected formats or mandatory fields to ensure correctness.
7. Used run_demo.py for script to test the entire pipeline locally with sample forms, showing end-to-end extraction and validation.

Example Output for sample.txt:

Processing: data\sample.txt
{

  "extractedFields": {
  
    "policy_number": "ABC12345",
    
    "policyholder_name": "Meghana",
    "claim_type": "Auto",
    "incident_date": "2025-01-10",
    "contact_phone": "9876543210",
    "estimated_damage": 15000,
    "location": "Kurnool, Andhra Pradesh",
    "description": "Vehicle was hit from the rear.\nLocation: Kurnool, Andhra Pradesh",
    "_raw_text_snippet": "Policy Number: ABC12345\nName of Insured: Meghana\nDate of Loss: 2025-01-10\nType of Loss: Auto\nEstimated Loss: ₹15000\nContact Phone: 9876543210\nDescription: Vehicle was hit from the rear.\nLocation: Kurnool, Andhra Pradesh"
  },
  
  "validation": {
  
    "missingFields": [],
    
    "inconsistencies": [],
    
    "investigation_flag": false
  },
  
  "recommendedRoute": "Fast-track",
  
  "reasoning": "Estimated damage 15000 < 25000 and no critical inconsistencies."
}

Steps to run:
1. Open this folder in local VS Code (recommended)
2. Create & Activate Virtual Environment for windows it is 
python -m venv .venv
.venv\Scripts\activate
3. Ensure to install the dependencies from the requirements.txt.
4. Then run the end to end pipeline demo using the command python -m src.run_demo data/sample.txt.
5. You can see the Output in the required JSON format.
   
I have made use of AI in assisting me not to miss any requirements and scope of this task and help me code effeciently according to the constraints provided to make my work finish within a short time.
