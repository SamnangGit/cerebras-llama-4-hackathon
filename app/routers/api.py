from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from controllers.analysis_controller import AnalysisController
from utils.db_ops import DBOps
from agents.model import GenerativeModel

# Response Models
# Router Definition
router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis"])

@router.post("/extract")
async def extract_transaction(request: Request):
    try:
        # Get request body
        image_info = await request.json()
        
        # Validate required fields
        if not image_info.get("image_path"):
            raise HTTPException(
                status_code=400,
                detail="image_path is required in request body"
            )
            
        if not image_info.get("user_full_name"):
            raise HTTPException(
                status_code=400,
                detail="user_full_name is required in request body"
            )
            
        # Validate image path exists and is a string
        if not isinstance(image_info["image_path"], str):
            raise HTTPException(
                status_code=400,
                detail="image_path must be a string"
            )
            
        # Validate user_full_name is a string
        if not isinstance(image_info["user_full_name"], str):
            raise HTTPException(
                status_code=400,
                detail="user_full_name must be a string"
            )
            
        # Process extraction
        controller = AnalysisController()
        result = controller.extract_and_save_fuel_transaction(
            image_path=image_info["image_path"],
            image_info={"user_full_name": image_info["user_full_name"]}
        )
        
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract transaction: {str(e)}"
        )

@router.post("/analyse")
async def analyse_transaction(request: Request):
    # try:
    data = await request.json()
    # validate sql_prompt and chart_type
    if not data.get("sql_prompt") or not data.get("chart_type"):
        raise HTTPException(
            status_code=400,
            detail="sql_prompt and chart_type are required in request body"
        )
    
    sql_prompt = data.get("sql_prompt")
    chart_type = data.get("chart_type")
    
    controller = AnalysisController()
    html_prompt = f"Visualize the data as Based on this data, generate a html page for me to visualize it. {chart_type} chart"
    file_path, explanation = controller.retrive_and_generate_html_file(sql_prompt, html_prompt)
    
    return {
        "file_path": file_path,
        "explanation": explanation,
        "status": "success"
    }
    
    # except HTTPException as he:
    #     raise he
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Failed to analyse transaction: {str(e)}"
    #     )