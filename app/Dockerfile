# syntax=docker/dockerfile:1

# Create a venv using the larger base image (which contains gcc).
FROM python:3.13-bullseye AS builder
RUN python3 -m venv /venv
COPY requirements.txt /requirements.txt
RUN /venv/bin/pip3 install --no-cache-dir -r /requirements.txt

# Copy the venv to a fresh "slim" image.
FROM python:3.13-slim-bullseye
COPY --from=builder /venv /venv
WORKDIR /app
COPY . .
CMD ["/venv/bin/python3", "app.py"]
