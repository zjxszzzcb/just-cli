FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Proxy support (optional, pass via --build-arg)
ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV http_proxy=${HTTP_PROXY}
ENV https_proxy=${HTTPS_PROXY}

# Install dependencies from requirements.txt
COPY tests/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project files
COPY . .

# Install the package
RUN pip install .

# Run tests
CMD ["python", "tests/run_tests.py", "--worker"]
