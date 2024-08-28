# Use the official Python image as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY ./requirements.txt /app/requirements.txt

# Install dependencies and zbar-tools
RUN apt-get update \
    && apt-get install -y zbar-tools \
    && pip install --upgrade pip \
    && pip install --upgrade -r /app/requirements.txt

# Copy the application code into the container
COPY ./bookflix /app/bookflix

# Expose port 8000 to the host
EXPOSE 8000

# Command to run the FastAPI application
CMD ["fastapi", "run", "--host", "0.0.0.0", "bookflix/main.py"]

