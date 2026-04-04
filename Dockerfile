FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install dependencies from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project files (assumes build context is project root)
COPY . ./

# Install the package
RUN pip install .

# Run tests
CMD ["python", "tests/run_tests.py", "--worker"]
