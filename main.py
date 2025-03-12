from fastapi import FastAPI, File, UploadFile, HTTPException
import rsa
import os

app = FastAPI()

# Generate RSA keys (Store these securely in production)
(public_key, private_key) = rsa.newkeys(512)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure upload directory exists

# ✅ Secure File Upload & Encryption
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        
        # Read file content
        file_data = await file.read()
        
        # Encrypt file content
        encrypted_data = rsa.encrypt(file_data, public_key)
        
        # Save encrypted file
        encrypted_path = file_location + ".enc"
        with open(encrypted_path, "wb") as ef:
            ef.write(encrypted_data)
        
        return {"message": f"File '{file.filename}' uploaded and encrypted successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ✅ Secure File Download & Decryption
@app.get("/download/{filename}")
async def download_file(filename: str):
    try:
        encrypted_path = os.path.join(UPLOAD_DIR, filename + ".enc")
        
        if not os.path.exists(encrypted_path):
            raise HTTPException(status_code=404, detail="File not found!")

        # Read encrypted file
        with open(encrypted_path, "rb") as ef:
            encrypted_data = ef.read()

        # Decrypt file
        decrypted_data = rsa.decrypt(encrypted_data, private_key)

        return {"filename": filename, "content": decrypted_data.decode(errors="ignore")}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Secure Cloud Storage API is running!"}
