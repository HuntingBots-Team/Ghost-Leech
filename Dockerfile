# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install git and other system dependencies
RUN apt-get update &&     apt-get install -y git build-essential libssl-dev &&     rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip &&     pip install --no-cache-dir -r requirements.txt &&     pip install TgCrypto

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 80

# Define the command to run the application
CMD ["bash", "start.sh"]
