# 🔁 Notes:

## upload.py

* File is fully read into memory with await file.read() — OK for <10MB.
* If you want to stream large files, we can use .file.read() in chunks (not urgent now).
