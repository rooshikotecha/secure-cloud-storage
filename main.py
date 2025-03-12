from fastapi import FastAPI, File, UploadFile
import rsa
import os

app = FastAPI()

# Generate RSA keys (Save them if needed)
(public_key, private_key) = rsa.newkeys(512)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure upload directory exists

# ✅ Upload and Encrypt File
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())

    # Encrypt file
    with open(file_location, "rb") as f:
        data = f.read()
    
    encrypted_data = rsa.encrypt(data, public_key)
    
    with open(file_location + ".enc", "wb") as ef:
        ef.write(encrypted_data)
    
    return {"message": f"File '{file.filename}' uploaded and encrypted successfully!"}

# ✅ Download and Decrypt File
@app.get("/download/{filename}")
async def download_file(filename: str):
    encrypted_path = os.path.join(UPLOAD_DIR, filename + ".enc")

    if not os.path.exists(encrypted_path):
        return {"error": "File not found!"}
    
    with open(encrypted_path, "rb") as ef:
        encrypted_data = ef.read()
    
    decrypted_data = rsa.decrypt(encrypted_data, private_key)

    return {"filename": filename, "content": decrypted_data.decode(errors="ignore")}

@app.get("/")
async def root():
    return {"message": "Secure Cloud Storage API is running!"}
