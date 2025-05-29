# from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from typing import Dict, Any
# import PyPDF2
# import io
# import re
# import json
# import logging
#
# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Initialize FastAPI app
# app = FastAPI(
#     title="Mechanical Property API",
#     description="API for extracting mechanical properties from PDF documents",
#     version="1.0.0"
# )
#
# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# router = APIRouter()
#
# def initialize_data_structure() -> Dict[str, Any]:
#     """Initialize the data structure for storing extracted information."""
#     return {
#         "Format_No": "",
#         "Format_Date": "",
#         "No": "",
#         "Report_No": "",
#         "Name_and_address": "",
#         "Sample_Forwarding_Letter": "",
#         "Specification_Grade": "",
#         "Date_of_Receipt": "",
#         "Test_Performed_on": "",
#         "Test_Method": "",
#         "Environmental_Conditions": {
#             "Temperature": "",
#             "Relative_Humidity": ""
#         },
#         "Sample_Details": {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": ""
#         },
#         "Mechanical_Properties": {
#             "Melt_No_Batch_No": "",
#             "UTS_MPa": "",
#             "YS_MPa": "",
#             "EL": "",
#             "RA": "",
#             "PS_02_MPa": "",
#             "Hardness": "",
#             "Impact_Strength_Joules": ""
#         }
#     }
#
# def clean_report_no(text: str) -> str:
#     """Clean and format the Report No value."""
#     # Remove any name and address information
#     if "Name and address" in text:
#         text = text.split("Name and address")[0]
#
#     # Extract only the TC/ULR number
#     pattern = r"(?:ULR|TC)\s*(?:\d+\s*)+(?=\s|$)"
#     match = re.search(pattern, text)
#     if match:
#         # Clean up extra spaces and format consistently
#         report_no = match.group(0)
#         report_no = re.sub(r'\s+', ' ', report_no).strip()
#         return report_no
#     return ""
#
# def extract_mechanical_properties(text: str) -> Dict[str, str]:
#     """Extract mechanical properties using multiple pattern matching strategies."""
#     data = {
#         "Melt_No_Batch_No": "",
#         "UTS_MPa": "",
#         "YS_MPa": "",
#         "EL": "",
#         "RA": "",
#         "PS_02_MPa": "",
#         "Hardness": "",
#         "Impact_Strength_Joules": ""
#     }
#
#     try:
#         # Strategy 1: Look for number sequences in various formats
#         number_patterns = [
#             r"(?:Melt|Batch|No\.?|UTS|YS|EL|RA|PS|Hardness|Impact).*?\n?\s*(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)",
#             r'(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)',
#             r'(?:^|\n).*?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)'
#         ]
#
#         for pattern in number_patterns:
#             matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
#             if matches:
#                 values = matches[0]
#                 keys = list(data.keys())
#                 for i, value in enumerate(values):
#                     if i < len(keys):
#                         data[keys[i]] = value.strip()
#                 if any(data.values()):
#                     break
#
#         # Strategy 2: Individual property patterns
#         if not any(data.values()):
#             property_patterns = {
#                 "Melt_No_Batch_No": [
#                     r"(?:Melt|Batch)\s*(?:No\.?|Number)\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"(?:^|\n|\t)\s*(\d+)(?:\s|$)"
#                 ],
#                 "UTS_MPa": [
#                     r"UTS\s*(?:Mpa|MPa)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"Ultimate\s*Tensile\s*Strength\s*[:/]?\s*(\d+(?:\.\d+)?)"
#                 ],
#                 "YS_MPa": [
#                     r"YS\s*(?:Mpa|MPa)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"Yield\s*Strength\s*[:/]?\s*(\d+(?:\.\d+)?)"
#                 ],
#                 "EL": [
#                     r"%?\s*EL\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"Elongation\s*[:/]?\s*(\d+(?:\.\d+)?)"
#                 ],
#                 "RA": [
#                     r"%?\s*RA\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"Reduction\s*(?:in)?\s*Area\s*[:/]?\s*(\d+(?:\.\d+)?)"
#                 ],
#                 "PS_02_MPa": [
#                     r"0\.2%?\s*PS\s*(?:Mpa|MPa)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"Proof\s*Stress\s*[:/]?\s*(\d+(?:\.\d+)?)"
#                 ],
#                 "Hardness": [
#                     r"Hardness\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"HB\s*[:/]?\s*(\d+(?:\.\d+)?)"
#                 ],
#                 "Impact_Strength_Joules": [
#                     r"Impact\s*(?:Strength)?\s*(?:Joules?)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
#                     r"Impact\s*(?:Test)?\s*[:/]?\s*(\d+(?:\.\d+)?)"
#                 ]
#             }
#
#             for prop, patterns in property_patterns.items():
#                 if not data[prop]:
#                     for pattern in patterns:
#                         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#                         if match:
#                             data[prop] = match.group(1).strip()
#                             break
#
#         return data
#
#     except Exception as e:
#         logger.error(f"Error in mechanical properties extraction: {str(e)}")
#         return data
#
# def extract_details(text: str) -> Dict[str, Any]:
#     """Extract all details from the text using flexible patterns."""
#     data = initialize_data_structure()
#
#     try:
#         # Extract Report No first
#         report_no_pattern = r"Report\s*No:?\s*([^\n]+)"
#         report_no_match = re.search(report_no_pattern, text, re.IGNORECASE)
#         if report_no_match:
#             raw_report_no = report_no_match.group(1)
#             data["Report_No"] = clean_report_no(raw_report_no)
#
#         # Other patterns
#         patterns = {
#             "Format_No": r"(?:Format|Form)\s*No\.?\s*([\w/\-]+)",
#             "Format_Date": r"(?:Date|Dated):\s*(\d{2}[\.-]\d{2}[\.-]\d{4})",
#             "No": r"(?:^|\n)\s*No:?\s*([\w/\-]+)",
#             "Name_and_address": r"Name\s*(?:and|&)\s*address\s*(?:of\s*customer)?\s*([^\n]+)",
#             "Sample_Forwarding_Letter": r"Sample\s*Forwarding\s*Letter\s*No\.\s*&\s*Date\s*([^\n]+)",
#             "Specification_Grade": r"Specification\s*/?\s*Grade\s*([^\n]+)",
#             "Date_of_Receipt": r"Date\s*of\s*Receipt\s*(?:of\s*sample)?\s*([^\n]+)",
#             "Test_Performed_on": r"Test\s*Performed\s*on\s*([^\n]+)",
#             "Test_Method": r"Test\s*Method\s*([^\n]+)"
#         }
#
#         for key, pattern in patterns.items():
#             if key != "Report_No":  # Skip Report_No as it's already handled
#                 match = re.search(pattern, text, re.IGNORECASE)
#                 if match:
#                     data[key] = match.group(1).strip()
#
#         # Environmental Conditions
#         env_patterns = {
#             "Temperature": r"Temperature.*?(\d+(?:\.\d+)?)",
#             "Relative_Humidity": r"(?:Relative\s*)?Humidity.*?(\d+(?:\.\d+)?)"
#         }
#
#         for key, pattern in env_patterns.items():
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 data["Environmental_Conditions"][key] = match.group(1)
#
#         # Sample Details
#         sample_details_pattern = re.search(
#             r"Customer\s*Sample.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
#             text,
#             re.DOTALL
#         )
#         if sample_details_pattern:
#             data["Sample_Details"].update({
#                 "Customer_Sample_No": sample_details_pattern.group(1),
#                 "Sample_Description_Size": sample_details_pattern.group(2),
#                 "Sample_Colour_Condition": sample_details_pattern.group(3),
#                 "Lab_Sample_No": sample_details_pattern.group(4)
#             })
#
#         # Extract Mechanical Properties
#         mechanical_props = extract_mechanical_properties(text)
#         data["Mechanical_Properties"].update(mechanical_props)
#
#         return data
#
#     except Exception as e:
#         logger.error(f"Error in extract_details: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
#
# @router.post("/upload-pdf", response_model=Dict[str, Any])
# async def upload_pdf(file: UploadFile = File(...)):
#     """Upload and process a PDF file to extract mechanical properties."""
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="File must be a PDF")
#
#     try:
#         pdf_content = await file.read()
#         pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
#
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text() + "\n"
#
#         data = extract_details(text)
#         return data
#
#     except PyPDF2.PdfReadError as e:
#         logger.error(f"PDF read error: {str(e)}")
#         raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")
#     except Exception as e:
#         logger.error(f"Error processing PDF: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
#
# # Include router in app
# app.include_router(router)
#
# # Startup event
# @app.on_event("startup")
# async def startup_event():
#     logger.info("Starting up Mechanical Property API")
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("mechanical:app", host="localhost", port=7000, reload=True)
#























