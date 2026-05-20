FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential pkg-config libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && if [ \"${AUTO_SEED_SAMPLE_DATA:-1}\" = \"1\" ]; then python manage.py seed --locations ${SEED_LOCATIONS:-5} --properties ${SEED_PROPERTIES:-20} --images ${SEED_IMAGES:-3} --seed ${SEED_RANDOM:-7} --idempotent; fi && daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application"]
