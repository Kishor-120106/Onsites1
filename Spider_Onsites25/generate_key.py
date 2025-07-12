
import os

key = os.urandom(32)  
print(f"Key length: {len(key)} bytes") 
with open("secret.key", "wb") as f:
    f.write(key)
print("✅ 32-byte AES key saved to secret.key")
