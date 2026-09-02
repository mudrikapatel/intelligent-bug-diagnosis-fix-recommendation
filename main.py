from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import os
import traceback
import uuid
from orchestrator import analyze_bug


app = FastAPI(
    title=(
        "Creation of Intelligent Bug Diagnosis Platform "
        "with Fix Recommendation Assistance - Group 1"
    ),
    version="3.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():

    return {
        "status": "AI Bug Analyzer Running",
        "project": "Creation of Intelligent Bug Diagnosis Platform",
        "group": "Group 1",
        "version": "3.0"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    safe_name = (
        os.path.basename(file.filename)
        if file.filename
        else f"bug_{uuid.uuid4().hex}.txt"
    )

    filepath = os.path.join(
        "uploads",
        safe_name
    )

    try:

        content = await file.read()

        with open(
            filepath,
            "wb"
        ) as f:

            f.write(content)

        result = analyze_bug(filepath)

        if not isinstance(result, dict):

            result = {
                "error": "Analyzer returned invalid response."
            }

        return result

    except Exception as e:

        error_message = str(e)

        print(
            "BACKEND ERROR:",
            repr(e)
        )

        traceback.print_exc()

        return {
            "error": error_message,

            "triage": {},

            "log_analysis": {},

            "root_cause": {},

            "duplicates": [],

            "remediation": {
                "recommended_fix": [
                    "Unable to generate fix due to backend error."
                ]
            },

            "similar_bugs": []
        }
