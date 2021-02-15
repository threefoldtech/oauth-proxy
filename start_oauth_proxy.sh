#!/bin/bash
port=$OAUTH_PROXY_PORT

uwsgi --http :${port} -w server