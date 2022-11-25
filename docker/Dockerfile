FROM python:3-alpine

COPY --chown=fileshare:fileshare docker/entrypoint /entrypoint
COPY --chown=fileshare:fileshare docker/start /start
COPY --chown=fileshare:fileshare . /app

WORKDIR /app

RUN set -ex && \
    apk add --no-cache --update libpq-dev && \
    addgroup -S -g 1000 fileshare && \
    adduser -S -u 1000 -s /bin/ash -G fileshare fileshare && \
    apk add --no-cache --virtual .build-deps gcc musl-dev && \
    su fileshare -c " \
      pip install pipenv && \
      export PATH=\$PATH:/home/fileshare/.local/bin && \
      pipenv install --system --deploy" && \
    apk del .build-deps gcc musl-dev && \
    chmod +x /entrypoint /start

USER fileshare

ENTRYPOINT ["/entrypoint"]

CMD ["/start"]
