ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install requirements
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 python3-flask \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /

# Use CWD
COPY app /

CMD [ "python3", "main.py" ]