from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime
import base64
import tempfile
import shutil
from production import (
    init_production,
    ALLOWED_ORIGINS,
    STATIC_DIR,
    USER_IMAGES_DIR,
    ACCEPTED_DIR,
    REPORTS_DIR,
    DEBUG,
)

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

BASE_DIR = STATIC_DIR.parent
STATIC_DIR_PATH = STATIC_DIR
USER_IMAGES_DIR_PATH = USER_IMAGES_DIR
ACCEPTED_DIR_PATH = ACCEPTED_DIR
REPORTS_DIR_PATH = REPORTS_DIR

app = Flask(__name__, static_folder=str(STATIC_DIR_PATH), static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

cors_origins = set(ALLOWED_ORIGINS)
cors_origins.update({"http://localhost:3000", "http://127.0.0.1:3000"})
CORS(app, origins=list(cors_origins), supports_credentials=True)

# Load the model when the app starts
print("Loading AI model...")
model = load_model()
print("Model loaded successfully!")


def _error(message: str, status_code: int):
    return jsonify({"detail": message}), status_code


@app.route("/predict", methods=["POST"])
def predict():
    file_storage = request.files.get("file")
    if file_storage is None or file_storage.filename == "":
        return _error("No file uploaded.", 400)

    content_type = file_storage.mimetype or ""
    if not content_type.startswith("image/"):
        return _error("Invalid file type. Please upload an image.", 400)

    image_bytes = file_storage.read()

    original_filename = os.path.basename(file_storage.filename or "uploaded.jpg")
    name_root, _ = os.path.splitext(original_filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_filename = f"{name_root}_{timestamp}.jpg"
    output_path = USER_IMAGES_DIR_PATH / output_filename

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        cropped_path = crop_face(tmp_path, output_path=str(output_path), expand_ratio=0.3)
    except ValueError:
        return _error("face is not visible please try again", 400)
    except Exception as exc:
        return _error(f"Cropping failed: {exc}", 500)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    try:
        with open(cropped_path, "rb") as cropped_file:
            cropped_bytes = cropped_file.read()
    except Exception:
        return _error("Failed to read cropped image.", 500)

    cropped_image_data_url = "data:image/jpeg;base64," + base64.b64encode(cropped_bytes).decode("utf-8")

    try:
        prediction = predict_attributes_from_bytes(cropped_bytes)
    finally:
        cleanup_after_prediction()

    if isinstance(prediction, dict) and "error" in prediction:
        return _error(f"Model prediction failed: {prediction['error']}", 500)

    try:
        configure_gemini()
    except Exception as exc:
        return _error(f"Gemini configuration failed: {exc}", 500)

    mapping_path = BASE_DIR / "attribute_mapping.json"
    try:
        feature_descriptions = gemini_load_json_file(str(mapping_path))
    except Exception as exc:
        return _error(f"Failed to load attribute mapping: {exc}", 500)

    summary_text = gemini_generate_summary(prediction)
    content_sections = gemini_generate_content(prediction, feature_descriptions)

    report_filename = f"report_{name_root}_{timestamp}.html"
    report_path = REPORTS_DIR_PATH / report_filename
    try:
        base_url_for_image = request.host_url.rstrip("/")
        absolute_image_url = f"{base_url_for_image}/static/user_images/{output_filename}"
        html = gemini_generate_html_report(
            data=prediction,
            summary=summary_text,
            content=content_sections,
            image_path=absolute_image_url,
        )
        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write(html)
    except Exception as exc:
        return _error(f"Failed to generate HTML report: {exc}", 500)

    base_url = request.host_url.rstrip("/")
    report_url = f"{base_url}/static/reports/{report_filename}"
    cropped_image_url = f"{base_url}/static/user_images/{output_filename}"

    return jsonify({
        "success": True,
        "prediction": prediction,
        "summary": summary_text,
        "skincare_recommendations": content_sections.get("skincare_list", []),
        "grooming_recommendations": content_sections.get("grooming_list", []),
        "grouped_attributes": None,
        "report_url": report_url,
        "cropped_image": cropped_image_data_url,
        "cropped_image_url": cropped_image_url,
        "cropped_image_filename": output_filename,
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "Lumera AI Facial Analysis API is running"})


@app.route("/consent", methods=["POST"])
def consent():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename")
    if not filename or not isinstance(filename, str):
        return _error("filename is required", 400)

    safe_name = os.path.basename(filename)
    src_path = USER_IMAGES_DIR_PATH / safe_name
    if not src_path.exists():
        return _error("Source image not found", 404)

    dst_path = ACCEPTED_DIR_PATH / safe_name
    try:
        shutil.copy2(src_path, dst_path)
    except Exception as exc:
        return _error(f"Failed to record consent: {exc}", 500)

    base_url = request.host_url.rstrip("/")
    return jsonify({"success": True, "accepted_image_url": f"{base_url}/static/accepted/{safe_name}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)
