FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y nginx gettext libcairo2-dev pkg-config build-essential

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/staticfiles /app/media

RUN rm /etc/nginx/sites-available/default
COPY scripts/nginx/default.conf /etc/nginx/sites-available/default

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh


# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
