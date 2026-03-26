ARG BUILD_FROM
FROM $BUILD_FROM

# Install pip if not already present
RUN apk add --no-cache py3-pip

# Copy and install Python dependencies
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy project files
COPY run.py /
COPY diagnostic/ /diagnostic/

CMD ["python3", "/run.py"]
