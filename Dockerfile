ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements
RUN \
    apk add --no-cache \
    python3 \
    py3-pip

# Use CWD
COPY app /app
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]