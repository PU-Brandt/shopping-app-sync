#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting ShoppingSync Control add-on"
python3 /addon_server.py
