FROM python:3.9
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update \
&& pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "./app.py"]