import requests
import os
from bottle import Bottle, redirect, request, abort, run
from urllib.parse import urlencode
import json
from beaker.middleware import SessionMiddleware
from uuid import uuid4

Oauth_url = os.environ.get("OAUTH_SERVER_URL")

app = Bottle()
_session_opts = {"session.type": "file", "session.data_dir": "./data", "session.auto": True}


def get_session():
    return request.environ.get("beaker.session")


@app.route("/start")
def start():
    state = str(uuid4()).replace("-", "")
    session = get_session()
    session["state"] = state
    res = requests.get(f"{Oauth_url}/pubkey")
    res.raise_for_status()
    data = res.json()
    redirect_url = "https://login.threefold.me"
    params = {
        "state": state,
        "appid": request.get_header("host"),
        "scope": json.dumps({"user": True, "email": True}),
        "redirecturl": "/callback",
        "publickey": data["publickey"].encode(),
    }
    params = urlencode(params)
    return redirect(f"{redirect_url}?{params}", code=302)


@app.route("/callback")
def callback():
    session = get_session()
    data = request.query.get("signedAttempt")
    res = requests.post(f"{Oauth_url}/verify", data={"signedAttempt": data, "state": session.get("state")})
    res.raise_for_status()
    return res.json()


app = SessionMiddleware(app, _session_opts)
run(app, host="0.0.0.0", port=8787)
