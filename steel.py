# from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException
# import PyPDF2
# import io
# import re
# import json
#
# app = FastAPI(title="api")
# router = APIRouter()
#
# def extract_details(text):
#     data = {
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
#
#         "Environmental_Conditions": {
#             "Temperature": "",
#             "Relative_Humidity": ""
#         },
#         "Sample_Details": {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": "",
#             "Chemical_Composition": {
#                 "Sample_No": "",
#                 "C": "",
#                 "Si": "",
#                 "Mn": "",
#                 "Cr": "",
#                 "Ni": "",
#                 "Mo": "",
#                 "P": "",
#                 "S": "",
#                 "Cu": ""
#             }
#         }
#     }
#
#     # Extract Format No. and Date
#     format_match = re.search(r"Format No\.\s*(TR/ML/C/0[56])\s*Rev\.\s*(\d+),\s*Date:\s*(\d{2}\.\d{2}\.\d{4})", text)
#     if format_match:
#         data["Format_No"] = format_match.group(1)
#         data["Format_Date"] = format_match.group(3)
#
#     # Extract No
#     no_match = re.search(r"No:\s*(OFMK/ML[-~]\d+/TR/\d+)", text)
#     if no_match:
#         data["No"] = no_match.group(1)
#
#     # Extract Report No
#     report_match = re.search(r"Report No:.*?(ULR)", text, re.IGNORECASE)
#     if report_match:
#         data["Report_No"] = report_match.group(1)
#
#     # Extract Name and address
#     name_match = re.search(r"Name and address of customer\s*([^\n]+)", text)
#     if name_match:
#         data["Name_and_address"] = name_match.group(1).strip()
#
#     # Extract Sample Forwarding Letter
#     sample_match = re.search(r"Sample Forwarding Letter No\. & Date\s*([^\n]+)", text)
#     if sample_match:
#         data["Sample_Forwarding_Letter"] = sample_match.group(1).strip()
#
#     # Extract Specification/Grade
#     spec_match = re.search(r"Specification / Grade\s*([^\n]+)", text)
#     if spec_match:
#         data["Specification_Grade"] = spec_match.group(1).strip()
#
#     # Extract Date of Receipt
#     receipt_match = re.search(r"Date of Receipt of sample\s*([^\n]+)", text)
#     if receipt_match:
#         data["Date_of_Receipt"] = receipt_match.group(1).strip()
#
#     # Extract Test Performed on
#     test_date_match = re.search(r"Test Performed on\s*([^\n]+)", text)
#     if test_date_match:
#         data["Test_Performed_on"] = test_date_match.group(1).strip()
#
#     # Extract Test Method
#     test_method_match = re.search(r"Test Method\s*([^\n]+)", text)
#     if test_method_match:
#         data["Test_Method"] = test_method_match.group(1).strip()
#
#     # Extract Environmental Conditions
#     # Updated temperature pattern to match the specific format
#     temp_match = re.search(r"Temperature.*?(\d{2,3})", text, re.IGNORECASE)
#     if temp_match:
#         data["Environmental_Conditions"]["Temperature"] = temp_match.group(1)
#
#     humidity_match = re.search(r"Relative Humidity.*?(\d{2,3})", text)
#     if humidity_match:
#         data["Environmental_Conditions"]["Relative_Humidity"] = humidity_match.group(1)
#
#     # Extract Sample Details from first table
#     sample_details_pattern = re.search(r"Customer\s*Sample.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text, re.DOTALL)
#     if sample_details_pattern:
#         data["Sample_Details"]["Customer_Sample_No"] = sample_details_pattern.group(1)
#         data["Sample_Details"]["Sample_Description_Size"] = sample_details_pattern.group(2)
#         data["Sample_Details"]["Sample_Colour_Condition"] = sample_details_pattern.group(3)
#         data["Sample_Details"]["Lab_Sample_No"] = sample_details_pattern.group(4)
#
#     # Extract Chemical Composition from second table
#     chemical_pattern = re.search(r"Sample\s*No\.\s*%C\s*%Si\s*%Mn\s*%Cr\s*%Ni\s*%Mo\s*%P\s*%S\s*%Cu.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)", text, re.DOTALL)
#     if chemical_pattern:
#         data["Sample_Details"]["Chemical_Composition"]["Sample_No"] = chemical_pattern.group(1)
#         data["Sample_Details"]["Chemical_Composition"]["C"] = chemical_pattern.group(2)
#         data["Sample_Details"]["Chemical_Composition"]["Si"] = chemical_pattern.group(3)
#         data["Sample_Details"]["Chemical_Composition"]["Mn"] = chemical_pattern.group(4)
#         data["Sample_Details"]["Chemical_Composition"]["Cr"] = chemical_pattern.group(5)
#         data["Sample_Details"]["Chemical_Composition"]["Ni"] = chemical_pattern.group(6)
#         data["Sample_Details"]["Chemical_Composition"]["Mo"] = chemical_pattern.group(7)
#         data["Sample_Details"]["Chemical_Composition"]["P"] = chemical_pattern.group(8)
#         data["Sample_Details"]["Chemical_Composition"]["S"] = chemical_pattern.group(9)
#         data["Sample_Details"]["Chemical_Composition"]["Cu"] = chemical_pattern.group(10)
#
#     return data
#
# @router.post("/upload-pdf")
# async def upload_pdf(file: UploadFile = File(...)):
#     try:
#         pdf_content = await file.read()
#         pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text() + "\n"
#
#         data = extract_details(text)
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# #
# app.include_router(router)
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("steel:app", host="localhost", port=8000, reload=True)

























from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import PyPDF2
import io
import re
import json
import logging
from typing import Dict, Any, List

