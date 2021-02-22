import nacl.signing
import os

k = nacl.signing.SigningKey.generate()  # Ususally the key is generated using a seed
res = k.encode(encoder=nacl.encoding.Base64Encoder).decode()  # What should be in the file
print("Private key generated")

# write res to file
with open("/opt/priv.key", "w+") as f:
    f.write(res)
