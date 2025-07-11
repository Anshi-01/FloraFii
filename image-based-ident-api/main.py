from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
from pathlib import Path

app = FastAPI()

origins = [
    "http://localhost:3000"  # Frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASS_NAMES = ["Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy", 
               "Background_without_leaves", "Blueberry___healthy", "Cherry___Powdery_mildew", "Cherry___healthy", 
               "Corn___Cercospora_leaf_spot Gray_leaf_spot", "Corn___Common_rust", "Corn___Northern_Leaf_Blight", 
               "Corn___healthy", "Grape___Black_rot", "Grape___Esca_(Black_Measles)", 
               "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy", "Orange___Haunglongbing_(Citrus_greening)", 
               "Peach___Bacterial_spot", "Peach___healthy", "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", 
               "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", 
               "Soybean___healthy", "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy", 
               "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold", 
               "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot", 
               "Tomato___Tomato_mosaic_virus", "Tomato___healthy"]

# Load model
try:
    model_path = Path(__file__).parent.absolute() / "saved_model"
    MODEL = tf.keras.models.load_model(model_path)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    MODEL = None

@app.get('/ping')
async def ping():
    return "Hello! API is running."

def read_file_as_image(data) -> np.ndarray:
    try:
        image = Image.open(BytesIO(data))
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = np.array(image)
        image = np.expand_dims(image, axis=0)
        return image
    except Exception as e:
        print(f"Error processing image: {e}")
        raise

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if MODEL is None:
        return {"error": "Model not loaded"}
        
    try:
        img = read_file_as_image(await file.read())
        class_probs = MODEL.predict(img)
        class_index = int(np.argmax(class_probs[0]))
        class_name = CLASS_NAMES[class_index]
        confidence = float(np.max(class_probs[0]))

        return {
            'class_name': class_name,
            'class_index': class_index,
            'confidence': confidence
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=10000)
