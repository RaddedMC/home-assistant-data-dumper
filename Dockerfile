ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install requirements
RUN \
    apk add --no-cache python3 py3-flask py3-requests git npm

# Build frontend
COPY frontend/ /frontend
WORKDIR /frontend
RUN \
    npm i \
    && npm run build

# Copy addon source
WORKDIR /
COPY app/ /
COPY run.sh /
RUN chmod a+x /run.sh

# Run
CMD /run.sh