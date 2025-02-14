from fastapi import APIRouter, Query, HTTPException
from controllers.ocr_controller import OCRController

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])

@router.get("/latest")
async def hello_world() -> str:
    return "Hello World"


@router.get("/")
async def ocr():
    """
    Endpoint to perform OCR on a specific image.
    Returns the extracted text from the image.
    """
    try:
        ocr_controller = OCRController()
        image_path = "/Users/samnangpheng/Desktop/SINET/ocr_telegram/app/uploads/3.jpg"
        result = ocr_controller.ocr_structured_output(image_path)
        return {"text": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


