"""
Helper script to set up MODEL_LOADER_URL in .env file
Run this after uploading model_loader.py to Google Drive
"""

import os
from pathlib import Path

def setup_model_loader_url():
    """
    Interactive script to add MODEL_LOADER_URL to .env file
    """
    print("=" * 70)
    print("MODEL_LOADER.PY GOOGLE DRIVE SETUP")
    print("=" * 70)
    print()
    print("This script will help you configure the Google Drive URL for model_loader.py")
    print()
    print("Steps to get the Google Drive link:")
    print("1. Upload model_loader.py to your Google Drive")
    print("2. Right-click the file → Share → Change to 'Anyone with the link'")
    print("3. Copy the share link (format: https://drive.google.com/file/d/FILE_ID/view)")
    print()
    
    # Get the URL from user
    url = input("Enter your Google Drive link for model_loader.py: ").strip()
    
    if not url:
        print("❌ No URL provided. Exiting.")
        return
    
    if "drive.google.com" not in url:
        print("⚠️  Warning: This doesn't look like a Google Drive URL")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Path to .env file
    env_path = Path(__file__).parent / ".env"
    
    # Read existing .env content
    env_lines = []
    model_loader_exists = False
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
        
        # Check if MODEL_LOADER_URL already exists
        for i, line in enumerate(env_lines):
            if line.startswith('MODEL_LOADER_URL'):
                env_lines[i] = f'MODEL_LOADER_URL="{url}"\n'
                model_loader_exists = True
                break
    
    # Add MODEL_LOADER_URL if it doesn't exist
    if not model_loader_exists:
        if env_lines and not env_lines[-1].endswith('\n'):
            env_lines.append('\n')
        env_lines.append(f'\n# Google Drive Model Loader URL\n')
        env_lines.append(f'MODEL_LOADER_URL="{url}"\n')
    
    # Write back to .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(env_lines)
    
    print()
    print("✅ SUCCESS! MODEL_LOADER_URL has been added to .env")
    print()
    print(f"   File: {env_path}")
    print(f"   URL: {url[:60]}...")
    print()
    print("Next steps:")
    print("1. Remove model_loader.py from your local backend folder (it will be downloaded)")
    print("2. Restart the backend server")
    print("3. The server will automatically download model_loader.py on startup")
    print()

if __name__ == "__main__":
    try:
        setup_model_loader_url()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
