ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists

# Use CWD
COPY ./app
RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]