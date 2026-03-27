ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set environment variables
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install requirements
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
    && pip3 install --no-cache-dir \
        Flask \
        requests \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Use CWD
COPY app /app
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]