FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

# Installs python dependencies according to 'requirements.txt' without keeping a download cache to save space.
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Exec form for shell/bash "python3 main.py" separated into command and arguments
CMD [ "python3", "main.py" ]


