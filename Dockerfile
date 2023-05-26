# Use the official Python 3.7 image as the base image
FROM python:3.7-slim

# Set the working directory in the container
WORKDIR /app

# Install the packages necessary for building Python packages
RUN apt-get update \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy the Poetry files to the container
COPY pyproject.toml poetry.lock /app/
 
# Install the dependencies
RUN poetry install --no-root --no-dev
 
# Copy the FastAPI files to the container
COPY . /app/

# Expose port 80 to the outside world
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Note: if you're using a different file name for your FastAPI app, replace "main" with the appropriate filename