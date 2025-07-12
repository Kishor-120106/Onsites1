import socket
import threading
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

PORT = 5500
SERVER = "192.168.193.67"
FORMAT = 'utf-8'
ADDR = (SERVER, PORT)


with open("secret.key", "rb") as f:
    key = f.read()
assert len(key) == 32  

print(f"[DEBUG] Loaded key of length: {len(key)} bytes")
if len(key) != 32:
    raise ValueError("❌ Invalid key length! Expected 32 bytes for AES-256.")

encryption_enabled = False


def encrypt_message(message, key):
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode('utf-8')

# AES Decryption
def decrypt_message(ciphertext_b64, key):
    try:
        ciphertext = base64.b64decode(ciphertext_b64.encode('utf-8'))
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode('utf-8')
    except:
        return None

print(f"[CONNECTING] Connecting to server at {SERVER}:{PORT}...")
socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect(ADDR)
print("[CONNECTED] Connected to server.")

def receive():
    while True:
        try:
            msg_length = socket_client.recv(64).decode(FORMAT).strip()
            if not msg_length:
                continue
            msg_length = int(msg_length)
            msg = socket_client.recv(msg_length).decode(FORMAT)
            if msg:
                if msg.startswith("[ENCRYPTED] "):
                    payload = msg[len("[ENCRYPTED] "):]
                    sender, encrypted_message = payload.split(":", 1)
                    decrypted = decrypt_message(encrypted_message, key)
                    if decrypted:
                        print(f"[DECRYPTED] {sender}: {decrypted}")
                    else:
                        print("[UNABLE TO DECRYPT]", msg)
                else:
                    print(msg)
        except:
            print("[ERROR] You have been disconnected.")
            socket_client.close()
            break

def send():
    global encryption_enabled
    username = input("Enter your username: ")
    while True:
        try:
            msg = input()
            if msg.lower() == "/encrypt on":
                encryption_enabled = True
                print("[ENCRYPTION] Enabled.")
                continue
            elif msg.lower() == "/encrypt off":
                encryption_enabled = False
                print("[ENCRYPTION] Disabled.")
                continue
            elif msg == "byeBro":
                print("[DISCONNECTING] Closing connection.")
                socket_client.close()
                break

            if encryption_enabled:
                encrypted_message = encrypt_message(msg, key)
                message_to_send = f"[ENCRYPTED] {username}:{encrypted_message}"
            else:
                message_to_send = f"{username}:{msg}"

            message = message_to_send.encode(FORMAT)
            length = str(len(message)).encode(FORMAT)
            length += b' ' * (64 - len(length))
            socket_client.send(length)
            socket_client.send(message)

        except:
            print("[ERROR] Failed to send message.")
            break

recv_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=send)
recv_thread.start()
send_thread.start()
