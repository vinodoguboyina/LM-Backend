# from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from collections import OrderedDict
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
# app = FastAPI(title="Radiology PDF Data Extractor API")
# router = APIRouter()
#
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
#         pattern = r"Name and address of customer\s*(.*?)(?=Sample Forwarding|$)"
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#         return clean_text(match.group(1)) if match else ""
#     except Exception:
#         return ""
#
# def extract_sample_details(text: str) -> Dict[str, str]:
#     try:
#         # Pattern to match the sample details table after the headers
#         pattern = r"Customer\s*Sample\s*Sample\s*Sample\s*Colou?r\s*/\s*Lab\s*Sample\s*No\.\s*Description/Size\s*Condition\s*No\.\s*(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)"
#
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
#
#         if match:
#             return {
#                 "Customer_Sample_No": match.group(1),
#                 "Sample_Description_Size": match.group(2),
#                 "Sample_Colour_Condition": match.group(3),
#                 "Lab_Sample_No": match.group(4)
#             }
#
#         # Fallback pattern for different format
#         fallback_pattern = r"(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)"
#         sections = text.split("Customer Sample")
#         if len(sections) > 1:
#             match = re.search(fallback_pattern, sections[1])
#             if match:
#                 return {
#                     "Customer_Sample_No": match.group(1),
#                     "Sample_Description_Size": match.group(2),
#                     "Sample_Colour_Condition": match.group(3),
#                     "Lab_Sample_No": match.group(4)
#                 }
#
#         return {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": ""
#         }
#     except Exception as e:
#         logger.error(f"Error extracting sample details: {str(e)}")
#         return {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": ""
#         }
#
#
# def extract_test_parameters(text: str) -> Dict[str, Any]:
#     try:
#         # Define patterns in the exact order they should appear (01 to 12)
#         parameters = OrderedDict([
#             ("01_No_of_Samples", {
#                 "pattern": r"(?:01\.?\s*)?No\.\s*of\s*Samples\s*(\d+(?:\.\d+)?)",
#                 "key": "No_of_Samples",
#                 "order": 1
#             }),
#             ("02_No_of_Exposures", {
#                 "pattern": r"(?:02\s*)?No\.\s*of\s*Exposures\s*(\d+(?:\.\d+)?)",
#                 "key": "No_of_Exposures",
#                 "order": 2
#             }),
#             ("03_Thickness", {
#                 "pattern": r"(?:03\s*)?Thickness\s*(\d+(?:\.\d+)?|\.\d+)",
#                 "key": "Thickness",
#                 "order": 3
#             }),
#             ("04_Test_Method_Technique", {
#                 "pattern": r"(?:04\.?\s*)?Test\s*Method\s*(?:&|and|\+)?\s*Technique\s*[\s:]*(\d+(?:\.\d+)?)",
#                 "key": "Test_Method_Technique",
#                 "order": 4
#             }),
#             ("05_Current_mA", {
#                 "pattern": r"(?:05\.?\s*)?Current,?\s*mA\s*(\d+(?:\.\d+)?)",
#                 "key": "Current_mA",
#                 "order": 5
#             }),
#             ("06_Source", {
#                 "pattern": r"(?:06\.?\s*)?Source\s*(\d+(?:\.\d+)?)",
#                 "key": "Source",
#                 "order": 6
#             }),
#             ("07_Penetrameter_used", {
#                 "pattern": r"(?:07\.?\s*)?Penetrameter\s*\(?s?\)?\s*used\s*(\d+(?:\.\d+)?)",
#                 "key": "Penetrameter_used",
#                 "order": 7
#             }),
#             ("08_Voltage_KV", {
#                 "pattern": r"(?:08\.?\s*)?Voltage,?\s*KV\s*(\d+(?:\.\d+)?)",
#                 "key": "Voltage_KV",
#                 "order": 8
#             }),
#             ("09_Sensitivity", {
#                 "pattern": r"(?:09\.?\s*)?Sensitivity\s*(\d+(?:\.\d+)?)",
#                 "key": "Sensitivity",
#                 "order": 9
#             }),
#             ("10_Casting_process", {
#                 "pattern": r"(?:10\.?\s*)?(?:Type\s*of\s*)?Casting/Casting\s*process\s*(\d+(?:\.\d+)?)",
#                 "key": "Casting_process",
#                 "order": 10
#             }),
#             ("11_SFPD", {
#                 "pattern": r"(?:11\.?\s*)?SFPD\s*(\d+(?:\.\d+)?)",
#                 "key": "SFPD",
#                 "order": 11
#             }),
#             ("12_Acceptance_std", {
#                 "pattern": r"(?:12\.?\s*)?Acceptance\s*std\.\s*(\d+(?:\.\d+)?)",
#                 "key": "Acceptance_std",
#                 "order": 12
#             })
#         ])
#
#         # Initialize result dictionary
#         extracted_values = {}
#
#         # Try to match using table format first
#         table_pattern = r"(\d+)[\s.]*([^0-9\n]+?)[\s.]*(\d+(?:\.\d+)?)"
#         table_matches = re.finditer(table_pattern, text, re.MULTILINE)
#
#         for match in table_matches:
#             sno = match.group(1)
#             param_name = match.group(2).strip()
#             value = match.group(3)
#
#             # Find corresponding parameter
#             for param_key, param_data in parameters.items():
#                 if sno == param_key[:2]:  # Match the number prefix (01, 02, etc.)
#                     try:
#                         extracted_values[param_data["key"]] = float(value) if '.' in value else int(value)
#                     except ValueError:
#                         extracted_values[param_data["key"]] = value
#                     break
#
#         # Then try specific patterns for any missing values
#         for _, param in parameters.items():
#             if param["key"] not in extracted_values:
#                 match = re.search(param["pattern"], text, re.IGNORECASE | re.MULTILINE)
#                 if match:
#                     value = match.group(1).strip()
#                     try:
#                         extracted_values[param["key"]] = float(value) if '.' in value else int(value)
#                     except ValueError:
#                         extracted_values[param["key"]] = value
#
#         # Create final ordered result
#         result = OrderedDict()
#         for _, param in sorted(parameters.items(), key=lambda x: x[1]["order"]):
#             if param["key"] in extracted_values:
#                 result[param["key"]] = extracted_values[param["key"]]
#
#         return result
#
#     except Exception as e:
#         logger.error(f"Error extracting test parameters: {str(e)}")
#         return OrderedDict()
#
# def extract_examination_results(text: str) -> list:
#     try:
#         results = []
#         pattern = r"(\d+)\s+(\d+\.?\d*)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
#         matches = re.finditer(pattern, text)
#
#         for match in matches:
#             results.append({
#                 "S_No": match.group(1),
#                 "Sample_No": match.group(2),
#                 "Segment_No": match.group(3),
#                 "Observation": match.group(4),
#                 "Level": match.group(5),
#                 "Remarks": match.group(6)
#             })
#         return results
#     except Exception as e:
#         logger.error(f"Error extracting examination results: {str(e)}")
#         return []
#
#
# def extract_forwarding_letter(text: str) -> str:
#     try:
#         # Multiple patterns to handle different formats
#         patterns = [
#             # Pattern for number and date with comma (96,19-02-2025)
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+,\d{2}-\d{2}-\d{4})",
#             # Pattern for number and date with & (96&19-02-2025)
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+&\d{2}-\d{2}-\d{4})",
#             # Pattern for only date (19-02-2025)
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d{2}-\d{2}-\d{4})",
#             # Pattern for 2-digit year formats
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+[,&]\d{2}-\d{2}-\d{2})",
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d{2}-\d{2}-\d{2})"
#         ]
#
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#             if match:
#                 value = match.group(1)
#
#                 # Convert 2-digit year to 4-digit year if needed
#                 if '-20' not in value:
#                     if ',' in value or '&' in value:
#                         # Handle number and date format
#                         parts = re.split('[,&]', value)
#                         if len(parts) == 2:
#                             number, date = parts
#                             date_parts = date.split('-')
#                             if len(date_parts) == 3 and len(date_parts[2]) == 2:
#                                 date_parts[2] = '20' + date_parts[2]
#                                 value = f"{number},{date_parts[0]}-{date_parts[1]}-{date_parts[2]}"
#                     else:
#                         # Handle date-only format
#                         date_parts = value.split('-')
#                         if len(date_parts) == 3 and len(date_parts[2]) == 2:
#                             date_parts[2] = '20' + date_parts[2]
#                             value = '-'.join(date_parts)
#                 return value
#
#         return ""
#
#     except Exception as e:
#         logger.error(f"Error extracting forwarding letter: {str(e)}")
#         return ""
#
#
# def process_pdf_text(text: str) -> Dict[str, Any]:
#     try:
#         data = {
#             "format_no": extract_value(text, r"Format\s*No\.\s*(TR/ML/C/06\s*Rev\.\s*01)"),
#             "format_date": extract_value(text, r"Date:\s*(\d{2}\.\d{2}\.\d{4})"),
#             "no": extract_value(text, r"No:\s*(OFMK/ML-\d+/TR/\d+)"),
#             "ulr": extract_value(text, r"ULR\s*(TC\s*\d\s*\d\s*\d\s*\d\s*\d)"),
#             "name_and_address": extract_customer_info(text),
#             "forwarding_letter": extract_forwarding_letter(text),
#             "specification": extract_value(text, r"Specification\s*/\s*Grade\s*([A-Za-z0-9]+)"),
#             "receipt_date": extract_value(text, r"Date of Receipt of sample\s*(\d{2}-\d{2}-(?:\d{4}|\d{2}))"),
#             "test_date": extract_value(text, r"Test Performed on\s*(\d{2}-\d{2}-(?:\d{4}|\d{2}))"),
#             "test_method": extract_value(text, r"Test Method\s*(.*?)(?=I\.|$)"),
#             "sample_details": extract_sample_details(text),
#             "test_parameters": extract_test_parameters(text),
#             "examination_results": extract_examination_results(text)
#         }
#
#         # Convert 2-digit years to 4-digit years for dates
#         for key in ['receipt_date', 'test_date']:
#             if data.get(key):
#                 date_parts = data[key].split('-')
#                 if len(date_parts) == 3 and len(date_parts[2]) == 2:
#                     date_parts[2] = '20' + date_parts[2]
#                     data[key] = '-'.join(date_parts)
#
#         return {k: v for k, v in data.items() if v}
#
#     except Exception as e:
#         logger.error(f"Error processing PDF text: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing PDF text: {str(e)}")
#
#
# @router.post("/upload-pdf")
# async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
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
# app.include_router(router)
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("radiology:app", host="localhost", port=12000, reload=True)












