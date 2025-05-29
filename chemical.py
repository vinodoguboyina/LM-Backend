#
# from fastapi import FastAPI, File, APIRouter, UploadFile, HTTPException
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
# app = FastAPI(title="Chemical API Service")
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
#     """Cleans extracted text by removing extra spaces and newlines."""
#     if not text:
#         return ""
#     return " ".join(text.replace("\n", " ").split()).strip()
#
#
# def extract_value(text: str, pattern: str, default: str = "") -> str:
#     """Extracts values based on a regex pattern."""
#     try:
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#         return clean_text(match.group(1)) if match else default
#     except Exception:
#         return default
#
#
# def extract_customer_info(text: str) -> str:
#     """Extracts customer name and address dynamically."""
#     try:
#         patterns = [
#             r"Name and Address of Customer[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])",
#             r"Customer Details?[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])",
#             r"Client[:\s]+([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n[A-Z])"
#         ]
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#             if match:
#                 return clean_text(match.group(1))
#         return ""
#     except Exception:
#         return ""
#
#
# def extract_table_values(text: str) -> Dict[str, Any]:
#     """Extracts values from the ferrous materials table."""
#     try:
#         # Split text into lines for processing
#         lines = text.split('\n')
#
#         # Initialize results dictionary
#         results = {
#             "first_table": {
#                 "customer_sample_no": "",
#                 "sample_description_size": "",
#                 "sample_colour_condition": "",
#                 "lab_sample_no": ""
#             },
#             "second_table": {
#                 "sample_no": "",
#                 "average_grain_size": "",
#                 "depth_of_decarburization": "",
#                 "case_depth": "",
#                 "structure_analysis_micro": "",
#                 "structure_analysis_macro": ""
#             }
#         }
#
#         # Process each line to find table values
#         for i, line in enumerate(lines):
#             # Look for numeric values in lines
#             numbers = re.findall(r'\b\d+\b', line)
#
#             # If we find a line with exactly 4 numbers, it might be the first table
#             if len(numbers) == 4:
#                 # Verify it's not a header line
#                 if not any(header in line.lower() for header in ["customer", "sample", "description", "lab"]):
#                     results["first_table"].update({
#                         "customer_sample_no": numbers[0],
#                         "sample_description_size": numbers[1],
#                         "sample_colour_condition": numbers[2],
#                         "lab_sample_no": numbers[3]
#                     })
#
#             # If we find a line with exactly 6 numbers, it might be the second table
#             elif len(numbers) == 6:
#                 # Verify it's not a header line
#                 if not any(header in line.lower() for header in ["structure", "analysis", "micro", "macro"]):
#                     results["second_table"].update({
#                         "sample_no": numbers[0],
#                         "average_grain_size": numbers[1],
#                         "depth_of_decarburization": numbers[2],
#                         "case_depth": numbers[3],
#                         "structure_analysis_micro": numbers[4],
#                         "structure_analysis_macro": numbers[5]
#                     })
#
#         return results
#     except Exception as e:
#         logger.error(f"Error extracting table values: {str(e)}")
#         return {"first_table": {}, "second_table": {}}
#
#
# def process_pdf_text(text: str) -> Dict[str, Any]:
#     """Processes the extracted text from the PDF and structures it in a dictionary."""
#     try:
#         # Extract table values
#         table_data = extract_table_values(text)
#
#         # Extract metadata using more flexible patterns
#         metadata_patterns = {
#             "report_number": r"(?:Report|Certificate|Test Report)\s*No\.?\s*:?\s*([^\n\r]+)",
#             "name_and_address": r"Name and [Aa]ddress of [Cc]ustomer\s*:?\s*([^\n\r]+)",
#             "forwarding_letter": r"(?:Sample Forwarding Letter|Reference)\s*(?:No\.?)?\s*(?:&|and)?\s*Date\s*:?\s*([^\n\r]+)",
#             "specification": r"(?:Specification|Grade|Standard)\s*/?(?:Grade)?\s*:?\s*([^\n\r]+)",
#             "receipt_date": r"(?:Date of Receipt|Receipt Date)\s*(?:of sample)?\s*:?\s*([^\n\r]+)",
#             "test_date": r"(?:Test Performed|Testing Date|Test Date)\s*(?:on)?\s*:?\s*([^\n\r]+)",
#             "test_method": r"(?:Test Method|Testing Method|Method)\s*:?\s*([^\n\r]+)"
#         }
#
#         # Extract metadata values
#         metadata = {}
#         for key, pattern in metadata_patterns.items():
#             value = extract_value(text, pattern)
#             if value:
#                 metadata[key] = value.strip()
#
#         # Extract environmental conditions with more flexible patterns
#         env_conditions = {}
#
#         # Extract temperature with various formats
#         temp_patterns = [
#             r"Temperature\s*(?:\(°C\))?\s*:?\s*(\d+(?:\.\d+)?)",
#             r"Temp\.?\s*:?\s*(\d+(?:\.\d+)?)\s*°?C?",
#             r"Temperature.*?(\d+)(?:\.\d+)?\s*°?C?"
#         ]
#
#         for pattern in temp_patterns:
#             temp_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#             if temp_match:
#                 env_conditions["temperature"] = temp_match.group(1)
#                 break
#
#         # Extract humidity with various formats
#         humidity_patterns = [
#             r"(?:Relative\s*)?Humidity\s*(?:\(%\))?\s*:?\s*(\d+(?:\.\d+)?)",
#             r"RH\s*:?\s*(\d+(?:\.\d+)?)\s*%?",
#             r"Humidity.*?(\d+)(?:\.\d+)?\s*%?"
#         ]
#
#         for pattern in humidity_patterns:
#             humidity_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#             if humidity_match:
#                 env_conditions["humidity"] = humidity_match.group(1)
#                 break
#
#         if env_conditions:
#             metadata["environmental_conditions"] = env_conditions
#
#         # Combine metadata with table data
#         gicv = {
#             **metadata,
#             "ferrous_materials": {
#                 "customer_sample_no": table_data["first_table"]["customer_sample_no"],
#                 "sample_description_size": table_data["first_table"]["sample_description_size"],
#                 "sample_colour_condition": table_data["first_table"]["sample_colour_condition"],
#                 "lab_sample_no": table_data["first_table"]["lab_sample_no"],
#                 "sample_no": table_data["second_table"]["sample_no"],
#                 "average_grain_size": table_data["second_table"]["average_grain_size"],
#                 "depth_of_decarburization": table_data["second_table"]["depth_of_decarburization"],
#                 "case_depth": table_data["second_table"]["case_depth"],
#                 "structure_analysis": {
#                     "micro": table_data["second_table"]["structure_analysis_micro"],
#                     "macro": table_data["second_table"]["structure_analysis_macro"]
#                 }
#             }
#         }
#
#         # Clean up empty values
#         if "ferrous_materials" in gicv:
#             if "structure_analysis" in gicv["ferrous_materials"]:
#                 gicv["ferrous_materials"]["structure_analysis"] = {
#                     k: v for k, v in gicv["ferrous_materials"]["structure_analysis"].items()
#                     if v and v.strip()
#                 }
#                 if not gicv["ferrous_materials"]["structure_analysis"]:
#                     del gicv["ferrous_materials"]["structure_analysis"]
#
#             gicv["ferrous_materials"] = {
#                 k: v for k, v in gicv["ferrous_materials"].items()
#                 if v and (not isinstance(v, str) or v.strip())
#             }
#
#         # Remove any remaining empty values
#         gicv = {k: v for k, v in gicv.items() if v}
#
#         return gicv
#
#     except Exception as e:
#         logger.error(f"Error processing PDF text: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing PDF text: {str(e)}")
#
#
# @router.post("/upload-pdf", summary="Upload Chemical PDF Report",
#              description="Upload and process chemical test report PDF")
# async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
#     """
#     Upload and process a chemical test report PDF file.
#
#     Args:
#         file: PDF file containing chemical test report
#
#     Returns:
#         Dict containing extracted report data
#     """
#     if not file.filename.lower().endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF file.")
#
#     try:
#         contents = await file.read()
#
#         if not contents:
#             raise HTTPException(status_code=400, detail="Empty file uploaded")
#
#         extracted_text = []
#         with pdfplumber.open(io.BytesIO(contents)) as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text()
#                 if text:
#                     extracted_text.append(text)
#
#         if not extracted_text:
#             raise HTTPException(status_code=422, detail="Could not extract text from PDF")
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
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
#
#
# # Include router in app with prefix
# app.include_router(router, prefix="/chemical", tags=["Chemical"])
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("chemical:app", host="localhost", port=10000, reload=True)














