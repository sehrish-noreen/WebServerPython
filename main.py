import socket
import os

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
        print("connection from client: ", c_address)
        req = c_socket.recv(1024).decode('utf-8') # string conversion
        print(f"raw request {req}")

        # skipping empty requests
        if not req.strip():
            c_socket.close()
            continue

        # pass header
        headers = req.split('\r\n')
        request_line = headers[0].split()
        if len(request_line)<2:
            c_socket.close()
            continue

        http_method = request_line[0]
        path = request_line[1]

        # default response
        response = 'HTTP/1.1 400 Bad Request\r\n\r\n'

        # get method response
        if http_method == 'GET':
            if path == '/':
                try:
                    with open('data.json', 'r') as in_file:
                        data = in_file.read().strip()
                    data = '[\n' + data + '\n]' if data else '[]'
                    response = ('HTTP/1.1 200 OK\r\n\r\n' + data)
                except FileNotFoundError:
                    response = 'HTTP/1.1 404 Not Found\r\n\r\nFile Not Found'

        # delete method response
        elif http_method == 'DELETE':
            try:
                os.remove('data.json')
                response = 'HTTP/1.1 200 Ok\r\n\r\nFile is deleted'
            except FileNotFoundError:
                response = 'HTTP/1.1 404 Not Found\r\n\r\nFile does not exist, could not delete'


        # post method
        elif http_method == 'POST':
            if path == '/':
                body = ''
                # seprate body from headers
                if '\r\n\r\n' in req:
                    _, _, body = req.partition('\r\n\r\n')
                    body = body.strip()
                    # print(f"body recieved  {repr(body)}") # debug
                try:
                    if os.path.exists('data.json'):
                        nonempty = os.path.getsize('data.json') > 0
                    else:
                        nonempty = False
                    with open('data.json', 'a') as out_file:
                        if nonempty:
                            out_file.write(',\n' + body)
                        else:
                            out_file.write(body)
                    response = 'HTTP/1.1 200 OK\r\n\r\nFile updated/created'
                except Exception as e:
                    response = f'HTTP/1.1 500 Internal Server Error\r\n\r\n{e}'

        c_socket.sendall(response.encode('utf-8'))
        c_socket.close()
