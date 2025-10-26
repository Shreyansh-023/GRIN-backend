"""
Quick setup script to configure Google Drive model URL in .env file.
Run this after uploading your model to Google Drive.

Usage:
    python setup_model_url.py "https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
"""

import sys
import re
import os

def update_model_url_in_env(google_drive_url):
    """Update the Google Drive URL in .env file"""
    
    # Validate the URL format
    if "drive.google.com" not in google_drive_url:
        print("❌ Error: This doesn't look like a Google Drive URL")
        print("   Expected format: https://drive.google.com/file/d/FILE_ID/view?usp=sharing")
        return False
    
    env_file = ".env"
    
    # Check if .env exists
    if not os.path.exists(env_file):
        print("⚠️  .env file not found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r", encoding="utf-8") as f:
                content = f.read()
        else:
            print("❌ Error: .env.example not found!")
            return False
    else:
        # Read the current .env
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
    
    # Replace or add the MODEL_DOWNLOAD_URL
    if "MODEL_DOWNLOAD_URL" in content:
        # Update existing
        old_pattern = r'MODEL_DOWNLOAD_URL="[^"]*"'
        new_value = f'MODEL_DOWNLOAD_URL="{google_drive_url}"'
        updated_content = re.sub(old_pattern, new_value, content)
    else:
        # Add new
        updated_content = content + f'\n\n# Google Drive Model Download URL\nMODEL_DOWNLOAD_URL="{google_drive_url}"\n'
    
    # Write back
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print("✅ Successfully updated MODEL_DOWNLOAD_URL in .env file")
    print(f"   URL: {google_drive_url}")
    print("\n📋 Next steps:")
    print("   1. Test the download: python download_model.py")
    print("   2. If successful, commit and push to GitHub")
    print("   3. Make sure to set MODEL_DOWNLOAD_URL in your deployment platform's environment variables")
    print("   4. Deploy your application!")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("🔧 LUMERA AI - Google Drive Model URL Setup (.env)")
    print("=" * 70)
    print()
    
    if len(sys.argv) < 2:
        print("📝 Usage:")
        print('   python setup_model_url.py "YOUR_GOOGLE_DRIVE_LINK"')
        print()
        print("📌 Steps to get your Google Drive link:")
        print("   1. Upload convnext_tiny_celeb.pth to Google Drive")
        print("   2. Right-click → Get link → Set to 'Anyone with the link'")
        print("   3. Copy the link")
        print("   4. Run: python setup_model_url.py \"<paste link here>\"")
        print()
        sys.exit(1)
    
    google_drive_url = sys.argv[1]
    
    if update_model_url_in_env(google_drive_url):
        sys.exit(0)
    else:
        sys.exit(1)
