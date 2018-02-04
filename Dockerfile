FROM python:3.6-alpine

WORKDIR /app

# Install dependencies.
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Add actual source code.
ADD src /app
