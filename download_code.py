"""
Utility to download sensitive Python files from Google Drive.
This allows keeping sensitive model loading code out of the repository.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Google Drive URL from environment variable
MODEL_LOADER_URL = os.getenv("MODEL_LOADER_URL", "")

# Local path for model_loader.py
MODEL_LOADER_PATH = "./model_loader.py"

def download_file_from_google_drive(url, destination):
    """
    Download a file from Google Drive.
    
    Args:
        url (str): Google Drive share link or download URL
        destination (str): Local file path to save the file
    
    Returns:
        bool: True if download successful, False otherwise
    """
    
    print(f"📥 Downloading {os.path.basename(destination)} from Google Drive...")
    
    try:
        import gdown
        
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
                print("❌ Download failed")
                return False
            
            print(f"   ✅ Download completed successfully!")
            return True
        else:
            print(f"   ❌ Could not extract file ID from URL")
            return False
            
    except ImportError:
        print("   ❌ gdown library not found. Please install it: pip install gdown")
        return False
    except Exception as e:
        print(f"   ❌ Download error: {str(e)}")
        return False

def ensure_model_loader_exists():
    """
    Check if model_loader.py exists locally.
    If not, download it from Google Drive using the URL in .env
    
    Returns:
        bool: True if file exists or was successfully downloaded, False otherwise
    """
    
    # Check if file already exists
    if os.path.exists(MODEL_LOADER_PATH):
        print(f"✅ {MODEL_LOADER_PATH} found locally.")
        return True
    
    print(f"⚠️  {MODEL_LOADER_PATH} not found locally.")
    
    # Check if URL is configured
    if not MODEL_LOADER_URL:
        print("❌ MODEL_LOADER_URL not set in .env file")
        print("   Please add MODEL_LOADER_URL=<your_google_drive_link> to backend/.env")
        return False
    
    # Attempt download
    print(f"   Attempting to download from configured URL...")
    success = download_file_from_google_drive(MODEL_LOADER_URL, MODEL_LOADER_PATH)
    
    if success and os.path.exists(MODEL_LOADER_PATH):
        file_size = os.path.getsize(MODEL_LOADER_PATH)
        print(f"✅ Successfully downloaded {MODEL_LOADER_PATH} ({file_size:,} bytes)")
        return True
    else:
        print(f"❌ Failed to download {MODEL_LOADER_PATH}")
        return False

if __name__ == "__main__":
    """
    Run this script directly to test the download functionality:
    python download_code.py
    """
    print("=" * 60)
    print("MODEL_LOADER.PY DOWNLOAD UTILITY")
    print("=" * 60)
    
    success = ensure_model_loader_exists()
    
    if success:
        print("\n✅ SUCCESS: model_loader.py is ready to use!")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Could not obtain model_loader.py")
        print("\nTroubleshooting:")
        print("1. Make sure MODEL_LOADER_URL is set in backend/.env")
        print("2. Verify the Google Drive link is publicly accessible")
        print("3. Ensure gdown is installed: pip install gdown")
        sys.exit(1)
