# Step 1: Base image
FROM python:3.10-slim

# Step 2: Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul

# Step 3: Install system dependencies
# ffmpeg: required for faster-whisper
# build-essential & pkg-config: required for compiling some python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Set work directory
WORKDIR /app

# Step 5: Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Step 6: Copy project files
COPY . .

# Step 7: Create storage directories if they don't exist
RUN mkdir -p /storage/audio/interviews

# Step 8: Expose port
EXPOSE 8000

# Step 9: Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]