# Import database and models
from db import get_db, engine, Base
from models import SteelPDF

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Steel API Service")
router = APIRouter()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)


def extract_details(text):
    data = {
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
            "Lab_Sample_No": "",
            "Chemical_Composition": {
                "Sample_No": "",
                "C": "",
                "Si": "",
                "Mn": "",
                "Cr": "",
                "Ni": "",
                "Mo": "",
                "P": "",
                "S": "",
                "Cu": ""
            }
        }
    }

    # Extract Format No. and Date
    format_match = re.search(r"Format No\.\s*(TR/ML/C/0[56])\s*Rev\.\s*(\d+),\s*Date:\s*(\d{2}\.\d{2}\.\d{4})", text)
    if format_match:
        data["Format_No"] = format_match.group(1)
        data["Format_Date"] = format_match.group(3)

    # Extract No
    no_match = re.search(r"No:\s*(OFMK/ML[-~]\d+/TR/\d+)", text)
    if no_match:
        data["No"] = no_match.group(1)

    # Extract Report No
    report_match = re.search(r"Report No:.*?(ULR)", text, re.IGNORECASE)
    if report_match:
        data["Report_No"] = report_match.group(1)

    # Extract Name and address
    name_match = re.search(r"Name and address of customer\s*([^\n]+)", text)
    if name_match:
        data["Name_and_address"] = name_match.group(1).strip()

    # Extract Sample Forwarding Letter
    sample_match = re.search(r"Sample Forwarding Letter No\. & Date\s*([^\n]+)", text)
    if sample_match:
        data["Sample_Forwarding_Letter"] = sample_match.group(1).strip()

    # Extract Specification/Grade
    spec_match = re.search(r"Specification / Grade\s*([^\n]+)", text)
    if spec_match:
        data["Specification_Grade"] = spec_match.group(1).strip()

    # Extract Date of Receipt
    receipt_match = re.search(r"Date of Receipt of sample\s*([^\n]+)", text)
    if receipt_match:
        data["Date_of_Receipt"] = receipt_match.group(1).strip()

    # Extract Test Performed on
    test_date_match = re.search(r"Test Performed on\s*([^\n]+)", text)
    if test_date_match:
        data["Test_Performed_on"] = test_date_match.group(1).strip()

    # Extract Test Method
    test_method_match = re.search(r"Test Method\s*([^\n]+)", text)
    if test_method_match:
        data["Test_Method"] = test_method_match.group(1).strip()

    # Extract Environmental Conditions
    # Updated temperature pattern to match the specific format
    temp_match = re.search(r"Temperature.*?(\d{2,3})", text, re.IGNORECASE)
    if temp_match:
        data["Environmental_Conditions"]["Temperature"] = temp_match.group(1)

    humidity_match = re.search(r"Relative Humidity.*?(\d{2,3})", text)
    if humidity_match:
        data["Environmental_Conditions"]["Relative_Humidity"] = humidity_match.group(1)

    # Extract Sample Details from first table
    sample_details_pattern = re.search(r"Customer\s*Sample.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text, re.DOTALL)
    if sample_details_pattern:
        data["Sample_Details"]["Customer_Sample_No"] = sample_details_pattern.group(1)
        data["Sample_Details"]["Sample_Description_Size"] = sample_details_pattern.group(2)
        data["Sample_Details"]["Sample_Colour_Condition"] = sample_details_pattern.group(3)
        data["Sample_Details"]["Lab_Sample_No"] = sample_details_pattern.group(4)

    # Extract Chemical Composition from second table
    chemical_pattern = re.search(r"Sample\s*No\.\s*%C\s*%Si\s*%Mn\s*%Cr\s*%Ni\s*%Mo\s*%P\s*%S\s*%Cu.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)", text, re.DOTALL)
    if chemical_pattern:
        data["Sample_Details"]["Chemical_Composition"]["Sample_No"] = chemical_pattern.group(1)
        data["Sample_Details"]["Chemical_Composition"]["C"] = chemical_pattern.group(2)
        data["Sample_Details"]["Chemical_Composition"]["Si"] = chemical_pattern.group(3)
        data["Sample_Details"]["Chemical_Composition"]["Mn"] = chemical_pattern.group(4)
        data["Sample_Details"]["Chemical_Composition"]["Cr"] = chemical_pattern.group(5)
        data["Sample_Details"]["Chemical_Composition"]["Ni"] = chemical_pattern.group(6)
        data["Sample_Details"]["Chemical_Composition"]["Mo"] = chemical_pattern.group(7)
        data["Sample_Details"]["Chemical_Composition"]["P"] = chemical_pattern.group(8)
        data["Sample_Details"]["Chemical_Composition"]["S"] = chemical_pattern.group(9)
        data["Sample_Details"]["Chemical_Composition"]["Cu"] = chemical_pattern.group(10)

    return data

def save_pdf_to_db(db: Session, filename: str) -> SteelPDF:
    """Save PDF file information to database"""
    try:
        pdf_record = SteelPDF(
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


@router.post("/upload-pdf", summary="Upload Steel PDF Report")
async def upload_pdf(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and process a steel test report PDF file.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a PDF file."
        )

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

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.get("/pdfs", response_model=List[Dict[str, Any]])
async def get_all_pdfs(db: Session = Depends(get_db)):
    """Get all PDF records"""
    try:
        pdfs = db.query(SteelPDF).all()
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
        pdf = db.query(SteelPDF).filter(SteelPDF.id == pdf_id).first()
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
        pdf = db.query(SteelPDF).filter(SteelPDF.id == pdf_id).first()
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
        pdf = db.query(SteelPDF).filter(SteelPDF.id == pdf_id).first()
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
app.include_router(router, prefix="/steel", tags=["Steel"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("steel:app", host="localhost", port=8000, reload=True)