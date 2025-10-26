# 🎯 QUICK START GUIDE - Model Deployment Setup

## ✅ What We've Set Up

Your Lumera AI project now has **automatic model downloading from Google Drive** on deployment. This solves the GitHub 100MB file size limit while keeping your model accessible.

---

## 🚀 3-Step Setup Process

### Step 1: Upload Model to Google Drive

1. Go to [Google Drive](https://drive.google.com)
2. Upload `backend/model/convnext_tiny_celeb.pth`
3. Right-click the file → **Share** → **Get link**
4. Change to: **"Anyone with the link"** 
5. Copy the link (example: `https://drive.google.com/file/d/ABC123xyz/view?usp=sharing`)

### Step 2: Configure the URL (Choose ONE method)

#### Method A: Automatic (Recommended) ✨

```bash
cd backend
python setup_model_url.py "PASTE_YOUR_GOOGLE_DRIVE_LINK_HERE"
```

This will automatically update the URL in your `.env` file.

#### Method B: Manual

Open `backend/.env` and add/update this line:

```properties
MODEL_DOWNLOAD_URL="https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
```

**IMPORTANT FOR DEPLOYMENT:** 
When deploying to Render/Railway/etc., you must set the `MODEL_DOWNLOAD_URL` environment variable in your deployment platform's settings!

### Step 3: Test & Deploy

```bash
# Test the download locally (optional but recommended)
cd backend
python download_model.py

# If successful, commit and push
cd ..
git add backend/download_model.py backend/setup_model_url.py backend/MODEL_DEPLOYMENT.md
git commit -m "Add automatic model download from Google Drive"
git push origin main
```

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `download_model.py` | Downloads model from Google Drive automatically |
| `setup_model_url.py` | Quick tool to configure your Google Drive URL |
| `MODEL_DEPLOYMENT.md` | Full documentation for deployment |
| `QUICKSTART.md` | This file - quick reference guide |

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. App Starts (Render/Railway/Local)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. model_loader.py checks: Does model file exist locally?  │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼ NO                        ▼ YES
┌───────────────────┐      ┌────────────────┐
│ 3. Download from  │      │ 4. Load model  │
│    Google Drive   │      │    directly    │
│    (1-2 min)      │      │    (instant)   │
└─────────┬─────────┘      └────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│ 5. Model cached for future runs         │
└─────────────────────────────────────────┘
```

---

## ✅ What's Already Done

- ✅ `model_loader.py` updated to auto-download model
- ✅ `.gitignore` updated to exclude `*.pth` files
- ✅ `requests` library already in `requirements.txt`
- ✅ Download utility with progress tracking
- ✅ Error handling and validation

---

## 🎯 What YOU Need to Do

1. **Upload model to Google Drive** → Get share link
2. **Run setup script** → `python setup_model_url.py "YOUR_LINK"`
3. **Test locally** → `python download_model.py`
4. **Commit & Push** → Your code (without the 100MB model!)
5. **Deploy** → Model downloads automatically on first run

---

## 🔒 Security Note

**Current Setup (Public Link):**
- ✅ Easy and fast
- ⚠️ Anyone with link can download
- 👍 Good for non-proprietary models

**If your model is sensitive:**
- Use Google Drive API with service account
- Or use AWS S3 / Google Cloud Storage with private buckets
- Contact me if you need help with private setup

---

## 🛠️ Troubleshooting

### "Model download failed"
- ✅ Check Google Drive link is public
- ✅ Verify URL in `download_model.py`
- ✅ Check your internet connection
- ✅ Try downloading manually with `python download_model.py`

### "Module not found: download_model"
- ✅ Make sure `download_model.py` is in the `backend/` folder
- ✅ Check file permissions

### Deployment platform storage issues
- ✅ Make sure persistent storage/disk is enabled
- ✅ Model needs ~200-500MB disk space

---

## 📞 Need Help?

Check the detailed guide: `MODEL_DEPLOYMENT.md`

Or run the test script:
```bash
cd backend
python download_model.py
```

---

## 🎉 That's It!

Your model will now:
- ✅ Stay out of GitHub (no 100MB limit issues)
- ✅ Download automatically on deployment
- ✅ Cache for fast subsequent loads
- ✅ Work on any platform (Render, Railway, etc.)

**Happy deploying! 🚀**