from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from collections import OrderedDict
from datetime import datetime
import pdfplumber
import io
import re
import logging
from typing import Dict, Any, List

# Import database and models
from db import get_db, engine, Base
from models import RadiologyPDF

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Radiology PDF Data Extractor API")
router = APIRouter()

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
        pattern = r"Name and address of customer\s*(.*?)(?=Sample Forwarding|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return clean_text(match.group(1)) if match else ""
    except Exception:
        return ""

def extract_sample_details(text: str) -> Dict[str, str]:
    try:
        # Pattern to match the sample details table after the headers
        pattern = r"Customer\s*Sample\s*Sample\s*Sample\s*Colou?r\s*/\s*Lab\s*Sample\s*No\.\s*Description/Size\s*Condition\s*No\.\s*(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)"

        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)

        if match:
            return {
                "Customer_Sample_No": match.group(1),
                "Sample_Description_Size": match.group(2),
                "Sample_Colour_Condition": match.group(3),
                "Lab_Sample_No": match.group(4)
            }

        # Fallback pattern for different format
        fallback_pattern = r"(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)"
        sections = text.split("Customer Sample")
        if len(sections) > 1:
            match = re.search(fallback_pattern, sections[1])
            if match:
                return {
                    "Customer_Sample_No": match.group(1),
                    "Sample_Description_Size": match.group(2),
                    "Sample_Colour_Condition": match.group(3),
                    "Lab_Sample_No": match.group(4)
                }

        return {
            "Customer_Sample_No": "",
            "Sample_Description_Size": "",
            "Sample_Colour_Condition": "",
            "Lab_Sample_No": ""
        }
    except Exception as e:
        logger.error(f"Error extracting sample details: {str(e)}")
        return {
            "Customer_Sample_No": "",
            "Sample_Description_Size": "",
            "Sample_Colour_Condition": "",
            "Lab_Sample_No": ""
        }


