FROM python:3.11-slim

WORKDIR /app

# 1. System packages needed for RDKit
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install PyTorch CPU (khfif bzaf o sari3 f l-build)
RUN pip install --no-cache-dir torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu

# 3. Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy project files
COPY . .

# 5. Permission for 3D generated html
RUN mkdir -p generated && chmod 777 generated

# 6. Default Port (Render automatically sets $PORT)
ENV PORT=8000
EXPOSE 8000

# 7. Start FastAPI listening on $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
