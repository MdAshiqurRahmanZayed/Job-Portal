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

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY pyproject.toml uv.lock /app/
RUN uv export --frozen --no-hashes --no-emit-project --no-dev -o /tmp/requirements.lock.txt && \
    uv pip install --system --no-cache -r /tmp/requirements.lock.txt && \
    rm /tmp/requirements.lock.txt

COPY . /app/

RUN mkdir -p /app/staticfiles /app/media

RUN rm /etc/nginx/sites-available/default
COPY scripts/nginx/default.conf /etc/nginx/sites-available/default

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh


# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
