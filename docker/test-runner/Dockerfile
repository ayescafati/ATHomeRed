FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m runner

WORKDIR /home/runner/app

COPY requirements.txt ./requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libpq-dev \
       libffi-dev \
       libssl-dev \
    rustc \
    cargo \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt

COPY . /home/runner/app

RUN python - <<'PY'
import io,sys
p = '/home/runner/app/docker/test-runner/entrypoint.sh'
try:
    b = open(p, 'rb').read()
except FileNotFoundError:
    b = b''
if b.startswith(b'\xef\xbb\xbf'):
    b = b[3:]
b = b.replace(b'\r\n', b'\n')
open(p, 'wb').write(b)
PY

RUN chown -R runner:runner /home/runner/app \
    && chmod +x /home/runner/app/docker/test-runner/entrypoint.sh

USER runner

ENV PATH="/home/runner/.local/bin:${PATH}"

ENTRYPOINT ["/home/runner/app/docker/test-runner/entrypoint.sh"]
