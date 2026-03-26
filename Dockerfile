ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python dependencies
RUN apk add --no-cache python3 py3-pip

# Copy project files
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY run.py /
COPY hadiagnostic/ /hadiagnostic/

CMD ["python3", "/run.py"]