from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Dict, Any, List
import PyPDF2
import io
import re
import json
import logging

# Import database and models
from db import get_db, engine, Base
from models import MechanicalPDF

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mechanical Property API",
    description="API for extracting mechanical properties from PDF documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# Create tables
Base.metadata.create_all(bind=engine)


def initialize_data_structure() -> Dict[str, Any]:
    """Initialize the data structure for storing extracted information."""
    return {
        "Format_No": "",
        "Format_Date": "",
        "No": "",
        "Report_No": "",
        "Name_and_address": "",
        "Sample_Forwarding_Letter": "",
        "Specification_Grade": "",
        "Date_of_Receipt": "",
        "Test_Performed_on": "",
        "Test_Method": "",
        "Environmental_Conditions": {
            "Temperature": "",
            "Relative_Humidity": ""
        },
        "Sample_Details": {
            "Customer_Sample_No": "",
            "Sample_Description_Size": "",
            "Sample_Colour_Condition": "",
            "Lab_Sample_No": ""
        },
        "Mechanical_Properties": {
            "Melt_No_Batch_No": "",
            "UTS_MPa": "",
            "YS_MPa": "",
            "EL": "",
            "RA": "",
            "PS_02_MPa": "",
            "Hardness": "",
            "Impact_Strength_Joules": ""
        }
    }

