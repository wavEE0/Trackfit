# switched to multi-stage build after reading about it
# builder stage installs gcc and compiles things, runner stage just has the app
# makes the final image smaller because we dont ship gcc and headers

# ── Stage 1: builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends     libpq-dev     gcc     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY trackfit/requirements.prod.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.prod.txt

# ── Stage 2: runner ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# only need the runtime library, not the dev headers
RUN apt-get update && apt-get install -y --no-install-recommends     libpq5     && rm -rf /var/lib/apt/lists/*

# copy installed packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app
COPY trackfit/ .

RUN SECRET_KEY=collectstatic-dummy python manage.py collectstatic --noinput

# run as non-root user - good security practice
RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2",      "--timeout", "30", "--access-logfile", "-", "trackfit.wsgi:application"]
