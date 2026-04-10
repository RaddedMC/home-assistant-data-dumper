ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:bookworm
FROM ${BUILD_FROM}

# Install requirements
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /data

# Use CWD
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]