def extract_test_parameters(text: str) -> Dict[str, Any]:
    try:
        # Define patterns in the exact order they should appear (01 to 12)
        parameters = OrderedDict([
            ("01_No_of_Samples", {
                "pattern": r"(?:01\.?\s*)?No\.\s*of\s*Samples\s*(\d+(?:\.\d+)?)",
                "key": "No_of_Samples",
                "order": 1
            }),
            ("02_No_of_Exposures", {
                "pattern": r"(?:02\s*)?No\.\s*of\s*Exposures\s*(\d+(?:\.\d+)?)",
                "key": "No_of_Exposures",
                "order": 2
            }),
            ("03_Thickness", {
                "pattern": r"(?:03\s*)?Thickness\s*(\d+(?:\.\d+)?|\.\d+)",
                "key": "Thickness",
                "order": 3
            }),
            ("04_Test_Method_Technique", {
                "pattern": r"(?:04\.?\s*)?Test\s*Method\s*(?:&|and|\+)?\s*Technique\s*[\s:]*(\d+(?:\.\d+)?)",
                "key": "Test_Method_Technique",
                "order": 4
            }),
            ("05_Current_mA", {
                "pattern": r"(?:05\.?\s*)?Current,?\s*mA\s*(\d+(?:\.\d+)?)",
                "key": "Current_mA",
                "order": 5
            }),
            ("06_Source", {
                "pattern": r"(?:06\.?\s*)?Source\s*(\d+(?:\.\d+)?)",
                "key": "Source",
                "order": 6
            }),
            ("07_Penetrameter_used", {
                "pattern": r"(?:07\.?\s*)?Penetrameter\s*\(?s?\)?\s*used\s*(\d+(?:\.\d+)?)",
                "key": "Penetrameter_used",
                "order": 7
            }),
            ("08_Voltage_KV", {
                "pattern": r"(?:08\.?\s*)?Voltage,?\s*KV\s*(\d+(?:\.\d+)?)",
                "key": "Voltage_KV",
                "order": 8
            }),
            ("09_Sensitivity", {
                "pattern": r"(?:09\.?\s*)?Sensitivity\s*(\d+(?:\.\d+)?)",
                "key": "Sensitivity",
                "order": 9
            }),
            ("10_Casting_process", {
                "pattern": r"(?:10\.?\s*)?(?:Type\s*of\s*)?Casting/Casting\s*process\s*(\d+(?:\.\d+)?)",
                "key": "Casting_process",
                "order": 10
            }),
            ("11_SFPD", {
                "pattern": r"(?:11\.?\s*)?SFPD\s*(\d+(?:\.\d+)?)",
                "key": "SFPD",
                "order": 11
            }),
            ("12_Acceptance_std", {
                "pattern": r"(?:12\.?\s*)?Acceptance\s*std\.\s*(\d+(?:\.\d+)?)",
                "key": "Acceptance_std",
                "order": 12
            })
        ])

        # Initialize result dictionary
        extracted_values = {}

        # Try to match using table format first
        table_pattern = r"(\d+)[\s.]*([^0-9\n]+?)[\s.]*(\d+(?:\.\d+)?)"
        table_matches = re.finditer(table_pattern, text, re.MULTILINE)

        for match in table_matches:
            sno = match.group(1)
            param_name = match.group(2).strip()
            value = match.group(3)

            # Find corresponding parameter
            for param_key, param_data in parameters.items():
                if sno == param_key[:2]:  # Match the number prefix (01, 02, etc.)
                    try:
                        extracted_values[param_data["key"]] = float(value) if '.' in value else int(value)
                    except ValueError:
                        extracted_values[param_data["key"]] = value
                    break

        # Then try specific patterns for any missing values
        for _, param in parameters.items():
            if param["key"] not in extracted_values:
                match = re.search(param["pattern"], text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    try:
                        extracted_values[param["key"]] = float(value) if '.' in value else int(value)
                    except ValueError:
                        extracted_values[param["key"]] = value

        # Create final ordered result
        result = OrderedDict()
        for _, param in sorted(parameters.items(), key=lambda x: x[1]["order"]):
            if param["key"] in extracted_values:
                result[param["key"]] = extracted_values[param["key"]]

        return result

    except Exception as e:
        logger.error(f"Error extracting test parameters: {str(e)}")
        return OrderedDict()

def extract_examination_results(text: str) -> list:
    try:
        results = []
        pattern = r"(\d+)\s+(\d+\.?\d*)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
        matches = re.finditer(pattern, text)

        for match in matches:
            results.append({
                "S_No": match.group(1),
                "Sample_No": match.group(2),
                "Segment_No": match.group(3),
                "Observation": match.group(4),
                "Level": match.group(5),
                "Remarks": match.group(6)
            })
        return results
    except Exception as e:
        logger.error(f"Error extracting examination results: {str(e)}")
        return []


def extract_forwarding_letter(text: str) -> str:
    try:
        # Multiple patterns to handle different formats
        patterns = [
            # Pattern for number and date with comma (96,19-02-2025)
            r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+,\d{2}-\d{2}-\d{4})",
            # Pattern for number and date with & (96&19-02-2025)
            r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+&\d{2}-\d{2}-\d{4})",
            # Pattern for only date (19-02-2025)
            r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d{2}-\d{2}-\d{4})",
            # Pattern for 2-digit year formats
            r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+[,&]\d{2}-\d{2}-\d{2})",
            r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d{2}-\d{2}-\d{2})"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1)

                # Convert 2-digit year to 4-digit year if needed
                if '-20' not in value:
                    if ',' in value or '&' in value:
                        # Handle number and date format
                        parts = re.split('[,&]', value)
                        if len(parts) == 2:
                            number, date = parts
                            date_parts = date.split('-')
                            if len(date_parts) == 3 and len(date_parts[2]) == 2:
                                date_parts[2] = '20' + date_parts[2]
                                value = f"{number},{date_parts[0]}-{date_parts[1]}-{date_parts[2]}"
                    else:
                        # Handle date-only format
                        date_parts = value.split('-')
                        if len(date_parts) == 3 and len(date_parts[2]) == 2:
                            date_parts[2] = '20' + date_parts[2]
                            value = '-'.join(date_parts)
                return value

        return ""

    except Exception as e:
        logger.error(f"Error extracting forwarding letter: {str(e)}")
        return ""


