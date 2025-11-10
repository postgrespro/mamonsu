# Стейдж нужен для того, что бы потом скопировать из него энтрипоинт нужной версии, т.к. в --from= нельзя использовать env
ARG POSTGRES_VERSION=15
FROM postgres:${POSTGRES_VERSION} AS postgres_base

FROM debian:bookworm-slim AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    software-properties-common \
    make \
    dpkg-dev \
    debhelper \
    build-essential \
    python3-dev \
    python3-setuptools && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN make deb

FROM postgres:${POSTGRES_VERSION}

COPY --from=builder /app/mamonsu*.deb /tmp/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-setuptools \
    sudo \
    && rm -rf /var/lib/apt/lists/*
RUN dpkg -i /tmp/mamonsu*.deb || apt-get install -f -y && \
    rm /tmp/mamonsu*.deb
RUN mkdir -p /var/log/mamonsu && \
    chown postgres:postgres /var/log/mamonsu && \
    chmod 755 /var/log/mamonsu

COPY --from=postgres_base /usr/local/bin/docker-entrypoint.sh /usr/local/bin/
COPY ./tests/service-scripts/mamonsu-pg/mamonsu.conf /etc/mamonsu/agent.conf
COPY ./tests/service-scripts/mamonsu-pg/entrypoint.sh ./tests/service-scripts/mamonsu-pg/init_mamonsu_in_zbx.sh /app/

RUN chmod +x /app/entrypoint.sh /app/init_mamonsu_in_zbx.sh

ENTRYPOINT ["/app/entrypoint.sh"]