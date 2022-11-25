FROM python:3-alpine

RUN set -ex && \
    apk add --update --no-cache libpq-dev && \
    addgroup -S -g 1000 fileshare && \
    adduser -S -u 1000 -s /bin/ash -G fileshare fileshare

USER fileshare

COPY --chown=fileshare:fileshare docker/entrypoint /entrypoint
COPY --chown=fileshare:fileshare docker/start /start
COPY --chown=fileshare:fileshare . /app

WORKDIR /app

RUN set -ex && \
    pip install pipenv && \
    export PATH=$PATH:/home/fileshare/.local/bin && \
    pipenv install --system --deploy && \
    chmod +x /entrypoint && \
    chmod +x /start

ENTRYPOINT ["/entrypoint"]

CMD ["/start"]
