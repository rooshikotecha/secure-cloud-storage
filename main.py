from fastapi import FastAPI, UploadFile, File
from pymongo import MongoClient
import rsa
import base64

app = FastAPI()

# Connect to MongoDB (Replace with your MongoDB URL)
client = MongoClient("mongodb://localhost:27017")
db = client["secure_storage"]
collection = db["files"]

# Generate RSA keys (Use this only once, then save keys securely)
(public_key, private_key) = rsa.newkeys(512)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_data = await file.read()

    # Encrypt file data using RSA public key
    encrypted_data = rsa.encrypt(file_data, public_key)
    encoded_data = base64.b64encode(encrypted_data).decode()  # Store as base64 string

    # Save encrypted data in MongoDB
    collection.insert_one({"filename": file.filename, "data": encoded_data})

    return {"message": "File uploaded & encrypted successfully"}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_record = collection.find_one({"filename": filename})
    if not file_record:
        return {"error": "File not found"}

    # Decode and decrypt data
    encrypted_data = base64.b64decode(file_record["data"])
    decrypted_data = rsa.decrypt(encrypted_data, private_key)

    return {"filename": filename, "content": decrypted_data.decode(errors="ignore")}

@app.get("/")
def home():
    return {"message": "Secure Cloud Storage API is Running"}
