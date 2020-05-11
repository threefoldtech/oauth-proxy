# Oauth proxy

This server will handle 3bot connect authentication and verification, eliminating the need to handle it in other services that are using `3bot connect`.

## Running the server

The application is a simple bottle server, and it can be run using `uwsgi`as follows:

```bash
uwsgi --http :{port number} -w server
```

## Using the oauth server in your application

In order to use this server the application server must have follwing two endpoints:

- An endpoint that gets the public key from the Oauth server and redirects the user to `3bot connect` correct url
- A callback endpoint that receives the data from `3bot connect` and sends it to Oauth server to verify

You can find an [example](exmaple.py) python script that implements both.

To run the example set `OAUTH_SERVER_URL` environment variable with Oauth server address and run the script:

```bash
python3 example.py
```