from fastapi import FastAPI, File, APIRouter, UploadFile, HTTPException, Depends
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
from models import ChemicalPDF

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create both app and router
app = FastAPI(title="Chemical API Service")
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
    """Cleans extracted text by removing extra spaces and newlines."""
    if not text:
        return ""
    return " ".join(text.replace("\n", " ").split()).strip()


def extract_value(text: str, pattern: str, default: str = "") -> str:
    """Extracts values based on a regex pattern."""
    try:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return clean_text(match.group(1)) if match else default
    except Exception:
        return default


def extract_customer_info(text: str) -> str:
    """Extracts customer name and address dynamically."""
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


def extract_table_values(text: str) -> Dict[str, Any]:
    """Extracts values from the ferrous materials table."""
    try:
        # Split text into lines for processing
        lines = text.split('\n')

        # Initialize results dictionary
        results = {
            "first_table": {
                "customer_sample_no": "",
                "sample_description_size": "",
                "sample_colour_condition": "",
                "lab_sample_no": ""
            },
            "second_table": {
                "sample_no": "",
                "average_grain_size": "",
                "depth_of_decarburization": "",
                "case_depth": "",
                "structure_analysis_micro": "",
                "structure_analysis_macro": ""
            }
        }

        # Process each line to find table values
        for i, line in enumerate(lines):
            # Look for numeric values in lines
            numbers = re.findall(r'\b\d+\b', line)

            # If we find a line with exactly 4 numbers, it might be the first table
            if len(numbers) == 4:
                # Verify it's not a header line
                if not any(header in line.lower() for header in ["customer", "sample", "description", "lab"]):
                    results["first_table"].update({
                        "customer_sample_no": numbers[0],
                        "sample_description_size": numbers[1],
                        "sample_colour_condition": numbers[2],
                        "lab_sample_no": numbers[3]
                    })

            # If we find a line with exactly 6 numbers, it might be the second table
            elif len(numbers) == 6:
                # Verify it's not a header line
                if not any(header in line.lower() for header in ["structure", "analysis", "micro", "macro"]):
                    results["second_table"].update({
                        "sample_no": numbers[0],
                        "average_grain_size": numbers[1],
                        "depth_of_decarburization": numbers[2],
                        "case_depth": numbers[3],
                        "structure_analysis_micro": numbers[4],
                        "structure_analysis_macro": numbers[5]
                    })

        return results
    except Exception as e:
        logger.error(f"Error extracting table values: {str(e)}")
        return {"first_table": {}, "second_table": {}}


