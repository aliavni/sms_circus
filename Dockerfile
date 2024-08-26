FROM python:3.12.5

WORKDIR /app

# dont write pyc files
# dont buffer to stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/
COPY requirements_dev.txt /app/

# dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /app/requirements_dev.txt \
    && rm -rf /root/.cache/pip

COPY . /app/
