FROM python:3.13-alpine

ARG APP_UID=10001
ARG APP_GID=10001

RUN addgroup -S -g "${APP_GID}" appgroup \
    && adduser -S -D -H -u "${APP_UID}" -G appgroup appuser

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --requirement requirements.txt

COPY --chown=appuser:appgroup app.py .

USER appuser
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/status', timeout=2)"

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=2", "--threads=4", "--access-logfile=-", "app:app"]
