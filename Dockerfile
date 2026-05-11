ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install requirements
RUN \
    apk add --no-cache python3 py3-flask py3-requests git npm

# Clone frontend
RUN \
    mkdir build \
    && git clone https://github.com/RaddedMC/home-assistant-data-dumper-frontend build/ \
    && cd build \
    && npm i \
    && npm run build

# # Copy out frontend and remove build files
RUN \
    mkdir /frontend \
    && mv /build/dist/* /frontend \
    && rm -rf /build

# Copy addon source
WORKDIR /
COPY app/ /
COPY run.sh /
RUN chmod a+x /run.sh

# Run
CMD /run.sh