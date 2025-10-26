# 🚀 Model Deployment Setup

## Problem Solved
This setup allows you to deploy your ML model (>100MB) without storing it in GitHub, by automatically downloading it from Google Drive when the application starts.

## 📋 Setup Instructions

### 1. Upload Your Model to Google Drive

1. Go to [Google Drive](https://drive.google.com)
2. Upload your `convnext_tiny_celeb.pth` file
3. Right-click the file → **Get link** → Set to "Anyone with the link"
4. Copy the share link (looks like: `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`)

### 2. Configure the Download URL

Open `backend/.env` and add/update:

```properties
MODEL_DOWNLOAD_URL="https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
```

**OR** use the setup script:

```bash
cd backend
python setup_model_url.py "YOUR_GOOGLE_DRIVE_LINK"
```

This will automatically update your `.env` file.

### 3. Test Locally (Optional)

You can test the download manually:

```bash
cd backend
python download_model.py
```

This will download the model to `backend/model/convnext_tiny_celeb.pth`.

### 4. Deploy

When you deploy to Render, Railway, or any platform:

1. The app will automatically check if the model exists
2. If not found, it will download from Google Drive on first startup
3. Subsequent runs will use the cached model

## 🔧 How It Works

1. **`download_model.py`**: Utility script that handles Google Drive downloads
2. **`model_loader.py`**: Updated to call `ensure_model_exists()` before loading
3. **On Deployment**: 
   - First run → Downloads model (takes 1-2 minutes)
   - Next runs → Uses cached model (instant)

## 📝 Important Notes

### For GitHub
- The actual `.pth` model file should **NOT** be committed
- It's already in `.gitignore` under `*.pth`
- Only the download script is in the repo

### For Deployment Platforms

**Render.com / Railway.app:**
- Go to your app settings → Environment Variables
- Add: `MODEL_DOWNLOAD_URL` = `your_google_drive_link`
- The model will download on first deployment
- Make sure you have persistent storage enabled

**Docker:**
- Set environment variable: `-e MODEL_DOWNLOAD_URL="your_link"`
- Model downloads on container first run
- Consider using volumes for persistence

## 🔒 Security Options

### Option 1: Public Google Drive Link (Current)
- ✅ Easy to set up
- ⚠️ Anyone with link can download
- 👍 Good for non-sensitive models

### Option 2: Private Google Drive + Service Account
If your model is sensitive:
1. Keep Google Drive file private
2. Use a service account with credentials
3. Update `download_model.py` to use Google Drive API with auth

### Option 3: Cloud Storage
- AWS S3 (private bucket)
- Google Cloud Storage
- Azure Blob Storage

## 🛠️ Troubleshooting

**Model not downloading?**
- Check the Google Drive link is public
- Verify the URL in `download_model.py`
- Check deployment logs for error messages

**File size too large for Google Drive?**
- Google Drive free: 15 GB limit (plenty for most models)
- Consider splitting very large models
- Or use AWS S3 / GCS instead

## 📊 File Structure

```
backend/
├── download_model.py          # 🆕 Model download utility
├── model_loader.py            # ✏️ Updated to auto-download
├── model/                     # Created automatically
│   └── convnext_tiny_celeb.pth  # Downloaded on first run
├── .env                       # API keys (git-ignored)
└── requirements.txt           # Add 'requests' if not present
```

## ✅ Checklist

- [ ] Model uploaded to Google Drive
- [ ] Google Drive link set to "Anyone with the link can view"
- [ ] `GOOGLE_DRIVE_MODEL_URL` updated in `download_model.py`
- [ ] `requests` library in `requirements.txt`
- [ ] Model file (`*.pth`) in `.gitignore`
- [ ] Tested locally with `python download_model.py`
- [ ] Ready to deploy! 🚀

---

**Need help?** Check the deployment logs or run `python download_model.py` locally to test.
