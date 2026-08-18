# Base image: minimal Python 3.12, keeps the container small
FROM python:3.12-slim

# All paths below are relative to this directory inside the container
WORKDIR /code

# Copy requirements first (before app code) so Docker can cache this layer —
# dependencies only get reinstalled when requirements.txt actually changes,
# not every time we edit app code. Speeds up rebuilds a lot.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code
COPY app ./app

# Start the FastAPI app via uvicorn, listening on all interfaces so
# the container is reachable from outside (not just localhost inside the container)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]