def process_pdf_text(text: str) -> Dict[str, Any]:
    try:
        data = {
            "format_no": extract_value(text, r"Format\s*No\.\s*(TR/ML/C/06\s*Rev\.\s*01)"),
            "format_date": extract_value(text, r"Date:\s*(\d{2}\.\d{2}\.\d{4})"),
            "no": extract_value(text, r"No:\s*(OFMK/ML-\d+/TR/\d+)"),
            "ulr": extract_value(text, r"ULR\s*(TC\s*\d\s*\d\s*\d\s*\d\s*\d)"),
            "name_and_address": extract_customer_info(text),
            "forwarding_letter": extract_forwarding_letter(text),
            "specification": extract_value(text, r"Specification\s*/\s*Grade\s*([A-Za-z0-9]+)"),
            "receipt_date": extract_value(text, r"Date of Receipt of sample\s*(\d{2}-\d{2}-(?:\d{4}|\d{2}))"),
            "test_date": extract_value(text, r"Test Performed on\s*(\d{2}-\d{2}-(?:\d{4}|\d{2}))"),
            "test_method": extract_value(text, r"Test Method\s*(.*?)(?=I\.|$)"),
            "sample_details": extract_sample_details(text),
            "test_parameters": extract_test_parameters(text),
            "examination_results": extract_examination_results(text)
        }

        # Convert 2-digit years to 4-digit years for dates
        for key in ['receipt_date', 'test_date']:
            if data.get(key):
                date_parts = data[key].split('-')
                if len(date_parts) == 3 and len(date_parts[2]) == 2:
                    date_parts[2] = '20' + date_parts[2]
                    data[key] = '-'.join(date_parts)

        return {k: v for k, v in data.items() if v}

    except Exception as e:
        logger.error(f"Error processing PDF text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF text: {str(e)}")


