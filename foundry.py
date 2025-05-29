# from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import pdfplumber
# import io
# import re
# import logging
# from typing import Dict, Any
#
# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Create both app and router
# app = FastAPI()
# router = APIRouter()
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
#
# def clean_text(text: str) -> str:
#     if not text:
#         return ""
#     return " ".join(text.replace("\n", " ").split()).strip()
#
# def extract_value(text: str, pattern: str, default: str = "") -> str:
#     try:
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#         return clean_text(match.group(1)) if match else default
#     except Exception:
#         return default
#
# def extract_customer_info(text: str) -> str:
#     try:
#         patterns = [
#             r"Name and Address of Customer[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])",
#             r"Customer Details?[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])",
#             r"Client[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])"
#         ]
#
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#             if match:
#                 return clean_text(match.group(1))
#         return ""
#     except Exception:
#         return ""
#
# def extract_sample_details(text: str) -> Dict[str, str]:
#     try:
#         logger.info("Extracting sample details from text: %s", text[:200])
#
#         header_pattern = r"Customer\s*Sampl?e\s*No\.?\s*Sample\s*Description/Size\s*Sample\s*[Cc]olou?r\s*/\s*Condition\s*Lab\s*Sample\s*No\.?"
#         header_match = re.search(header_pattern, text, re.IGNORECASE)
#
#         if header_match:
#             values_text = text[header_match.end():]
#             values_pattern = r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
#             values_match = re.search(values_pattern, values_text)
#
#             if values_match:
#                 logger.info("Found sample values: %s", values_match.groups())
#                 return {
#                     "Customer_Sample_No": values_match.group(1),
#                     "Sample_Description_Size": values_match.group(2),
#                     "Sample_Colour_Condition": values_match.group(3),
#                     "Lab_Sample_No": values_match.group(4)
#                 }
#
#         fallback_pattern = r"(?:^|\n)\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)(?:\s|$)"
#         fallback_match = re.search(fallback_pattern, text, re.MULTILINE)
#
#         if fallback_match:
#             logger.info("Found sample values using fallback: %s", fallback_match.groups())
#             return {
#                 "Customer_Sample_No": fallback_match.group(1),
#                 "Sample_Description_Size": fallback_match.group(2),
#                 "Sample_Colour_Condition": fallback_match.group(3),
#                 "Lab_Sample_No": fallback_match.group(4)
#             }
#
#         logger.warning("No sample details found")
#         return {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": ""
#         }
#     except Exception as e:
#         logger.error("Error extracting sample details: %s", str(e))
#         return {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": ""
#         }
#
# def extract_chemical_properties(text: str) -> Dict[str, str]:
#     try:
#         logger.info("Extracting chemical properties from text: %s", text[:200])
#
#         patterns = [
#             r"Sample\s*No\.\s*%C\s*%Si/%Mn/%Cr\s*(\d+)\s*(\d+(?:\.\d+)?)\s*(\d+(?:\.\d+)?)",
#             r"(\d+)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)"
#         ]
#
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#             if match:
#                 logger.info("Found chemical properties: %s", match.groups())
#                 return {
#                     "Sample_No": match.group(1),
#                     "%C": match.group(2),
#                     "%Si/%Mn/%Cr": match.group(3)
#                 }
#
#         logger.warning("No chemical properties found")
#         return {
#             "Sample_No": "",
#             "%C": "",
#             "%Si/%Mn/%Cr": ""
#         }
#     except Exception as e:
#         logger.error("Error extracting chemical properties: %s", str(e))
#         return {
#             "Sample_No": "",
#             "%C": "",
#             "%Si/%Mn/%Cr": ""
#         }
#
# def process_pdf_text(text: str) -> Dict[str, Any]:
#     try:
#         data = {
#             "format_no": extract_value(text, r"Format\s*No\.\s*(?:TR/ML/NDT/)?(\d+)"),
#             "format_date": extract_value(text, r"Format.*?Date\s*:?\s*(\d{2}[-/.]\d{2}[-/.]\d{4})"),
#             "report_number": extract_value(text, r"(?:Report|Test Report|Certificate)\s*No\.?\s*:?\s*([^\n]+)"),
#             "ulr": extract_value(text, r"ULR\s*:?\s*(\d\s*\d\s*\d\s*\d)"),
#             "name_and_address": extract_customer_info(text),
#             "forwarding_letter": extract_value(text, r"Sample Forwarding Letter No\. & Date\s*([^\n]+)"),
#             "specification": extract_value(text, r"Specification\s*/?\s*Grade\s*:?\s*([^\n]+)"),
#             "receipt_date": extract_value(text, r"Date of Receipt of sample\s*:?\s*([^\n]+)"),
#             "test_date": extract_value(text, r"Test Performed on\s*:?\s*([^\n]+)"),
#             "test_method": extract_value(text, r"Test Method\s*:?\s*([^\n]+)"),
#             "environmental_conditions": {
#                 "temperature": extract_value(text, r"Temperature\s*(?:in\s*°C)?\s*:?\s*(\d+(?:\.\d+)?)"),
#                 "humidity": extract_value(text, r"(?:Relative\s*)?Humidity\s*(?:\(%\))?\s*:?\s*(\d+(?:\.\d+)?)")
#             },
#             "Sample_Details": extract_sample_details(text),
#             "Chemical_Properties": extract_chemical_properties(text)
#         }
#
#         logger.info("Extracted data: %s", data)
#         data = {k: v for k, v in data.items() if v}
#         return data
#
#     except Exception as e:
#         logger.error("Error processing PDF text: %s", str(e))
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error processing PDF text: {str(e)}"
#         )
#
# @router.post("/upload-pdf", summary="Upload Foundry PDF Report",
#              description="Upload and process foundry test report PDF")
# async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
#     """
#     Upload and process a foundry test report PDF file.
#     """
#     if not file.filename.lower().endswith('.pdf'):
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid file format. Please upload a PDF file."
#         )
#
#     try:
#         contents = await file.read()
#         if not contents:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Empty file uploaded"
#             )
#
#         extracted_text = []
#         with pdfplumber.open(io.BytesIO(contents)) as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text()
#                 if text:
#                     extracted_text.append(text)
#
#         if not extracted_text:
#             raise HTTPException(
#                 status_code=422,
#                 detail="Could not extract text from PDF"
#             )
#
#         full_text = "\n".join(extracted_text)
#         report_data = process_pdf_text(full_text)
#
#         return {
#             "status": "success",
#             "message": "PDF processed successfully",
#             "data": report_data
#         }
#
#     except Exception as e:
#         logger.error("Error processing PDF: %s", str(e))
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error processing PDF: {str(e)}"
#         )
#
# # Include router in app with prefix
# app.include_router(router, prefix="/foundry", tags=["Foundry"])
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("foundry:app", host="localhost", port=15000, reload=True)
#
#
#
#









