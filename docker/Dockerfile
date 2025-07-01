FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 agent

# Copy installed packages from builder
COPY --from=builder /root/.local /home/agent/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=agent:agent . .

# Switch to non-root user
USER agent

# Add user's local bin to PATH
ENV PATH=/home/agent/.local/bin:$PATH

# Set Python path
ENV PYTHONPATH=/app

# Run the agent
CMD ["python", "main.py"]