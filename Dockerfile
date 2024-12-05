# Use an official Python runtime
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Copy the config.env file into the container at /usr/src/app
COPY config.env .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy 'tghbot' and 'plugins' and 'sabnzbdapi' directories
COPY plugins /usr/src/app/plugins
COPY sabnzbdapi /usr/src/app/sabnzbdapi
COPY tghbot /usr/src/app/tghbot


# Make port 80 available to the world outside this container
EXPOSE 80

# Run update.py when the container launches
CMD ["python", "./update.py"]
