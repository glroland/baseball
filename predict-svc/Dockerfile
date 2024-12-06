FROM registry.access.redhat.com/ubi9/python-311:1-77.1729767833

# listen on port 8080
EXPOSE 8080/tcp

# Set the working directory in the container
WORKDIR /projects

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY ./src/ .

# Environment variable for number of workers
ENV NUM_WORKERS "10"

# Specify the command to run on container start
CMD fastapi run app.py --host 0.0.0.0 --port 8080 --no-reload --workers $NUM_WORKERS
