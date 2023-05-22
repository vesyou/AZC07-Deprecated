# Use Python 3.9 slim as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask application is listening on
EXPOSE 5000

# Set the entrypoint command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