from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pdfplumber
import io
import re
import logging
from typing import Dict, Any, List
from datetime import datetime

from db import get_db
from models import FoundryPDF

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create both app and router
app = FastAPI()
router = APIRouter()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.replace("\n", " ").split()).strip()

def extract_value(text: str, pattern: str, default: str = "") -> str:
    try:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return clean_text(match.group(1)) if match else default
    except Exception:
        return default

def extract_customer_info(text: str) -> str:
    try:
        patterns = [
            r"Name and Address of Customer[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])",
            r"Customer Details?[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])",
            r"Client[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return clean_text(match.group(1))
        return ""
    except Exception:
        return ""

def extract_sample_details(text: str) -> Dict[str, str]:
    try:
        logger.info("Extracting sample details from text: %s", text[:200])

        header_pattern = r"Customer\s*Sampl?e\s*No\.?\s*Sample\s*Description/Size\s*Sample\s*[Cc]olou?r\s*/\s*Condition\s*Lab\s*Sample\s*No\.?"
        header_match = re.search(header_pattern, text, re.IGNORECASE)

        if header_match:
            values_text = text[header_match.end():]
            values_pattern = r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
            values_match = re.search(values_pattern, values_text)

            if values_match:
                logger.info("Found sample values: %s", values_match.groups())
                return {
                    "Customer_Sample_No": values_match.group(1),
                    "Sample_Description_Size": values_match.group(2),
                    "Sample_Colour_Condition": values_match.group(3),
                    "Lab_Sample_No": values_match.group(4)
                }

        fallback_pattern = r"(?:^|\n)\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)(?:\s|$)"
        fallback_match = re.search(fallback_pattern, text, re.MULTILINE)

        if fallback_match:
            logger.info("Found sample values using fallback: %s", fallback_match.groups())
            return {
                "Customer_Sample_No": fallback_match.group(1),
                "Sample_Description_Size": fallback_match.group(2),
                "Sample_Colour_Condition": fallback_match.group(3),
                "Lab_Sample_No": fallback_match.group(4)
            }

        logger.warning("No sample details found")
        return {
            "Customer_Sample_No": "",
            "Sample_Description_Size": "",
            "Sample_Colour_Condition": "",
            "Lab_Sample_No": ""
        }
    except Exception as e:
        logger.error("Error extracting sample details: %s", str(e))
        return {
            "Customer_Sample_No": "",
            "Sample_Description_Size": "",
            "Sample_Colour_Condition": "",
            "Lab_Sample_No": ""
        }

def extract_chemical_properties(text: str) -> Dict[str, str]:
    try:
        logger.info("Extracting chemical properties from text: %s", text[:200])

        patterns = [
            r"Sample\s*No\.\s*%C\s*%Si/%Mn/%Cr\s*(\d+)\s*(\d+(?:\.\d+)?)\s*(\d+(?:\.\d+)?)",
            r"(\d+)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                logger.info("Found chemical properties: %s", match.groups())
                return {
                    "Sample_No": match.group(1),
                    "%C": match.group(2),
                    "%Si/%Mn/%Cr": match.group(3)
                }

        logger.warning("No chemical properties found")
        return {
            "Sample_No": "",
            "%C": "",
            "%Si/%Mn/%Cr": ""
        }
    except Exception as e:
        logger.error("Error extracting chemical properties: %s", str(e))
        return {
            "Sample_No": "",
            "%C": "",
            "%Si/%Mn/%Cr": ""
        }

def process_pdf_text(text: str) -> Dict[str, Any]:
    try:
        data = {
            "format_no": extract_value(text, r"Format\s*No\.\s*(?:TR/ML/NDT/)?(\d+)"),
            "format_date": extract_value(text, r"Format.*?Date\s*:?\s*(\d{2}[-/.]\d{2}[-/.]\d{4})"),
            "report_number": extract_value(text, r"(?:Report|Test Report|Certificate)\s*No\.?\s*:?\s*([^\n]+)"),
            "ulr": extract_value(text, r"ULR\s*:?\s*(\d\s*\d\s*\d\s*\d)"),
            "name_and_address": extract_customer_info(text),
            "forwarding_letter": extract_value(text, r"Sample Forwarding Letter No\. & Date\s*([^\n]+)"),
            "specification": extract_value(text, r"Specification\s*/?\s*Grade\s*:?\s*([^\n]+)"),
            "receipt_date": extract_value(text, r"Date of Receipt of sample\s*:?\s*([^\n]+)"),
            "test_date": extract_value(text, r"Test Performed on\s*:?\s*([^\n]+)"),
            "test_method": extract_value(text, r"Test Method\s*:?\s*([^\n]+)"),
            "environmental_conditions": {
                "temperature": extract_value(text, r"Temperature\s*(?:in\s*°C)?\s*:?\s*(\d+(?:\.\d+)?)"),
                "humidity": extract_value(text, r"(?:Relative\s*)?Humidity\s*(?:\(%\))?\s*:?\s*(\d+(?:\.\d+)?)")
            },
            "Sample_Details": extract_sample_details(text),
            "Chemical_Properties": extract_chemical_properties(text)
        }

        logger.info("Extracted data: %s", data)
        data = {k: v for k, v in data.items() if v}
        return data

    except Exception as e:
        logger.error("Error processing PDF text: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF text: {str(e)}"
        )

def save_pdf_to_db(db: Session, filename: str) -> FoundryPDF:
    """Save PDF file information to database"""
    try:
        pdf_record = FoundryPDF(
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


@router.post("/upload-pdf", summary="Upload Foundry PDF Report")
async def upload_pdf(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Upload and process a foundry test report PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a PDF file."
        )

    try:
        # Save file info to database first
        pdf_record = save_pdf_to_db(db, file.filename)

        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )

        extracted_text = []
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from PDF"
            )

        full_text = "\n".join(extracted_text)
        report_data = process_pdf_text(full_text)

        # Add database record info to response
        report_data["db_record"] = {
            "id": pdf_record.id,
            "filename": pdf_record.filename,
            "updated_time": pdf_record.updated_time.isoformat(),
            "updated_date": pdf_record.updated_date.isoformat()
        }

        return {
            "status": "success",
            "message": "PDF processed successfully",
            "data": report_data
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
        pdfs = db.query(FoundryPDF).all()
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
        pdf = db.query(FoundryPDF).filter(FoundryPDF.id == pdf_id).first()
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
        pdf = db.query(FoundryPDF).filter(FoundryPDF.id == pdf_id).first()
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
        pdf = db.query(FoundryPDF).filter(FoundryPDF.id == pdf_id).first()
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
app.include_router(router, prefix="/foundry", tags=["Foundry"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("foundry:app", host="localhost", port=15000, reload=True)