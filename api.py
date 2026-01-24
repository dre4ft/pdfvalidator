from fastapi import  APIRouter, UploadFile, File, Body,HTTPException
from pdf_validator import api_runner
from fastapi.responses import JSONResponse
from typing import List
import os

api_router = APIRouter(prefix="/api", tags=["api"])

UPLOAD_DIR = "to_analyze"

@api_router.post("/scan/remote")
async def scan_remote(files: List[UploadFile] = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    saved_paths = []
    for f in files:
        save_path = os.path.join(UPLOAD_DIR, f.filename)
        with open(save_path, "wb") as out_file:
            content = await f.read()
            out_file.write(content)
        
        saved_paths.append(save_path)

    
    result = api_runner(saved_paths) 

    return JSONResponse(content={
    "mode": "remote",
    "received_paths": [f.filename for f in files],
    "status": result
    })

@api_router.post("/yara/update")
async def update_yara_rules(rules: str = Body(..., media_type="text/plain")):
    YARA_RULES_FILE = "yara_rules/pdf.yara"
    with open(YARA_RULES_FILE, "a") as f:
        f.write(rules)
    
    return JSONResponse(content={"status": "YARA rules updated successfully."})

@api_router.get("/yara/rules")
async def get_yara_rules():
    YARA_RULES_FILE = "yara_rules/pdf.yara"
    if not os.path.isfile(YARA_RULES_FILE):
        raise HTTPException(status_code=404, detail="YARA rules file not found.")

    with open(YARA_RULES_FILE, "r") as f:
        rules = f.read()
    
    return JSONResponse(content={"rules": rules})



