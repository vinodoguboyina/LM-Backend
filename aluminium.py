# from fastapi import APIRouter, File, UploadFile, HTTPException
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
# # Create router
# router = APIRouter()
#
#
# def clean_text(text: str) -> str:
#     if not text:
#         return ""
#     return " ".join(text.replace("\n", " ").split()).strip()
#
#
# def extract_value(text: str, pattern: str, default: str = "") -> str:
#     try:
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#         return clean_text(match.group(1)) if match else default
#     except Exception:
#         return default
#
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
#
# def extract_chemical_values(text: str) -> Dict[str, str]:
#     try:
#         table_pattern = r'Sample\s+No\.\s*%Si\s*%Mg\s*%Mn\s*%Fe\s*%Cu\s*%Ti\s*%Zn\s*%Cr\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)'
#         match = re.search(table_pattern, text, re.DOTALL)
#
#         if match:
#             return {
#                 "Sample No.": match.group(1),
#                 "Si": match.group(2),
#                 "Mg": match.group(3),
#                 "Mn": match.group(4),
#                 "Fe": match.group(5),
#                 "Cu": match.group(6),
#                 "Ti": match.group(7),
#                 "Zn": match.group(8),
#                 "Cr": match.group(9)
#             }
#
#         values_pattern = r'(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'
#         values_match = re.search(values_pattern, text)
#
#         if values_match:
#             return {
#                 "Sample No.": values_match.group(1),
#                 "Si": values_match.group(2),
#                 "Mg": values_match.group(3),
#                 "Mn": values_match.group(4),
#                 "Fe": values_match.group(5),
#                 "Cu": values_match.group(6),
#                 "Ti": values_match.group(7),
#                 "Zn": values_match.group(8),
#                 "Cr": values_match.group(9)
#             }
#         return {}
#     except Exception:
#         return {}
#
#
# def extract_sample_info(text: str) -> Dict[str, str]:
#     try:
#         patterns = [
#             r'Customer\s+Sample.*?No\.\s*Description/Size\s*Condition\s*No\.\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)',
#             r'Sample\s+Details?.*?(\d+).*?([^:\n]+).*?([^:\n]+).*?(\d+)'
#         ]
#
#         for pattern in patterns:
#             match = re.search(pattern, text, re.DOTALL)
#             if match:
#                 return {
#                     "Customer Sample No": clean_text(match.group(1)),
#                     "Sample Description/Size": clean_text(match.group(2)),
#                     "Sample Colour/Condition": clean_text(match.group(3)),
#                     "Lab Sample No": clean_text(match.group(4))
#                 }
#         return {}
#     except Exception:
#         return {}
#
#
# def process_pdf_text(text: str) -> Dict[str, Any]:
#     try:
#         data = {
#             "report_number": extract_value(text, r"(?:Report|Test Report|Certificate)\s*No\.?\s*:?\s*([^\n]+)"),
#             "date": extract_value(text, r"Date\s*:?\s*([^\n]+)"),
#             "name_and_address": extract_customer_info(text),
#             "forwarding_letter": extract_value(text, r"Sample Forwarding Letter No\. & Date\s*([^\n]+)"),
#             "specification": extract_value(text, r"Specification\s*/?\s*Grade\s*:?\s*([^\n]+)"),
#             "receipt_date": extract_value(text, r"Date of Receipt of sample\s*:?\s*([^\n]+)"),
#             "test_date": extract_value(text, r"Test Performed on\s*:?\s*([^\n]+)"),
#             "test_method": extract_value(text, r"Test Method\s*:?\s*([^\n]+)"),
#             "temperature": extract_value(text, r"Temperature\s*(?:in\s*°C)?\s*:?\s*(\d+(?:\.\d+)?)"),
#             "humidity": extract_value(text, r"(?:Relative\s*)?Humidity\s*(?:\(%\))?\s*:?\s*(\d+(?:\.\d+)?)")
#         }
#
#         data = {k: v for k, v in data.items() if v}
#
#         sample_info = extract_sample_info(text)
#         if sample_info:
#             data.update(sample_info)
#
#         chemical_values = extract_chemical_values(text)
#         if chemical_values:
#             if "Sample No." in chemical_values:
#                 data["Sample No."] = chemical_values.pop("Sample No.")
#             data.update(chemical_values)
#
#         return data
#
#     except Exception as e:
#         logger.error(f"Error processing PDF text: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing PDF text: {str(e)}")
#
#
# @router.post("/upload-pdf", summary="Upload Aluminium PDF Report",
#              description="Upload and process aluminium test report PDF")
# async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
#     """
#     Upload and process an aluminium test report PDF file.
#
#     Args:
#         file: PDF file containing aluminium test report
#
#     Returns:
#         Dict containing extracted report data
#     """
#     if not file.filename.lower().endswith('.pdf'):
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid file format. Please upload a PDF file."
#         )
#
#     try:
#         contents = await file.read()
#
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
#         logger.error(f"Error processing PDF: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error processing PDF: {str(e)}"
#         )
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("aluminium:app", host="localhost", port=11000, reload=True)

















