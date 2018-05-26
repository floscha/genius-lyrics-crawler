FROM python:3.6-alpine

WORKDIR /app

# Install dependencies.
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Add actual source code.
COPY src /app
