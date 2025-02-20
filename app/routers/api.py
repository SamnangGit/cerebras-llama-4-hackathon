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
    try:
        # Get request body
        analysis_info = await request.json()
        
        # Validate required fields
        if not analysis_info.get("sql_prompt"):
            raise HTTPException(
                status_code=400,
                detail="sql_prompt is required in request body"
            )
            
        if not analysis_info.get("html_prompt"):
            raise HTTPException(
                status_code=400,
                detail="html_prompt is required in request body"
            )
            
        # Validate field types
        if not isinstance(analysis_info["sql_prompt"], str):
            raise HTTPException(
                status_code=400,
                detail="sql_prompt must be a string"
            )
            
        if not isinstance(analysis_info["html_prompt"], str):
            raise HTTPException(
                status_code=400,
                detail="html_prompt must be a string"
            )
            
        # Validate chart_type if provided
        if "chart_type" in analysis_info and not isinstance(analysis_info["chart_type"], str):
            raise HTTPException(
                status_code=400,
                detail="chart_type must be a string"
            )
            
        # Process analysis
        controller = AnalysisController()
        
        # Combine chart type with HTML prompt if provided
        html_prompt = analysis_info["html_prompt"]
        if analysis_info.get("chart_type"):
            html_prompt = f"{html_prompt} as a {analysis_info['chart_type']} chart"
            
        file_path, explanation = controller.retrive_and_generate_html_file(
            sql_prompt=analysis_info["sql_prompt"],
            html_prompt=html_prompt
        )
        
        return {
            "file_path": file_path,
            "explanation": explanation,
            "status": "success"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze transaction: {str(e)}"
        )