from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import pdfplumber
import io
import re
import logging
from typing import Dict, Any, List

# Import database and models
from db import get_db, engine, Base
from models import AluminiumPDF

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create both app and router
app = FastAPI(title="Aluminium API Service")
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


def extract_chemical_values(text: str) -> Dict[str, str]:
    try:
        table_pattern = r'Sample\s+No\.\s*%Si\s*%Mg\s*%Mn\s*%Fe\s*%Cu\s*%Ti\s*%Zn\s*%Cr\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)\s*(\d+\.?\d*)'
        match = re.search(table_pattern, text, re.DOTALL)

        if match:
            return {
                "Sample No.": match.group(1),
                "Si": match.group(2),
                "Mg": match.group(3),
                "Mn": match.group(4),
                "Fe": match.group(5),
                "Cu": match.group(6),
                "Ti": match.group(7),
                "Zn": match.group(8),
                "Cr": match.group(9)
            }

        values_pattern = r'(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'
        values_match = re.search(values_pattern, text)

        if values_match:
            return {
                "Sample No.": values_match.group(1),
                "Si": values_match.group(2),
                "Mg": values_match.group(3),
                "Mn": values_match.group(4),
                "Fe": values_match.group(5),
                "Cu": values_match.group(6),
                "Ti": values_match.group(7),
                "Zn": values_match.group(8),
                "Cr": values_match.group(9)
            }
        return {}
    except Exception:
        return {}


def extract_sample_info(text: str) -> Dict[str, str]:
    try:
        patterns = [
            r'Customer\s+Sample.*?No\.\s*Description/Size\s*Condition\s*No\.\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)',
            r'Sample\s+Details?.*?(\d+).*?([^:\n]+).*?([^:\n]+).*?(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return {
                    "Customer Sample No": clean_text(match.group(1)),
                    "Sample Description/Size": clean_text(match.group(2)),
                    "Sample Colour/Condition": clean_text(match.group(3)),
                    "Lab Sample No": clean_text(match.group(4))
                }
        return {}
    except Exception:
        return {}


def process_pdf_text(text: str) -> Dict[str, Any]:
    try:
        data = {
            "report_number": extract_value(text, r"(?:Report|Test Report|Certificate)\s*No\.?\s*:?\s*([^\n]+)"),
            "date": extract_value(text, r"Date\s*:?\s*([^\n]+)"),
            "name_and_address": extract_customer_info(text),
            "forwarding_letter": extract_value(text, r"Sample Forwarding Letter No\. & Date\s*([^\n]+)"),
            "specification": extract_value(text, r"Specification\s*/?\s*Grade\s*:?\s*([^\n]+)"),
            "receipt_date": extract_value(text, r"Date of Receipt of sample\s*:?\s*([^\n]+)"),
            "test_date": extract_value(text, r"Test Performed on\s*:?\s*([^\n]+)"),
            "test_method": extract_value(text, r"Test Method\s*:?\s*([^\n]+)"),
            "temperature": extract_value(text, r"Temperature\s*(?:in\s*°C)?\s*:?\s*(\d+(?:\.\d+)?)"),
            "humidity": extract_value(text, r"(?:Relative\s*)?Humidity\s*(?:\(%\))?\s*:?\s*(\d+(?:\.\d+)?)")
        }

        data = {k: v for k, v in data.items() if v}

        sample_info = extract_sample_info(text)
        if sample_info:
            data.update(sample_info)

        chemical_values = extract_chemical_values(text)
        if chemical_values:
            if "Sample No." in chemical_values:
                data["Sample No."] = chemical_values.pop("Sample No.")
            data.update(chemical_values)

        return data

    except Exception as e:
        logger.error(f"Error processing PDF text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF text: {str(e)}")

def save_pdf_to_db(db: Session, filename: str) -> AluminiumPDF:
    """Save PDF file information to database"""
    try:
        pdf_record = AluminiumPDF(
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


@router.post("/upload-pdf", summary="Upload Aluminium PDF Report")
async def upload_pdf(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and process an aluminium test report PDF file.
    """
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
        pdfs = db.query(AluminiumPDF).all()
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
        pdf = db.query(AluminiumPDF).filter(AluminiumPDF.id == pdf_id).first()
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
        pdf = db.query(AluminiumPDF).filter(AluminiumPDF.id == pdf_id).first()
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
        pdf = db.query(AluminiumPDF).filter(AluminiumPDF.id == pdf_id).first()
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
app.include_router(router, prefix="/aluminium", tags=["Aluminium"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("aluminium:app", host="localhost", port=11000, reload=True)