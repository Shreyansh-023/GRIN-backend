"""
Utility to download the ML model from Google Drive on first run or deployment.
This keeps the model out of GitHub (>100MB limit) while ensuring it's available when needed.
"""

import os
import requests
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Google Drive URL from environment variable (more secure)
GOOGLE_DRIVE_MODEL_URL = os.getenv("MODEL_DOWNLOAD_URL", "")

# Local model path
MODEL_DIR = "./model"
MODEL_PATH = os.path.join(MODEL_DIR, "convnext_tiny_celeb.pth")

def get_google_drive_download_url(share_link):
    """
    Convert Google Drive share link to direct download URL.
    
    If you have a share link like:
    https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    
    This function converts it to:
    https://drive.google.com/uc?export=download&id=FILE_ID
    
    Args:
        share_link (str): Google Drive share link
    
    Returns:
        str: Direct download URL
    """
    if "drive.google.com" in share_link:
        if "/file/d/" in share_link:
            file_id = share_link.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    return share_link

def download_file_from_google_drive(url, destination):
    """
    Download a file from Google Drive with progress indication.
    Handles large files with confirmation tokens.
    
    Args:
        url (str): Google Drive download URL
        destination (str): Local file path to save the model
    """
    
    print(f"📥 Downloading model from Google Drive...")
    print(f"   URL: {url[:60]}...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    # Try using gdown for better Google Drive support
    try:
        import gdown
        print("   ✅ gdown library found")
        
        # Extract file ID from various Google Drive URL formats
        file_id = None
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        
        if file_id:
            download_url = f"https://drive.google.com/uc?id={file_id}"
            print(f"   Using gdown to download file ID: {file_id}")
            
            # gdown.download returns the file path on success, None on failure
            result = gdown.download(download_url, destination, quiet=False, fuzzy=True)
            
            if result is None:
                print("❌ gdown download returned None - download failed")
                return False
            
            print(f"   ✅ gdown download completed, result: {result}")
        else:
            print(f"   ⚠️  Could not extract file ID from URL, falling back to requests")
            raise ImportError("Could not extract file ID")
            
    except ImportError as e:
        print(f"   ⚠️  gdown not available or incompatible: {e}")
        print("   Falling back to requests...")
        
        # Fallback to requests if gdown not available
        session = requests.Session()
        
        response = session.get(url, stream=True, allow_redirects=True)
        
        # Handle Google Drive warning for large files
        token = None
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                token = value
                break
        
        if token:
            params = {'confirm': token}
            url_with_token = url + f"&confirm={token}"
            response = session.get(url_with_token, stream=True, allow_redirects=True)
        
        # Save the file
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}% ({downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)", end='')
        print()  # New line after progress
    
    except Exception as e:
        print(f"❌ Download error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify file was downloaded
    if os.path.exists(destination):
        file_size = os.path.getsize(destination) / (1024*1024)
        print(f"✅ Model downloaded successfully to: {destination}")
        print(f"   File size: {file_size:.1f} MB")
        
        if file_size < 1:
            print("⚠️  Warning: Downloaded file is very small. Download may have failed.")
            print("   Please check your Google Drive link is set to 'Anyone with the link'")
            return False
        return True
    else:
        print("❌ Download failed: File not created")
        return False

def ensure_model_exists():
    """
    Check if the model file exists locally.
    If not, download it from Google Drive.
    
    Returns:
        bool: True if model is ready, False otherwise
    """
    if os.path.exists(MODEL_PATH):
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        if file_size < 1:
            print(f"⚠️  Model file exists but is corrupted (size: {file_size:.1f} MB). Re-downloading...")
            os.remove(MODEL_PATH)
        else:
            print(f"✅ Model already exists: {MODEL_PATH} ({file_size:.1f} MB)")
            return True
    
    print(f"⚠️  Model not found at: {MODEL_PATH}")
    
    if not GOOGLE_DRIVE_MODEL_URL or GOOGLE_DRIVE_MODEL_URL == "your_google_drive_model_link_here":
        print("❌ ERROR: Google Drive model URL not configured!")
        print("   Please set MODEL_DOWNLOAD_URL in your .env file")
        print("   Example: MODEL_DOWNLOAD_URL=\"https://drive.google.com/file/d/YOUR_FILE_ID/view\"")
        return False
    
    try:
        # Convert share link to direct download URL if needed
        download_url = get_google_drive_download_url(GOOGLE_DRIVE_MODEL_URL)
        
        # Download the model
        success = download_file_from_google_drive(download_url, MODEL_PATH)
        
        return success
        
    except Exception as e:
        print(f"❌ Error downloading model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    """
    Can be run standalone to pre-download the model:
    python download_model.py
    """
    print("=" * 60)
    print("🤖 LUMERA AI - Model Download Utility")
    print("=" * 60)
    
    if ensure_model_exists():
        print("\n✅ Model is ready to use!")
        sys.exit(0)
    else:
        print("\n❌ Model download failed!")
        sys.exit(1)
