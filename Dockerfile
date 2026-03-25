FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY medconnect/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY medconnect /app
COPY deploy /app/deploy
RUN chmod +x /app/deploy/entrypoint.sh

ENV PORT=5000
EXPOSE 5000

ENTRYPOINT ["/app/deploy/entrypoint.sh"]
CMD ["gunicorn", "-c", "/app/deploy/gunicorn.conf.py", "wsgi:app"]
