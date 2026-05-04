ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install requirements
RUN \
    apk add --no-cache python3 py3-flask

# Working directory
WORKDIR /

# Use CWD
COPY app /

CMD python3 app.py