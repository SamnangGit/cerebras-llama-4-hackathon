from fastapi import APIRouter, Query, HTTPException
from controllers.ocr_controller import OCRController
from utils.db_ops import DBOps
from agents.model import GenerativeModel


router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])

@router.get("/")
async def ocr():
    """
    Endpoint to perform OCR on a specific image.
    Returns the extracted text from the image.
    """
    try:
        ocr_controller = OCRController()
        image_path = "/Users/samnangpheng/Desktop/SINET/ocr_telegram/app/public/uploads/5.jpg"
        
        result = ocr_controller.extract_and_save_fuel_transaction(image_path)
        return {"text": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/html")
async def get_html():
    try:
        ocr_controller = OCRController()
        result = ocr_controller.retrive_and_generate_html_file(sql_prompt="I want to get the total amount of fuel based on vehicle plate number", html_prompt="Based on this data, generate a html page for me to visualize it as bar chart")
        return {"html": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))