# Use official Python 3.12 image
FROM python:3.12.6-slim

# Set working directory inside container
WORKDIR /app

# Copy project files (ignoring env via .dockerignore)
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app uses
EXPOSE 1729

# Run the app
CMD ["python", "mcp-server.py"]