def process_pdf_text(text: str) -> Dict[str, Any]:
    """Processes the extracted text from the PDF and structures it in a dictionary."""
    try:
        # Extract table values
        table_data = extract_table_values(text)

        # Extract metadata using more flexible patterns
        metadata_patterns = {
            "report_number": r"(?:Report|Certificate|Test Report)\s*No\.?\s*:?\s*([^\n\r]+)",
            "name_and_address": r"Name and [Aa]ddress of [Cc]ustomer\s*:?\s*([^\n\r]+)",
            "forwarding_letter": r"(?:Sample Forwarding Letter|Reference)\s*(?:No\.?)?\s*(?:&|and)?\s*Date\s*:?\s*([^\n\r]+)",
            "specification": r"(?:Specification|Grade|Standard)\s*/?(?:Grade)?\s*:?\s*([^\n\r]+)",
            "receipt_date": r"(?:Date of Receipt|Receipt Date)\s*(?:of sample)?\s*:?\s*([^\n\r]+)",
            "test_date": r"(?:Test Performed|Testing Date|Test Date)\s*(?:on)?\s*:?\s*([^\n\r]+)",
            "test_method": r"(?:Test Method|Testing Method|Method)\s*:?\s*([^\n\r]+)"
        }

        # Extract metadata values
        metadata = {}
        for key, pattern in metadata_patterns.items():
            value = extract_value(text, pattern)
            if value:
                metadata[key] = value.strip()

        # Extract environmental conditions with more flexible patterns
        env_conditions = {}

        # Extract temperature with various formats
        temp_patterns = [
            r"Temperature\s*(?:\(°C\))?\s*:?\s*(\d+(?:\.\d+)?)",
            r"Temp\.?\s*:?\s*(\d+(?:\.\d+)?)\s*°?C?",
            r"Temperature.*?(\d+)(?:\.\d+)?\s*°?C?"
        ]

        for pattern in temp_patterns:
            temp_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if temp_match:
                env_conditions["temperature"] = temp_match.group(1)
                break

        # Extract humidity with various formats
        humidity_patterns = [
            r"(?:Relative\s*)?Humidity\s*(?:\(%\))?\s*:?\s*(\d+(?:\.\d+)?)",
            r"RH\s*:?\s*(\d+(?:\.\d+)?)\s*%?",
            r"Humidity.*?(\d+)(?:\.\d+)?\s*%?"
        ]

        for pattern in humidity_patterns:
            humidity_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if humidity_match:
                env_conditions["humidity"] = humidity_match.group(1)
                break

        if env_conditions:
            metadata["environmental_conditions"] = env_conditions

        # Combine metadata with table data
        gicv = {
            **metadata,
            "ferrous_materials": {
                "customer_sample_no": table_data["first_table"]["customer_sample_no"],
                "sample_description_size": table_data["first_table"]["sample_description_size"],
                "sample_colour_condition": table_data["first_table"]["sample_colour_condition"],
                "lab_sample_no": table_data["first_table"]["lab_sample_no"],
                "sample_no": table_data["second_table"]["sample_no"],
                "average_grain_size": table_data["second_table"]["average_grain_size"],
                "depth_of_decarburization": table_data["second_table"]["depth_of_decarburization"],
                "case_depth": table_data["second_table"]["case_depth"],
                "structure_analysis": {
                    "micro": table_data["second_table"]["structure_analysis_micro"],
                    "macro": table_data["second_table"]["structure_analysis_macro"]
                }
            }
        }

        # Clean up empty values
        if "ferrous_materials" in gicv:
            if "structure_analysis" in gicv["ferrous_materials"]:
                gicv["ferrous_materials"]["structure_analysis"] = {
                    k: v for k, v in gicv["ferrous_materials"]["structure_analysis"].items()
                    if v and v.strip()
                }
                if not gicv["ferrous_materials"]["structure_analysis"]:
                    del gicv["ferrous_materials"]["structure_analysis"]

            gicv["ferrous_materials"] = {
                k: v for k, v in gicv["ferrous_materials"].items()
                if v and (not isinstance(v, str) or v.strip())
            }

        # Remove any remaining empty values
        gicv = {k: v for k, v in gicv.items() if v}

        return gicv

    except Exception as e:
        logger.error(f"Error processing PDF text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF text: {str(e)}")


def save_pdf_to_db(db: Session, filename: str) -> ChemicalPDF:
    """Save PDF file information to database"""
    try:
        pdf_record = ChemicalPDF(
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


@router.post("/upload-pdf", summary="Upload Chemical PDF Report")
async def upload_pdf(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and process a chemical test report PDF file.
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
        pdfs = db.query(ChemicalPDF).all()
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
        pdf = db.query(ChemicalPDF).filter(ChemicalPDF.id == pdf_id).first()
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
        pdf = db.query(ChemicalPDF).filter(ChemicalPDF.id == pdf_id).first()
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
        pdf = db.query(ChemicalPDF).filter(ChemicalPDF.id == pdf_id).first()
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
app.include_router(router, prefix="/chemical", tags=["Chemical"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("chemical:app", host="localhost", port=10000, reload=True)