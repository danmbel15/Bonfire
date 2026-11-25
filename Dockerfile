FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

ENV PYTHONUNBUFFERED=1

# Installs python dependencies according to 'requirements.txt' without keeping a download cache to save space.
RUN pip install --no-cache-dir -r requirements.txt

# Copies Bonfire's bot's script into app/
COPY main.py .

# Exec form for shell/bash "python3 main.py" separated into command and arguments
CMD [ "python3", "main.py" ]