def clean_report_no(text: str) -> str:
    """Clean and format the Report No value."""
    # Remove any name and address information
    if "Name and address" in text:
        text = text.split("Name and address")[0]

    # Extract only the TC/ULR number
    pattern = r"(?:ULR|TC)\s*(?:\d+\s*)+(?=\s|$)"
    match = re.search(pattern, text)
    if match:
        # Clean up extra spaces and format consistently
        report_no = match.group(0)
        report_no = re.sub(r'\s+', ' ', report_no).strip()
        return report_no
    return ""

def extract_mechanical_properties(text: str) -> Dict[str, str]:
    """Extract mechanical properties using multiple pattern matching strategies."""
    data = {
        "Melt_No_Batch_No": "",
        "UTS_MPa": "",
        "YS_MPa": "",
        "EL": "",
        "RA": "",
        "PS_02_MPa": "",
        "Hardness": "",
        "Impact_Strength_Joules": ""
    }

    try:
        # Strategy 1: Look for number sequences in various formats
        number_patterns = [
            r"(?:Melt|Batch|No\.?|UTS|YS|EL|RA|PS|Hardness|Impact).*?\n?\s*(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)",
            r'(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)',
            r'(?:^|\n).*?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)\s*(?:\||\t|\s{2,})?(\d+(?:\.\d+)?)'
        ]

        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                values = matches[0]
                keys = list(data.keys())
                for i, value in enumerate(values):
                    if i < len(keys):
                        data[keys[i]] = value.strip()
                if any(data.values()):
                    break

        # Strategy 2: Individual property patterns
        if not any(data.values()):
            property_patterns = {
                "Melt_No_Batch_No": [
                    r"(?:Melt|Batch)\s*(?:No\.?|Number)\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"(?:^|\n|\t)\s*(\d+)(?:\s|$)"
                ],
                "UTS_MPa": [
                    r"UTS\s*(?:Mpa|MPa)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"Ultimate\s*Tensile\s*Strength\s*[:/]?\s*(\d+(?:\.\d+)?)"
                ],
                "YS_MPa": [
                    r"YS\s*(?:Mpa|MPa)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"Yield\s*Strength\s*[:/]?\s*(\d+(?:\.\d+)?)"
                ],
                "EL": [
                    r"%?\s*EL\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"Elongation\s*[:/]?\s*(\d+(?:\.\d+)?)"
                ],
                "RA": [
                    r"%?\s*RA\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"Reduction\s*(?:in)?\s*Area\s*[:/]?\s*(\d+(?:\.\d+)?)"
                ],
                "PS_02_MPa": [
                    r"0\.2%?\s*PS\s*(?:Mpa|MPa)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"Proof\s*Stress\s*[:/]?\s*(\d+(?:\.\d+)?)"
                ],
                "Hardness": [
                    r"Hardness\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"HB\s*[:/]?\s*(\d+(?:\.\d+)?)"
                ],
                "Impact_Strength_Joules": [
                    r"Impact\s*(?:Strength)?\s*(?:Joules?)?\s*[:/]?\s*(\d+(?:\.\d+)?)",
                    r"Impact\s*(?:Test)?\s*[:/]?\s*(\d+(?:\.\d+)?)"
                ]
            }

            for prop, patterns in property_patterns.items():
                if not data[prop]:
                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                        if match:
                            data[prop] = match.group(1).strip()
                            break

        return data

    except Exception as e:
        logger.error(f"Error in mechanical properties extraction: {str(e)}")
        return data

