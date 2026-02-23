from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="AI Sentiment Analysis API")

# Get configuration from environment
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased")
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "512"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Validate required environment variables
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set!")

print(f"🔑 API Key loaded: {API_KEY[:5]}... (hidden for security)")
print(f"🤖 Loading model: {MODEL_NAME}")
print(f"📝 Environment: {ENVIRONMENT}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Load model
model = TFAutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
    from_pt=True
)

class TextRequest(BaseModel):
    text: str

class HealthResponse(BaseModel):
    status: str
    environment: str
    model: str

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="healthy",
        environment=ENVIRONMENT,
        model=MODEL_NAME
    )

@app.post("/predict")
async def predict(
    request: TextRequest,
    x_api_key: str = Header(...)
):
    # API Key validation
    if x_api_key != API_KEY:
        if DEBUG:
            print(f"⚠️ Invalid API key attempt: {x_api_key[:5]}...")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    
    try:
        # Tokenize input
        inputs = tokenizer(
            request.text,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="tf"
        )
        
        # Get predictions
        outputs = model(**inputs)
        probs = tf.nn.softmax(outputs.logits, axis=1)
        
        # Convert to float for JSON serialization
        result = {
            "negative": float(probs[0][0]),
            "positive": float(probs[0][1]),
            "text_length": len(request.text)
        }
        
        if DEBUG:
            print(f"✅ Prediction made for text: {request.text[:50]}...")
        
        return result
        
    except Exception as e:
        if DEBUG:
            print(f"❌ Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "model": MODEL_NAME,
        "api_key_configured": bool(API_KEY)
    }