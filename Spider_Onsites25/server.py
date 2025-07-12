import socket 
import threading

PORT = 5500 
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

print(f"[SERVER IP] {SERVER}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients=[]
print(f"[STARTING]Server is starting on {SERVER}:{PORT}")

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                msg = message.encode('utf-8')
                length = str(len(msg)).encode('utf-8')
                length += b' ' * (64 - len(length))
                client.send(length)
                client.send(msg)
            except:
                client.close()
                clients.remove(client)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(conn)
    
    #client_id = f"User{len(clients)+1}"
    #clients[conn] = client_id
    #conn.send(f"Welcome {client_id}!".encode(FORMAT))
    
    
    connected = True
    while connected:
       try:
            msg_length = conn.recv(64).decode(FORMAT).strip()
            if not msg_length:
                continue
            msg_length = int(msg_length)
            
            msg = conn.recv(msg_length).decode('utf-8')
            
            if msg == "byeBro":
                connected = False
            else:
                print(f"[{addr}] {msg}")
                broadcast(msg, conn)
       except:
            break

    clients.remove(conn)
    conn.close()
    

       

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print(f"[SERVER IP]{SERVER}")
print("[STARTING] Server is starting...")
start()