def save_pdf_to_db(db: Session, filename: str) -> RadiologyPDF:
    """Save PDF file information to database"""
    try:
        pdf_record = RadiologyPDF(
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


@router.post("/upload-pdf")
async def upload_pdf(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Upload and process a radiology PDF file"""
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
        pdfs = db.query(RadiologyPDF).all()
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
        pdf = db.query(RadiologyPDF).filter(RadiologyPDF.id == pdf_id).first()
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
        pdf = db.query(RadiologyPDF).filter(RadiologyPDF.id == pdf_id).first()
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
        pdf = db.query(RadiologyPDF).filter(RadiologyPDF.id == pdf_id).first()
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
app.include_router(router, prefix="/radiology", tags=["Radiology"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("radiology:app", host="localhost", port=12000, reload=True)






















# from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException, Depends, Response
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from collections import OrderedDict
# from datetime import datetime
# import pdfplumber
# import io
# import re
# import logging
# from typing import Dict, Any, List
# import uuid
# from minio import Minio
# from minio.error import S3Error
#
# # Import database and models
# from db import get_db, engine, Base
# from models import RadiologyPDF
#
# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# app = FastAPI(title="Radiology PDF Data Extractor API")
# router = APIRouter()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Create tables
# Base.metadata.create_all(bind=engine)
#
# # MinIO client setup
# minio_client = Minio(
#     "minio-server:9000",  # Replace with your MinIO server address
#     access_key="minioadmin",  # Replace with your access key
#     secret_key="minioadmin",  # Replace with your secret key
#     secure=False  # Set to True if you're using HTTPS
# )
#
# # MinIO bucket name
# BUCKET_NAME = "radiology-pdfs"
#
#
# # Ensure bucket exists
# def initialize_minio():
#     try:
#         # Check if the bucket exists, create if it doesn't
#         if not minio_client.bucket_exists(BUCKET_NAME):
#             minio_client.make_bucket(BUCKET_NAME)
#             logger.info(f"Created bucket {BUCKET_NAME}")
#         else:
#             logger.info(f"Bucket {BUCKET_NAME} already exists")
#     except S3Error as e:
#         logger.error(f"Error initializing MinIO: {e}")
#         raise e
#
#
# # Initialize MinIO on startup
# @app.on_event("startup")
# async def startup_event():
#     initialize_minio()
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
#         pattern = r"Name and address of customer\s*(.*?)(?=Sample Forwarding|$)"
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#         return clean_text(match.group(1)) if match else ""
#     except Exception:
#         return ""
#
#
# def extract_sample_details(text: str) -> Dict[str, str]:
#     try:
#         # Pattern to match the sample details table after the headers
#         pattern = r"Customer\s*Sample\s*Sample\s*Sample\s*Colou?r\s*/\s*Lab\s*Sample\s*No\.\s*Description/Size\s*Condition\s*No\.\s*(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)"
#
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
#
#         if match:
#             return {
#                 "Customer_Sample_No": match.group(1),
#                 "Sample_Description_Size": match.group(2),
#                 "Sample_Colour_Condition": match.group(3),
#                 "Lab_Sample_No": match.group(4)
#             }
#
#         # Fallback pattern for different format
#         fallback_pattern = r"(\d+)\s+([\d.]+)\s+(\d+)\s+(\d+)"
#         sections = text.split("Customer Sample")
#         if len(sections) > 1:
#             match = re.search(fallback_pattern, sections[1])
#             if match:
#                 return {
#                     "Customer_Sample_No": match.group(1),
#                     "Sample_Description_Size": match.group(2),
#                     "Sample_Colour_Condition": match.group(3),
#                     "Lab_Sample_No": match.group(4)
#                 }
#
#         return {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": ""
#         }
#     except Exception as e:
#         logger.error(f"Error extracting sample details: {str(e)}")
#         return {
#             "Customer_Sample_No": "",
#             "Sample_Description_Size": "",
#             "Sample_Colour_Condition": "",
#             "Lab_Sample_No": ""
#         }
#
#
# def extract_test_parameters(text: str) -> Dict[str, Any]:
#     try:
#         # Define patterns in the exact order they should appear (01 to 12)
#         parameters = OrderedDict([
#             ("01_No_of_Samples", {
#                 "pattern": r"(?:01\.?\s*)?No\.\s*of\s*Samples\s*(\d+(?:\.\d+)?)",
#                 "key": "No_of_Samples",
#                 "order": 1
#             }),
#             ("02_No_of_Exposures", {
#                 "pattern": r"(?:02\s*)?No\.\s*of\s*Exposures\s*(\d+(?:\.\d+)?)",
#                 "key": "No_of_Exposures",
#                 "order": 2
#             }),
#             ("03_Thickness", {
#                 "pattern": r"(?:03\s*)?Thickness\s*(\d+(?:\.\d+)?|\.\d+)",
#                 "key": "Thickness",
#                 "order": 3
#             }),
#             ("04_Test_Method_Technique", {
#                 "pattern": r"(?:04\.?\s*)?Test\s*Method\s*(?:&|and|\+)?\s*Technique\s*[\s:]*(\d+(?:\.\d+)?)",
#                 "key": "Test_Method_Technique",
#                 "order": 4
#             }),
#             ("05_Current_mA", {
#                 "pattern": r"(?:05\.?\s*)?Current,?\s*mA\s*(\d+(?:\.\d+)?)",
#                 "key": "Current_mA",
#                 "order": 5
#             }),
#             ("06_Source", {
#                 "pattern": r"(?:06\.?\s*)?Source\s*(\d+(?:\.\d+)?)",
#                 "key": "Source",
#                 "order": 6
#             }),
#             ("07_Penetrameter_used", {
#                 "pattern": r"(?:07\.?\s*)?Penetrameter\s*\(?s?\)?\s*used\s*(\d+(?:\.\d+)?)",
#                 "key": "Penetrameter_used",
#                 "order": 7
#             }),
#             ("08_Voltage_KV", {
#                 "pattern": r"(?:08\.?\s*)?Voltage,?\s*KV\s*(\d+(?:\.\d+)?)",
#                 "key": "Voltage_KV",
#                 "order": 8
#             }),
#             ("09_Sensitivity", {
#                 "pattern": r"(?:09\.?\s*)?Sensitivity\s*(\d+(?:\.\d+)?)",
#                 "key": "Sensitivity",
#                 "order": 9
#             }),
#             ("10_Casting_process", {
#                 "pattern": r"(?:10\.?\s*)?(?:Type\s*of\s*)?Casting/Casting\s*process\s*(\d+(?:\.\d+)?)",
#                 "key": "Casting_process",
#                 "order": 10
#             }),
#             ("11_SFPD", {
#                 "pattern": r"(?:11\.?\s*)?SFPD\s*(\d+(?:\.\d+)?)",
#                 "key": "SFPD",
#                 "order": 11
#             }),
#             ("12_Acceptance_std", {
#                 "pattern": r"(?:12\.?\s*)?Acceptance\s*std\.\s*(\d+(?:\.\d+)?)",
#                 "key": "Acceptance_std",
#                 "order": 12
#             })
#         ])
#
#         # Initialize result dictionary
#         extracted_values = {}
#
#         # Try to match using table format first
#         table_pattern = r"(\d+)[\s.]*([^0-9\n]+?)[\s.]*(\d+(?:\.\d+)?)"
#         table_matches = re.finditer(table_pattern, text, re.MULTILINE)
#
#         for match in table_matches:
#             sno = match.group(1)
#             param_name = match.group(2).strip()
#             value = match.group(3)
#
#             # Find corresponding parameter
#             for param_key, param_data in parameters.items():
#                 if sno == param_key[:2]:  # Match the number prefix (01, 02, etc.)
#                     try:
#                         extracted_values[param_data["key"]] = float(value) if '.' in value else int(value)
#                     except ValueError:
#                         extracted_values[param_data["key"]] = value
#                     break
#
#         # Then try specific patterns for any missing values
#         for _, param in parameters.items():
#             if param["key"] not in extracted_values:
#                 match = re.search(param["pattern"], text, re.IGNORECASE | re.MULTILINE)
#                 if match:
#                     value = match.group(1).strip()
#                     try:
#                         extracted_values[param["key"]] = float(value) if '.' in value else int(value)
#                     except ValueError:
#                         extracted_values[param["key"]] = value
#
#         # Create final ordered result
#         result = OrderedDict()
#         for _, param in sorted(parameters.items(), key=lambda x: x[1]["order"]):
#             if param["key"] in extracted_values:
#                 result[param["key"]] = extracted_values[param["key"]]
#
#         return result
#
#     except Exception as e:
#         logger.error(f"Error extracting test parameters: {str(e)}")
#         return OrderedDict()
#
#
# def extract_examination_results(text: str) -> list:
#     try:
#         results = []
#         pattern = r"(\d+)\s+(\d+\.?\d*)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
#         matches = re.finditer(pattern, text)
#
#         for match in matches:
#             results.append({
#                 "S_No": match.group(1),
#                 "Sample_No": match.group(2),
#                 "Segment_No": match.group(3),
#                 "Observation": match.group(4),
#                 "Level": match.group(5),
#                 "Remarks": match.group(6)
#             })
#         return results
#     except Exception as e:
#         logger.error(f"Error extracting examination results: {str(e)}")
#         return []
#
#
# def extract_forwarding_letter(text: str) -> str:
#     try:
#         # Multiple patterns to handle different formats
#         patterns = [
#             # Pattern for number and date with comma (96,19-02-2025)
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+,\d{2}-\d{2}-\d{4})",
#             # Pattern for number and date with & (96&19-02-2025)
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+&\d{2}-\d{2}-\d{4})",
#             # Pattern for only date (19-02-2025)
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d{2}-\d{2}-\d{4})",
#             # Pattern for 2-digit year formats
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d+[,&]\d{2}-\d{2}-\d{2})",
#             r"Sample\s+Forwarding\s+Letter\s+No\.\s*&\s*Date\s*(\d{2}-\d{2}-\d{2})"
#         ]
#
#         for pattern in patterns:
#             match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#             if match:
#                 value = match.group(1)
#
#                 # Convert 2-digit year to 4-digit year if needed
#                 if '-20' not in value:
#                     if ',' in value or '&' in value:
#                         # Handle number and date format
#                         parts = re.split('[,&]', value)
#                         if len(parts) == 2:
#                             number, date = parts
#                             date_parts = date.split('-')
#                             if len(date_parts) == 3 and len(date_parts[2]) == 2:
#                                 date_parts[2] = '20' + date_parts[2]
#                                 value = f"{number},{date_parts[0]}-{date_parts[1]}-{date_parts[2]}"
#                     else:
#                         # Handle date-only format
#                         date_parts = value.split('-')
#                         if len(date_parts) == 3 and len(date_parts[2]) == 2:
#                             date_parts[2] = '20' + date_parts[2]
#                             value = '-'.join(date_parts)
#                 return value
#
#         return ""
#
#     except Exception as e:
#         logger.error(f"Error extracting forwarding letter: {str(e)}")
#         return ""
#
#
# def process_pdf_text(text: str) -> Dict[str, Any]:
#     try:
#         data = {
#             "format_no": extract_value(text, r"Format\s*No\.\s*(TR/ML/C/06\s*Rev\.\s*01)"),
#             "format_date": extract_value(text, r"Date:\s*(\d{2}\.\d{2}\.\d{4})"),
#             "no": extract_value(text, r"No:\s*(OFMK/ML-\d+/TR/\d+)"),
#             "ulr": extract_value(text, r"ULR\s*(TC\s*\d\s*\d\s*\d\s*\d\s*\d)"),
#             "name_and_address": extract_customer_info(text),
#             "forwarding_letter": extract_forwarding_letter(text),
#             "specification": extract_value(text, r"Specification\s*/\s*Grade\s*([A-Za-z0-9]+)"),
#             "receipt_date": extract_value(text, r"Date of Receipt of sample\s*(\d{2}-\d{2}-(?:\d{4}|\d{2}))"),
#             "test_date": extract_value(text, r"Test Performed on\s*(\d{2}-\d{2}-(?:\d{4}|\d{2}))"),
#             "test_method": extract_value(text, r"Test Method\s*(.*?)(?=I\.|$)"),
#             "sample_details": extract_sample_details(text),
#             "test_parameters": extract_test_parameters(text),
#             "examination_results": extract_examination_results(text)
#         }
#
#         # Convert 2-digit years to 4-digit years for dates
#         for key in ['receipt_date', 'test_date']:
#             if data.get(key):
#                 date_parts = data[key].split('-')
#                 if len(date_parts) == 3 and len(date_parts[2]) == 2:
#                     date_parts[2] = '20' + date_parts[2]
#                     data[key] = '-'.join(date_parts)
#
#         return {k: v for k, v in data.items() if v}
#
#     except Exception as e:
#         logger.error(f"Error processing PDF text: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing PDF text: {str(e)}")
#
#
# def save_pdf_to_db(db: Session, filename: str, object_name: str) -> RadiologyPDF:
#     """Save PDF file information to database with MinIO object reference"""
#     try:
#         pdf_record = RadiologyPDF(
#             filename=filename,
#             object_name=object_name,  # Add this field to your RadiologyPDF model
#             updated_time=datetime.now(),
#             updated_date=datetime.now()
#         )
#         db.add(pdf_record)
#         db.commit()
#         db.refresh(pdf_record)
#         return pdf_record
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error saving PDF to database: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error saving PDF to database: {str(e)}"
#         )
#
#
# @router.post("/upload-pdf")
# async def upload_pdf(
#         file: UploadFile = File(...),
#         db: Session = Depends(get_db)
# ) -> Dict[str, Any]:
#     """Upload and process a radiology PDF file"""
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
#         # Generate a unique object name for MinIO
#         object_name = f"{uuid.uuid4()}-{file.filename}"
#
#         # Upload file to MinIO
#         minio_client.put_object(
#             bucket_name=BUCKET_NAME,
#             object_name=object_name,
#             data=io.BytesIO(contents),
#             length=len(contents),
#             content_type="application/pdf"
#         )
#
#         # Save file info to database
#         pdf_record = save_pdf_to_db(db, file.filename, object_name)
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
#         # Add database record info to response
#         report_data["db_record"] = {
#             "id": pdf_record.id,
#             "filename": pdf_record.filename,
#             "object_name": pdf_record.object_name,
#             "updated_time": pdf_record.updated_time.isoformat(),
#             "updated_date": pdf_record.updated_date.isoformat()
#         }
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
#
# @router.get("/pdfs", response_model=List[Dict[str, Any]])
# async def get_all_pdfs(db: Session = Depends(get_db)):
#     """Get all PDF records"""
#     try:
#         pdfs = db.query(RadiologyPDF).all()
#         return [
#             {
#                 "id": pdf.id,
#                 "filename": pdf.filename,
#                 "object_name": pdf.object_name,
#                 "updated_time": pdf.updated_time.isoformat(),
#                 "updated_date": pdf.updated_date.isoformat(),
#                 "download_url": f"/radiology/download/{pdf.id}"
#             }
#             for pdf in pdfs
#         ]
#     except Exception as e:
#         logger.error(f"Error retrieving PDFs: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error retrieving PDFs: {str(e)}"
#         )
#
#
# @router.get("/pdf/{pdf_id}", response_model=Dict[str, Any])
# async def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
#     """Get a specific PDF record by ID"""
#     try:
#         pdf = db.query(RadiologyPDF).filter(RadiologyPDF.id == pdf_id).first()
#         if not pdf:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"PDF with id {pdf_id} not found"
#             )
#         return {
#             "id": pdf.id,
#             "filename": pdf.filename,
#             "object_name": pdf.object_name,
#             "updated_time": pdf.updated_time.isoformat(),
#             "updated_date": pdf.updated_date.isoformat(),
#             "download_url": f"/radiology/download/{pdf_id}"
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error retrieving PDF: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error retrieving PDF: {str(e)}"
#         )
#
#
# @router.get("/download/{pdf_id}")
# async def download_pdf(pdf_id: int, db: Session = Depends(get_db)):
#     """Download a PDF file by ID"""
#     try:
#         pdf = db.query(RadiologyPDF).filter(RadiologyPDF.id == pdf_id).first()
#         if not pdf:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"PDF with id {pdf_id} not found"
#             )
#
#         # Get the file from MinIO
#         try:
#             response = minio_client.get_object(
#                 bucket_name=BUCKET_NAME,
#                 object_name=pdf.object_name
#             )
#
#             # Return the file as a streaming response
#             return StreamingResponse(
#                 response,
#                 media_type="application/pdf",
#                 headers={
#                     "Content-Disposition": f"attachment; filename=\"{pdf.filename}\""
#                 }
#             )
#         except S3Error as e:
#             logger.error(f"MinIO error: {e}")
#             raise HTTPException(
#                 status_code=404,
#                 detail="File not found in storage"
#             )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error downloading PDF: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error downloading PDF: {str(e)}"
#         )
#
#
# @router.put("/pdf/{pdf_id}", response_model=Dict[str, Any])
# async def update_pdf(
#         pdf_id: int,
#         file: UploadFile = File(None),
#         filename: str = None,
#         db: Session = Depends(get_db)
# ):
#     """Update a PDF record and optionally replace the file"""
#     try:
#         pdf = db.query(RadiologyPDF).filter(RadiologyPDF.id == pdf_id).first()
#         if not pdf:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"PDF with id {pdf_id} not found"
#             )
#
#         # Update filename if provided
#         if filename:
#             pdf.filename = filename
#
#         # Update the file in MinIO if provided
#         if file:
#             if not file.filename.lower().endswith('.pdf'):
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Invalid file format. Please upload a PDF file."
#                 )
#
#             contents = await file.read()
#             if not contents:
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Empty file uploaded"
#                 )
#
#             # Generate a new object name
#             new_object_name = f"{uuid.uuid4()}-{file.filename if filename is None else filename}"
#
#             # Upload new file to MinIO
#             minio_client.put_object(
#                 bucket_name=BUCKET_NAME,
#                 object_name=new_object_name,
#                 data=io.BytesIO(contents),
#                 length=len(contents),
#                 content_type="application/pdf"
#             )
#
#             # Delete old file from MinIO
#             try:
#                 minio_client.remove_object(BUCKET_NAME, pdf.object_name)
#             except Exception as e:
#                 logger.warning(f"Could not remove old file from MinIO: {e}")
#
#             # Update object name in database
#             pdf.object_name = new_object_name
#
#         pdf.updated_time = datetime.now()
#         pdf.updated_date = datetime.now()
#
#         db.commit()
#         db.refresh(pdf)
#
#         return {
#             "id": pdf.id,
#             "filename": pdf.filename,
#             "object_name": pdf.object_name,
#             "updated_time": pdf.updated_time.isoformat(),
#             "updated_date": pdf.updated_date.isoformat(),
#             "download_url": f"/radiology/download/{pdf_id}"
#         }
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error updating PDF: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error updating PDF: {str(e)}"
#         )
#
#
# @router.delete("/pdf/{pdf_id}")
# async def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
#     """Delete a PDF record and its file from MinIO"""
#     try:
#         pdf = db.query(RadiologyPDF).filter(RadiologyPDF.id == pdf_id).first()
#         if not pdf:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"PDF with id {pdf_id} not found"
#             )
#
#         # Delete file from MinIO
#         try:
#             minio_client.remove_object(BUCKET_NAME, pdf.object_name)
#         except Exception as e:
#             logger.warning(f"Could not remove file from MinIO: {e}")
#
#         # Delete record from database
#         db.delete(pdf)
#         db.commit()
#
#         return {"message": f"PDF with id {pdf_id} deleted successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error deleting PDF: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error deleting PDF: {str(e)}"
#         )
#
#
# # Include router in app with prefix
# app.include_router(router, prefix="/radiology", tags=["Radiology"])
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("radiology:app", host="localhost", port=12000, reload=True)