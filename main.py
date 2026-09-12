from json.decoder import JSONDecodeError

from builtins import FileNotFoundError, OSError

import socket
import os
import json

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
        req = c_socket.recv(1024).decode('utf-8') # fix todo

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
                    # read data file
                    try:
                        with open('data.json', 'r', encoding='utf-8') as file:
                            content = file.read().strip()
                            data = json.loads(content) if content else []
                    except FileNotFoundError:
                        data = []

                    # convert data to json
                    body = json.dumps(data, indent=2)
                    response = f'HTTP/1.1 200 OK\r\nContent-Type:application/json\r\nContent-Length:{len(body)}\r\n\r\n{body}'

                except (OSError, JSONDecodeError) as e:
                    response = f'HTTP/1.1 500 Internal Server Error\r\n\r\nFile error: {e}'
                except FileNotFoundError:
                    response = 'HTTP/1.1 404 Not Found\r\n\r\nFile not found'

        # delete method response
        elif http_method == 'DELETE':
            try:
                os.remove('data.json')
                response = 'HTTP/1.1 200 OK\r\n\r\nFile is deleted'
            except FileNotFoundError:
                response = 'HTTP/1.1 404 Not Found\r\n\r\nFile does not exist, could not delete'
            except OSError as e:
                response = f'HTTP/1.1 500 Internal Server Error\r\n\r\nFile error:{e}'


        # post method
        elif http_method == 'POST':
            if path=='/':
                try:
                    if '\r\n\r\n' not in req:
                        response = (
                            'HTTP/1.1 400 Bad Request\r\n\r\n'
                            '\r\n'
                            'Missing Body'
                        )
                    else:
                        _, body = req.split('\r\n\r\n', 1)
                        body = body.strip()
                        print("body: ", body)
                        new_data = json.loads(body)

                        # reading existing data from json file
                        try:
                            with open('data.json', 'r', encoding='utf-8') as body_file:
                                content= body_file.read().strip()
                                data = json.loads(content) if content else []
                        except FileNotFoundError:
                                data = []
                        data.append(new_data)

                        # writing updated data to json file
                        with open('data.json', 'w', encoding='utf-8') as out_file:
                            json.dump(data, out_file, indent=2)
                        response = 'HTTP/1.1 201 Created\r\n\r\nData added successfully'

                except json.JSONDecodeError:
                    response = 'HTTP/1.1 400 Bad Request\r\n\r\nInvalid Json'

                except OSError as e:
                    response = f'HTTP/1.1 500 Internal Server Error\r\n\r\nFile error:{e}'









        c_socket.sendall(response.encode('utf-8'))
        c_socket.close()