def extract_details(text: str) -> Dict[str, Any]:
    """Extract all details from the text using flexible patterns."""
    data = initialize_data_structure()

    try:
        # Extract Report No first
        report_no_pattern = r"Report\s*No:?\s*([^\n]+)"
        report_no_match = re.search(report_no_pattern, text, re.IGNORECASE)
        if report_no_match:
            raw_report_no = report_no_match.group(1)
            data["Report_No"] = clean_report_no(raw_report_no)

        # Other patterns
        patterns = {
            "Format_No": r"(?:Format|Form)\s*No\.?\s*([\w/\-]+)",
            "Format_Date": r"(?:Date|Dated):\s*(\d{2}[\.-]\d{2}[\.-]\d{4})",
            "No": r"(?:^|\n)\s*No:?\s*([\w/\-]+)",
            "Name_and_address": r"Name\s*(?:and|&)\s*address\s*(?:of\s*customer)?\s*([^\n]+)",
            "Sample_Forwarding_Letter": r"Sample\s*Forwarding\s*Letter\s*No\.\s*&\s*Date\s*([^\n]+)",
            "Specification_Grade": r"Specification\s*/?\s*Grade\s*([^\n]+)",
            "Date_of_Receipt": r"Date\s*of\s*Receipt\s*(?:of\s*sample)?\s*([^\n]+)",
            "Test_Performed_on": r"Test\s*Performed\s*on\s*([^\n]+)",
            "Test_Method": r"Test\s*Method\s*([^\n]+)"
        }

        for key, pattern in patterns.items():
            if key != "Report_No":  # Skip Report_No as it's already handled
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[key] = match.group(1).strip()

        # Environmental Conditions
        env_patterns = {
            "Temperature": r"Temperature.*?(\d+(?:\.\d+)?)",
            "Relative_Humidity": r"(?:Relative\s*)?Humidity.*?(\d+(?:\.\d+)?)"
        }

        for key, pattern in env_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["Environmental_Conditions"][key] = match.group(1)

        # Sample Details
        sample_details_pattern = re.search(
            r"Customer\s*Sample.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
            text,
            re.DOTALL
        )
        if sample_details_pattern:
            data["Sample_Details"].update({
                "Customer_Sample_No": sample_details_pattern.group(1),
                "Sample_Description_Size": sample_details_pattern.group(2),
                "Sample_Colour_Condition": sample_details_pattern.group(3),
                "Lab_Sample_No": sample_details_pattern.group(4)
            })

        # Extract Mechanical Properties
        mechanical_props = extract_mechanical_properties(text)
        data["Mechanical_Properties"].update(mechanical_props)

        return data

    except Exception as e:
        logger.error(f"Error in extract_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

def save_pdf_to_db(db: Session, filename: str) -> MechanicalPDF:
    """Save PDF file information to database"""
    try:
        pdf_record = MechanicalPDF(
            filename=filename,
            updated_time=datetime.now(),
            updated_date=datetime.now()
        )
        db.add(pdf_record)
        db.commit()
        db.refresh(pdf_record)
        return pdf_record
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving PDF to database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saving PDF to database: {str(e)}"
        )


