# Use an optimized, slim official Python environment
FROM python:3.11-slim

WORKDIR /app

# Copy over package configuration manifests
COPY requirements.txt .

# Install dependencies directly into global container space
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Fire up the production ASGI engine mapping the target source
CMD ["python", "-m", "src.main"]