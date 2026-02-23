import os
import secrets
import string
from pathlib import Path

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path('.env')
    
    if not env_path.exists():
        # Generate a secure API key
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        env_content = f"""# API Configuration
API_KEY={api_key}

# Backend Settings
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# Model Settings
MODEL_NAME=distilbert-base-uncased
MAX_LENGTH=512

# Environment (development/production)
ENVIRONMENT=development
DEBUG=True
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created .env file with API key: {api_key[:10]}...")
        print("⚠️  Keep this key secure! Don't share it publicly.")
    else:
        print("📝 .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = ['backend', 'frontend', 'model_cache', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}/")

if __name__ == "__main__":
    print("🚀 Setting up NLP Sentiment Analysis Project...")
    print("-" * 50)
    
    create_directories()
    create_env_file()
    
    print("-" * 50)
    print("✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start backend: uvicorn backend.app:app --reload")
    print("3. Start frontend: streamlit run frontend/app.py")
    print("4. Open browser: http://localhost:8501")