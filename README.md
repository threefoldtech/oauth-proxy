# Oauth proxy

This server will handle 3bot connect authentication and verification, eliminating the need to handle it in other services that are using 3bot connect.

When the server recieves a authentication request it will redirect to 3bot connect and if the login is successful it will ensure the validity of the data before returning the user email to the server.

## Running the server

The application is a simple bottle server, and it can be run as follows:

```bash
python3 server.py --port {port_number}
```

To check available config:

```bash
pyhon3 server.py -h
```
