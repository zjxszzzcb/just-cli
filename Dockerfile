FROM python:3.11

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install dependencies from requirements.txt
COPY tests/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy project files (assumes build context is project root)
COPY . .

# Install the package
RUN pip install .

RUN bash scripts/system/linux/proxy/proxy.sh install

ENV HTTP_PROXY_URL=http://host.docker.internal:7890
ENV HTTPS_PROXY_URL=http://host.docker.internal:7890

# Run tests
CMD ["/bin/bash"]
