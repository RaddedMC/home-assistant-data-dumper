ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements
RUN \
    apk add --no-cache \
        python3 \
        py3-flask \

# Use CWD
COPY ./app

CMD [ "python", "app.py" ]