#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Home Assistant Data Dumper"

exec python3 -m app.main