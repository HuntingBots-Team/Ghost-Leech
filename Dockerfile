# Step 1: Use a base image with Python
FROM python:3.10.0:latest

# Step 2: Set the working directory in the container
WORKDIR /usr/src/app

# Step 3: Copy the requirements file into the container
COPY requirements.txt ./

# Step 4: Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the current directory contents into the container at /usr/src/app
COPY . .

# Step 6: Make the start script executable
RUN chmod +x start.sh

# Step 7: Specify the command to run on container start
CMD ["bash", "start.sh"]