@router.post("/upload-pdf", response_model=Dict[str, Any])
async def upload_pdf(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """Upload and process a PDF file to extract mechanical properties."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # Save file info to database first
        pdf_record = save_pdf_to_db(db, file.filename)

        pdf_content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        data = extract_details(text)

        # Add database record info to response
        data["db_record"] = {
            "id": pdf_record.id,
            "filename": pdf_record.filename,
            "updated_time": pdf_record.updated_time.isoformat(),
            "updated_date": pdf_record.updated_date.isoformat()
        }

        return {
            "status": "success",
            "message": "PDF processed successfully",
            "data": data
        }

    except PyPDF2.PdfReadError as e:
        logger.error(f"PDF read error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.get("/pdfs", response_model=List[Dict[str, Any]])
async def get_all_pdfs(db: Session = Depends(get_db)):
    """Get all PDF records"""
    try:
        pdfs = db.query(MechanicalPDF).all()
        return [
            {
                "id": pdf.id,
                "filename": pdf.filename,
                "updated_time": pdf.updated_time.isoformat(),
                "updated_date": pdf.updated_date.isoformat()
            }
            for pdf in pdfs
        ]
    except Exception as e:
        logger.error(f"Error retrieving PDFs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving PDFs: {str(e)}"
        )


@router.get("/pdf/{pdf_id}", response_model=Dict[str, Any])
async def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """Get a specific PDF record by ID"""
    try:
        pdf = db.query(MechanicalPDF).filter(MechanicalPDF.id == pdf_id).first()
        if not pdf:
            raise HTTPException(
                status_code=404,
                detail=f"PDF with id {pdf_id} not found"
            )
        return {
            "id": pdf.id,
            "filename": pdf.filename,
            "updated_time": pdf.updated_time.isoformat(),
            "updated_date": pdf.updated_date.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving PDF: {str(e)}"
        )


@router.put("/pdf/{pdf_id}", response_model=Dict[str, Any])
async def update_pdf(
        pdf_id: int,
        filename: str,
        db: Session = Depends(get_db)
):
    """Update a PDF record"""
    try:
        pdf = db.query(MechanicalPDF).filter(MechanicalPDF.id == pdf_id).first()
        if not pdf:
            raise HTTPException(
                status_code=404,
                detail=f"PDF with id {pdf_id} not found"
            )

        pdf.filename = filename
        pdf.updated_time = datetime.now()
        pdf.updated_date = datetime.now()

        db.commit()
        db.refresh(pdf)

        return {
            "id": pdf.id,
            "filename": pdf.filename,
            "updated_time": pdf.updated_time.isoformat(),
            "updated_date": pdf.updated_date.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating PDF: {str(e)}"
        )


@router.delete("/pdf/{pdf_id}")
async def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """Delete a PDF record"""
    try:
        pdf = db.query(MechanicalPDF).filter(MechanicalPDF.id == pdf_id).first()
        if not pdf:
            raise HTTPException(
                status_code=404,
                detail=f"PDF with id {pdf_id} not found"
            )

        db.delete(pdf)
        db.commit()

        return {"message": f"PDF with id {pdf_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting PDF: {str(e)}"
        )


# Include router in app with prefix
app.include_router(router, prefix="/mechanical", tags=["Mechanical"])


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Mechanical Property API")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("mechanical:app", host="localhost", port=7000, reload=True)