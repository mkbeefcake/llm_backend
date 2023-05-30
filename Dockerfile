FROM python:3.10-slim-bullseye AS python-base

# builder-base is used to build dependencies
FROM python-base AS builder-base
RUN buildDeps="build-essential" \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        netcat \
    && apt-get install -y git \
    && apt-get install -y --no-install-recommends $buildDeps \
    && rm -rf /var/lib/apt/lists/*

# Create App directory
RUN mkdir /app
WORKDIR /app
COPY . .
RUN chmod +x /docker-entrypoint.sh
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

EXPOSE 8000
ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD ["poetry", "run", "python", "main.py"]

# 'lint' stage runs black and isort
# running in check mode means build will fail if any linting errors occur
FROM development AS lint
RUN pip install git+https://github.com/psf/black
RUN black --config ./pyproject.toml --check app tests
RUN isort --settings-path ./pyproject.toml --recursive --check-only
CMD ["tail", "-f", "/dev/null"]

# 'test' stage runs our unit tests with pytest and
# coverage.  Build will fail if test coverage is under 95%
FROM development AS test
RUN coverage run --rcfile ./pyproject.toml -m pytest ./tests
RUN coverage report --fail-under 95

# 'production' stage uses the clean 'python-base' stage and copyies
# in only our runtime deps that were installed in the 'builder-base'
FROM python-base AS production
ENV FASTAPI_ENV=production

COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY gunicorn_conf.py /gunicorn_conf.py

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create user with the name poetry
RUN groupadd -g 1500 poetry && \
    useradd -m -u 1500 -g poetry poetry

COPY --chown=poetry:poetry ./app /app
USER poetry
WORKDIR /app

ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD [ "gunicorn", "--worker-class uvicorn.workers.UvicornWorker", "--config /gunicorn_conf.py", "main:app"]