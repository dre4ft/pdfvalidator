from fastapi import  APIRouter, UploadFile, File, Body
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
    "received_paths": saved_paths,
    "status": result
    })




