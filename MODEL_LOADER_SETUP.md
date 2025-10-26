# Model Loader Security Setup

## Overview
This system allows you to keep sensitive model loading code (`model_loader.py`) secure by storing it on Google Drive instead of in your GitHub repository. The backend will automatically download it when needed.

## Why?
- **Security**: Keep proprietary model architecture and loading logic private
- **Flexibility**: Update model loading code without committing to repository
- **Clean Repository**: Sensitive code stays out of version control

## Setup Instructions

### Step 1: Upload model_loader.py to Google Drive

1. **Upload the file**:
   - Go to [Google Drive](https://drive.google.com)
   - Upload `backend/model_loader.py`

2. **Make it publicly accessible**:
   - Right-click the uploaded file
   - Click "Share"
   - Change from "Restricted" to **"Anyone with the link"**
   - Copy the share link (e.g., `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`)

### Step 2: Configure the URL

**Option A: Using the helper script (Recommended)**
```bash
cd backend
python setup_model_loader_url.py
# Follow the interactive prompts
```

**Option B: Manual configuration**
```bash
# Edit backend/.env and add:
MODEL_LOADER_URL="https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
```

### Step 3: Remove local model_loader.py

```bash
# Remove the local file (it will be downloaded automatically)
rm backend/model_loader.py
```

### Step 4: Restart the Backend

```bash
cd backend
uvicorn app:app --reload
```

The backend will automatically:
1. Check if `model_loader.py` exists locally
2. If not, download it from Google Drive using the URL in `.env`
3. Import and use it normally

## How It Works

### File Structure
```
backend/
├── app.py                          # Main FastAPI app (checks for model_loader.py)
├── download_code.py                # Handles downloading model_loader.py
├── model_loader.py                 # (Downloaded from Google Drive, gitignored)
├── setup_model_loader_url.py      # Helper script to configure .env
└── .env                            # Contains MODEL_LOADER_URL (gitignored)
```

### Startup Flow
1. `app.py` runs `ensure_model_loader_exists()` from `download_code.py`
2. If `model_loader.py` exists locally → Use it
3. If not → Download from `MODEL_LOADER_URL` in `.env`
4. Import `model_loader.py` and start the application

## Troubleshooting

### Error: "model_loader.py is required but not available"
**Solution**: 
- Make sure `MODEL_LOADER_URL` is set in `backend/.env`
- Verify the Google Drive link is publicly accessible
- Run `python setup_model_loader_url.py` to configure it

### Error: "gdown library not found"
**Solution**:
```bash
pip install gdown
```

### Download fails or file is 0 bytes
**Solution**:
- Check that the file permissions are set to "Anyone with the link"
- Verify the URL is correct
- Try downloading manually from the link to test

### Model_loader.py exists but is outdated
**Solution**:
```bash
# Remove local file to force re-download
rm backend/model_loader.py
# Restart backend
uvicorn app:app --reload
```

## Security Notes

- ✅ `.gitignore` excludes `model_loader.py` (won't be committed)
- ✅ `.gitignore` excludes `.env` (won't expose your Google Drive URL)
- ✅ `.env.example` provides template without sensitive data
- ⚠️ Make sure your Google Drive file is only shared with "Anyone with the link", not "Anyone on the internet"

## Deployment (Render/Railway)

When deploying to production:

1. **Set environment variable**:
   ```
   MODEL_LOADER_URL=https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing
   ```

2. **Ensure gdown is installed**:
   - Add `gdown==5.2.0` to `requirements.txt` (already included)

3. **The platform will automatically**:
   - Download `model_loader.py` on first startup
   - Cache it for subsequent requests
   - Re-download if the file is missing

## Testing

Test the download functionality:
```bash
cd backend
python download_code.py
```

Expected output:
```
============================================================
MODEL_LOADER.PY DOWNLOAD UTILITY
============================================================
⚠️  ./model_loader.py not found locally.
   Attempting to download from configured URL...
📥 Downloading model_loader.py from Google Drive...
   Using gdown to download file ID: YOUR_FILE_ID
✅ Download completed successfully!
✅ Successfully downloaded ./model_loader.py (X,XXX bytes)

✅ SUCCESS: model_loader.py is ready to use!
```

## Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive)
- [gdown Documentation](https://github.com/wkentaro/gdown)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
