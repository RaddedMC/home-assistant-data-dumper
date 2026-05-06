ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install requirements
RUN \
    apk add --no-cache python3 py3-flask py3-requests

# Working directory
WORKDIR /

# Use CWD
COPY app /
COPY run.sh /
RUN chmod a+x /run.sh

CMD /run.sh