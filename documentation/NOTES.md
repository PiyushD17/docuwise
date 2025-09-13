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

* We now have 2 dockerfiles : Prod and Dev.

* How to run the dev backend
```bash
docker run --rm -p 8000:8000 -v "$PWD":/app --env-file .env docuwise-api:dev
docker run --rm -p 3000:3000 -v "$PWD":/app docuwise-ui:dev
```

* How to run prod front end
```bash
docker build -t docuwise-ui:dev \
  --build-arg NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
  -f Dockerfile .
docker run --rm -p 3000:3000 docuwise-ui:dev
```


## Build & Run Docker Dev

```bash
# From project root (where .env and compose.dev.yaml live)
docker compose -f compose.dev.yaml up --build

# stop
docker compose -f compose.dev.yaml down
```

## Build & Run Docker Prod
```bash
# From project root
docker compose -f compose.prod.yaml up -d --build

# Check health/logs
docker compose -f compose.prod.yaml ps
docker compose -f compose.prod.yaml logs -f api
docker compose -f compose.prod.yaml logs -f ui

# Stop
docker compose -f compose.prod.yaml down
```

### When Prod is used, the data lands up inside the file system of the container.

* How to verify this?

```bash
docker compose ps
docker compose exec api sh -lc 'pwd; echo "---"; ls -alh /app/data'
```

## Makefile
* To make things easier, I have added a makefile (need to install make command on Windows)
* Now we can simply run these commands to spin up prod or dev.

### 🟢 Development (compose.dev.yaml)

```bash
# start dev stack
make dev-up

# stop dev stack
make dev-down

# down + up again
make dev-restart

# tail logs for all dev services
make dev-logs

# tail logs for API only
make dev-api-logs

# tail logs for UI only
make dev-ui-logs

# show running dev containers
make dev-ps

# build dev images
make dev-build

# rebuild without cache + restart
make dev-rebuild
```

### 🔵 Production (compose.prod.yaml)
```bash
# start prod stack
make prod-up

# stop prod stack + remove volumes
make prod-down

# down + up again
make prod-restart

# tail logs for all prod services
make prod-logs

# tail logs for API only
make prod-api-logs

# tail logs for UI only
make prod-ui-logs

# show running prod containers
make prod-ps

# build prod images
make prod-build

# rebuild without cache + restart
make prod-rebuild
```

### 🧪 QA / E2E
```bash
# curl API (/health) + UI (/)
make health

# run scripts/e2e_smoke.py
make smoke

# run scripts/e2e_ingest.py
make smoke_ingest
# full cycle: prod-up → health → smoke → prod-down
make check
```

### 🛠 Utilities
```bash
# list docuwise-related images
make images

# prune unused Docker objects
make prune

# open a Mongo shell inside the running container
make mongo-sh

# run Ruff linting
make lint

# run pytest suite
make test

# auto-format with Ruff + isort + black
make format
```
