import socket

HOST = "0.0.0.0"
PORT = 8080

# sever socket
s_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# port
s_socket.bind((HOST, PORT))
s_socket.listen(10)
print(f"listening on port {PORT}")

# connection with client
while True:
        c_socket, c_address = s_socket.accept()
        print(c_socket, c_address)
        req = c_socket.recv(1024).decode()
        print(req)
