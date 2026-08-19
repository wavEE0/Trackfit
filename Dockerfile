# using python 3.11 slim - smaller than the full image
# NOTE: this is a first pass, will look into multi-stage builds later
FROM python:3.11-slim

# stops python from buffering stdout/stderr so logs appear in real time
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# install system deps needed by psycopg2 and pillow
RUN apt-get update && apt-get install -y --no-install-recommends     libpq-dev     gcc     && rm -rf /var/lib/apt/lists/*

# copy requirements first so docker can cache this layer
# only re-runs pip install if requirements.prod.txt changes
COPY trackfit/requirements.prod.txt .
RUN pip install --no-cache-dir -r requirements.prod.txt

# copy the django project
COPY trackfit/ .

# collect static files for whitenoise to serve
# SECRET_KEY is a dummy here just so collectstatic doesnt complain
RUN SECRET_KEY=collectstatic-dummy python manage.py collectstatic --noinput

EXPOSE 8000

# gunicorn is the production wsgi server - dont use runserver in prod
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "trackfit.wsgi:application"]
