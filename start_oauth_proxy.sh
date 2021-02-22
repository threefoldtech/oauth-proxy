#!/bin/bash
python3 /oauth-proxy/create_keys.py

port=$OAUTH_PROXY_PORT
uwsgi --http :${port} -w server