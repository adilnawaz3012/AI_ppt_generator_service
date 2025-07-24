FROM python:3.11-slim

# Set a consistent working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# now copy all necessary application files into the image
COPY ./app ./app
COPY ./templates ./templates