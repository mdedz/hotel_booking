FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
ENV PYTHONPATH=/app/src

# system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    nodejs \
    libpq-dev \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# project
COPY src ./src
COPY entrypoint.sh .

# django static
RUN python src/manage.py collectstatic --noinput

CMD ["gunicorn", "hotel_booking.wsgi:application", "--bind", "0.0.0.0:8000"]
