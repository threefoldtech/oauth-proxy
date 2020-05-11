import nacl.encoding
import nacl.exceptions
import nacl.signing
import requests
import json
import base64
import argparse

from bottle import Bottle, redirect, request, abort, run
from urllib.parse import urlencode
from nacl.public import Box

from uuid import uuid4

from beaker.middleware import SessionMiddleware

LOGIN_URL = "/login"
CALLBACK_URL = "/callback"
KEY_PATH = "/opt/priv.key"

_session_opts = {"session.type": "file", "session.data_dir": "./data", "session.auto": True}

with open(KEY_PATH) as kp:
    PRIV_KEY = nacl.signing.SigningKey(kp.read(), encoder=nacl.encoding.Base64Encoder)

app = Bottle()


def get_session():
    return request.environ.get("beaker.session")


def frmt_response(session):
    return {"email": session["email"], "username": session["username"]}


@app.route(LOGIN_URL)
def login():
    session = get_session()
    if not session.get("authorized", False):
        state = str(uuid4()).replace("-", "")
        session["state"] = state
        redirect_url = "https://login.threefold.me"
        public_key = PRIV_KEY.verify_key

        params = {
            "state": state,
            "appid": request.get_header("host"),
            "scope": json.dumps({"user": True, "email": True}),
            "redirecturl": CALLBACK_URL,
            "publickey": public_key.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder),
        }
        params = urlencode(params)
        return redirect(f"{redirect_url}?{params}", code=302)
    else:
        return frmt_response(session)


@app.route(CALLBACK_URL)
def callback():

    data = request.query.get("signedAttempt")

    if not data:
        return abort(400, "signedAttempt parameter is missing")

    data = json.loads(data)

    if "signedAttempt" not in data:
        return abort(400, "signedAttempt value is missing")

    username = data["doubleName"]

    if not username:
        return abort(400, "DoubleName is missing")

    res = requests.get(f"https://login.threefold.me/api/users/{username}", {"Content-Type": "application/json"})
    if res.status_code != 200:
        return abort(400, "Error getting user pub key")

    pub_key = nacl.signing.VerifyKey(res.json()["publicKey"], encoder=nacl.encoding.Base64Encoder)

    # verify data
    signedData = data["signedAttempt"]

    verifiedData = pub_key.verify(base64.b64decode(signedData)).decode()

    data = json.loads(verifiedData)

    if "doubleName" not in data:
        return abort(400, "Decrypted data does not contain (doubleName)")

    if "signedState" not in data:
        return abort(400, "Decrypted data does not contain (state)")

    if data["doubleName"] != username:
        return abort(400, "username mismatch!")

    # verify state
    state = data["signedState"]
    session = get_session()
    if state != session["state"]:
        return abort(400, "Invalid state. not matching one in user session")

    nonce = base64.b64decode(data["data"]["nonce"])
    ciphertext = base64.b64decode(data["data"]["ciphertext"])

    try:
        box = Box(PRIV_KEY.to_curve25519_private_key(), pub_key.to_curve25519_public_key())
        decrypted = box.decrypt(ciphertext, nonce)
    except nacl.exceptions.CryptoError:
        return abort(400, "Error decrypting data")

    try:
        result = json.loads(decrypted)
    except json.JSONDecodeError:
        return abort(400, "3bot login returned faulty data")

    if "email" not in result:
        return abort(400, "Email is not present in data")

    email = result["email"]["email"]

    sei = result["email"]["sei"]
    res = requests.post(
        "https://openkyc.live/verification/verify-sei",
        headers={"Content-Type": "application/json"},
        json={"signedEmailIdentifier": sei},
    )

    if res.status_code != 200:
        return abort(400, "Email is not verified")

    session["username"] = username
    session["email"] = email
    session["authorized"] = True
    session["signedAttempt"] = signedData
    return frmt_response(session)


parser = argparse.ArgumentParser()
parser.add_argument("--host", help="Host of the server", default="0.0.0.0")
parser.add_argument("--port", help="Port of the server", default=8080)
args = parser.parse_args()
app = SessionMiddleware(app, _session_opts)
run(app, host=args.host, port=args.port)
