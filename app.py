from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from fastapi import Request
import io
import os
import datetime
from production import init_production, ALLOWED_ORIGINS, STATIC_DIR, USER_IMAGES_DIR, ACCEPTED_DIR, REPORTS_DIR

# Initialize production settings
init_production()

# Import memory optimization
from memory_optimization import optimize_memory, cleanup_after_prediction

# Apply memory optimizations
optimize_memory()

# CRITICAL: Ensure model_loader.py is available before importing
# This allows storing sensitive model code in Google Drive instead of GitHub
import sys
from download_code import ensure_model_loader_exists

if not ensure_model_loader_exists():
    print("❌ CRITICAL: model_loader.py is required but not available")
    print("   Please configure MODEL_LOADER_URL in backend/.env")
    sys.exit(1)

from model_loader import predict_attributes_from_bytes, load_model
from Gemini import (
    configure_gemini,
    generate_summary as gemini_generate_summary,
    generate_content as gemini_generate_content,
    generate_html_report as gemini_generate_html_report,
    load_json_file as gemini_load_json_file,
)
from temp import crop_face
import base64
import numpy as np
import cv2
import tempfile
import shutil

app = FastAPI()
# Mount static files for serving saved images
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
USER_IMAGES_DIR = os.path.join(STATIC_DIR, "user_images")
ACCEPTED_DIR = os.path.join(STATIC_DIR, "accepted")
REPORTS_DIR = os.path.join(STATIC_DIR, "reports")
os.makedirs(USER_IMAGES_DIR, exist_ok=True)
os.makedirs(ACCEPTED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load the model when the app starts
print("Loading AI model...")
model = load_model()
print("Model loaded successfully!")

# CORS configuration
origins = [
    "http://localhost:3000",  # React app default port
    "http://localhost:8000",  # FastAPI default port
    "http://127.0.0.1:3000",  # Allow loopback host as well
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    # Read image bytes
    image_bytes = await file.read()

    # Step 0: Save upload to a temp file and crop using temp.crop_face()
    original_filename = os.path.basename(file.filename or "uploaded.jpg")
    name_root, _ = os.path.splitext(original_filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_filename = f"{name_root}_{timestamp}.jpg"
    output_path = os.path.join(USER_IMAGES_DIR, output_filename)

    # Write uploaded bytes to a temporary file path for the cropper
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        # Use the required cropper; this may raise ValueError if no face visible
        cropped_path = crop_face(tmp_path, output_path=output_path, expand_ratio=0.3)
    except ValueError:
        # Specific message required by product
        raise HTTPException(status_code=400, detail="face is not visible please try again")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cropping failed: {str(e)}")
    finally:
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    # Read cropped image bytes
    try:
        with open(cropped_path, "rb") as f:
            cropped_bytes = f.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read cropped image.")

    image_bytes = cropped_bytes
    cropped_image_data_url = "data:image/jpeg;base64," + base64.b64encode(cropped_bytes).decode("utf-8")
    
    try:
        # Step 1: Get model predictions
        prediction = predict_attributes_from_bytes(image_bytes)
        # Clean up memory after prediction
        cleanup_after_prediction()
        
        if "error" in prediction:
            raise HTTPException(status_code=500, detail=f"Model prediction failed: {prediction['error']}")

        # Step 2: Generate summary and content using Gemini + attribute mapping
        try:
            configure_gemini()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini configuration failed: {str(e)}")

        mapping_path = os.path.join(BASE_DIR, "attribute_mapping.json")
        try:
            feature_descriptions = gemini_load_json_file(mapping_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load attribute mapping: {str(e)}")

        summary_text = gemini_generate_summary(prediction)
        content_sections = gemini_generate_content(prediction, feature_descriptions)

        # Step 3: Generate HTML report and save under static/reports
        report_filename = f"report_{name_root}_{timestamp}.html"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        try:
            # Build absolute image URL for HTML
            base_url_for_image = str(request.base_url).rstrip('/')
            absolute_image_url = f"{base_url_for_image}/static/user_images/{output_filename}"
            html = gemini_generate_html_report(
                data=prediction,
                summary=summary_text,
                content=content_sections,
                image_path=absolute_image_url,
            )
            with open(report_path, "w", encoding="utf-8") as rf:
                rf.write(html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate HTML report: {str(e)}")

        # Build absolute URLs for frontend use
        base_url = str(request.base_url).rstrip('/')
        report_url = f"{base_url}/static/reports/{report_filename}"
        cropped_image_url = f"{base_url}/static/user_images/{output_filename}"

        # Return comprehensive analysis
        return JSONResponse(content={
            "success": True,
            "prediction": prediction,
            "summary": summary_text,
            "skincare_recommendations": content_sections.get("skincare_list", []),
            "grooming_recommendations": content_sections.get("grooming_list", []),
            "grouped_attributes": None,
            "report_url": report_url,
            "cropped_image": cropped_image_data_url,
            "cropped_image_url": cropped_image_url,
            "cropped_image_filename": output_filename
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

## Removed legacy PDF report endpoint

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Lumera AI Facial Analysis API is running"}

@app.post("/consent")
async def consent(request: Request, data: dict = Body(...)):
    """
    Records user consent by moving the cropped image to the accepted folder.
    Expects JSON body: { "filename": "<cropped_filename>.jpg" }
    """
    filename = data.get("filename")
    if not filename or not isinstance(filename, str):
        raise HTTPException(status_code=400, detail="filename is required")

    src_path = os.path.join(USER_IMAGES_DIR, os.path.basename(filename))
    if not os.path.exists(src_path):
        raise HTTPException(status_code=404, detail="Source image not found")

    dst_path = os.path.join(ACCEPTED_DIR, os.path.basename(filename))
    try:
        # Copy image from user_images to accepted (retain original for report)
        shutil.copy2(src_path, dst_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record consent: {str(e)}")

    base_url = str(request.base_url).rstrip('/')
    return {"success": True, "accepted_image_url": f"{base_url}/static/accepted/{os.path.basename(filename)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
