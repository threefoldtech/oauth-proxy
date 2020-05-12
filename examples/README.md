# App server examples

Here you will find two example app that use the oauth server written in python and crystal.

Make sure to set `OAUTH_SERVER_URL` environment variable with Oauth server address before running any of the examples.

## Python example

To run the example:

```bash
python3 example.py
```

## Crystal example

Change directory to `crystal_example` and run the following to install the deps:

```bash
shards install
```

Then start the server:

```bash
crystal run example.cr
```
