FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt update && apt install curl net-tools -y

# Install dependencies from requirements.txt
COPY tests/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project files (assumes build context is project root)
COPY . .

# Install the package
RUN pip install .

RUN just --help

# Run tests
CMD ["/bin/bash"]
