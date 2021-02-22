FROM ubuntu:20.04
      ENV LC_ALL C.UTF-8
      ENV LANG C.UTF-8
RUN apt-get update && apt-get install -y \
    python3 python3-pip

RUN mkdir /oauth-proxy
COPY . /oauth-proxy/
WORKDIR /oauth-proxy
RUN cd /oauth-proxy && pip3 install -r requirements.txt

ENV OAUTH_PROXY_PORT=8080

RUN chmod  +x  /oauth-proxy/start_oauth_proxy.sh
ENTRYPOINT ["/oauth-proxy/start_oauth_proxy.sh" ]