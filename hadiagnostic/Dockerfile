ARG BUILD_FROM
FROM $BUILD_FROM

# Installer Python et les dépendances via apk (évite les problèmes pip/PEP668)
RUN apk add --no-cache python3 py3-requests py3-flask

# Copy project files
COPY run.py /
COPY diagnostic/ /diagnostic/

CMD ["python3", "/run.py"]
