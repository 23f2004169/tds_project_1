FROM python:3.12-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Install Node.js (which includes npm and npx)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Verify Node.js, npm, and npx installation
RUN node --version && npm --version && npx --version

# Install Prettier version 3.4.2 globally
RUN npm install -g prettier@3.4.2

# Verify Prettier installation
RUN prettier --version

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Create a virtual environment and install dependencies
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Set the entry point to use the virtual environment
ENV PATH="/app/venv/bin:/root/.local/bin/:$PATH"

# Copy the application code
COPY app.py /app
COPY evaluate.py /app
COPY datagen.py /app
COPY tasksA.py /app
COPY tasksB.py /app

# Command to run the application
CMD ["python3", "app.py"]