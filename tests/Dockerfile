FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install dependencies first to leverage Docker cache
# We manually install dependencies listed in pyproject.toml
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    "httpx>=0.24.0" \
    "python-dotenv>=0.9.9" \
    "py7zr>=1.0.0" \
    "rich>=14.2.0" \
    "textual>=6.4.0" \
    "typer>=0.20.0" \
    "zstandard>=0.25.0" \
    hatchling

# Copy project files
COPY . .

# Install the package (dependencies should already be satisfied)
RUN pip install  .

# Run tests
CMD ["python", "tests/run_tests.py", "--worker"]
