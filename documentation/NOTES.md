# 🔁 Notes:

## upload.py

* File is fully read into memory with await file.read() — OK for <10MB.
* If you want to stream large files, we can use .file.read() in chunks (not urgent now).

* Spin up the containers using the docker-compose yaml.
* `docker-compose up -d`

* To automatically fix lint issues using ruff:
* `ruff check . --fix`


* 🚀 http://localhost:3000 → Frontend

* 🛠️ http://localhost:8000/docs → FastAPI docs

* 📦 localhost:27017 → MongoDB

### NodeJS Scaffolding
* For scaffolding, you need the directory to be completely empty. As we have a dockerfile to spin up the nodejs container, it is not empty.
* So temporarily we will move it, run the docker run command (which creates a temporary container) without docker compose, and then restore it back to the docuwise-ui folder.

```powershell
Move-Item -Path .\docuwise-ui\Dockerfile -Destination .\Dockerfile.ui.bak

docker run -it --rm -v "${PWD}\docuwise-ui:/app" -w /app node:20-alpine npx create-next-app@latest .
```

```
✔ Would you like to use TypeScript? … Yes
✔ Would you like to use ESLint? … Yes
✔ Would you like to use Tailwind CSS? … Yes
✔ Would you like your code inside a `src/` directory? … Yes
✔ Would you like to use App Router? (recommended) … No
✔ Would you like to use Turbopack for `next dev`? … No
✔ Would you like to customize the import alias (`@/*` by default)? … No
Creating a new Next.js app in /app.
```

* For the dockerization, we have removed the app.api.routes from main.py, ingest.py and upload.py

```python
# ingest.py
# FROM
from app.services.chunker import TextChunker
from app.services.embedder import TextEmbedder
from app.services.indexer import FAISSIndexer
from app.services.pdf_loader import PDFLoader

# TO
from services.chunker import TextChunker
from services.embedder import TextEmbedder
from services.indexer import FAISSIndexer
from services.pdf_loader import PDFLoader

# main.py
# FROM
from app.api.routes import ingest, upload

# TO
from app.api.routes import ingest, upload

# upload.py
# FROM
from app.models.file_metadata import FileUploadResponse
from app.services.mongo_client import save_metadata

# TO
from models.file_metadata import FileUploadResponse
from services.mongo_client import save_metadata
```
