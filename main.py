from json.decoder import JSONDecodeError
from builtins import FileNotFoundError, OSError

import socket
import os
import json

HOST = "0.0.0.0"
PORT = 8080
DATA_FILE = "data.json"

# sever socket
s_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# port
s_socket.bind((HOST, PORT))
s_socket.listen(10)
print(f"listening on port {PORT}")

# response template function
def build_response(status, body, content_type="text/plain"):
    body_bytes = body.encode("utf-8")
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("utf-8")
    return head + body_bytes

# connection with client
while True:
        c_socket, c_address = s_socket.accept()
        print("connection from client: ", c_address)

        # reading header and body bytes from client
        raw = b""
        while b"\r\n\r\n"not in raw:
            chunk = c_socket.recv(4096)
            if not chunk:
                break
            raw = raw + chunk

        # handle empty request
        if not raw.strip():
            c_socket.close()
            continue

        header_bytes, _, body_bytes = raw.partition(b"\r\n\r\n")

        content_length = 0
        for line in header_bytes.decode("utf-8", errors="ignore").split("\r\n"):
            if line.lower().startswith("content-length"):
                content_length = int(line.split(":", 1)[1].strip())
                break

        while len(body_bytes) < content_length:
            chunk = c_socket.recv(4096)
            if not chunk:
                break
            body_bytes = body_bytes + chunk

        # build request
        req = (header_bytes + b"\r\n\r\n" + body_bytes).decode("utf-8", errors="ignore")

        # parse request, header
        headers = req.split("\r\n")
        request_line = headers[0].split()
        if len(request_line) < 2:
            c_socket.close()
            continue

        http_method = request_line[0].upper()
        path = request_line[1]

        # default response
        response = build_response("400 Bad Request", "Bad Request")

        # get method response
        if http_method == 'GET':
            if path == '/':
                try:
                    # read data file
                    try:
                        with open(DATA_FILE, 'r', encoding='utf-8') as file:
                            content = file.read().strip()
                            data = json.loads(content) if content else []
                    except FileNotFoundError:
                        data = []
                    # convert data to json
                    body = json.dumps(data, indent=2)
                    response = build_response("200 OK", body, "application/json")
                except (OSError, JSONDecodeError) as e:
                    response = build_response("500 Internal Server Error", f"File error: {e}")

        # delete method response
        elif http_method == 'DELETE':
            try:
                os.remove(DATA_FILE)
                # response = 'HTTP/1.1 200 OK\r\n\r\nFile is deleted'
                response = build_response("200 OK", "File has been Deleted")
            except FileNotFoundError:
                response = build_response("404 Not Found", "File does not exist, could not delete")
            except OSError as e:
                response = build_response("500 Internal Server Error", f"File error: {e}")

        # post method
        elif http_method == 'POST':
            if path=='/':
                if not body_bytes:
                    response = build_response("400 Bad Request", "Missing body")
                else:
                    body = body_bytes.decode("utf-8").strip()
                    print("body: ", body)
                    # parsing incoming json data
                    try:
                        new_data = json.loads(body)
                    except JSONDecodeError:
                        response = build_response("400 Bad Request", "Invalid Json")
                    else:
                        # reading existing data from json file
                        try:
                            with open(DATA_FILE, 'r', encoding='utf-8') as body_file:
                                content= body_file.read().strip()
                                data = json.loads(content) if content else []
                        except FileNotFoundError:
                                data = []
                                # backup file in case existing file is corrupt, and start new file
                        except json.JSONDecodeError:
                            os.rename(DATA_FILE, DATA_FILE + ".bak")
                            data = []
                        # append new data into file and save
                        data.append(new_data)
                        # writing updated data to json file
                        try:
                            with open(DATA_FILE, 'w', encoding='utf-8') as out_file:
                                json.dump(data, out_file, indent=2)
                            response = build_response("201 Created", "Data added successfully")
                        except OSError as e:
                            response = build_response("500 Internal Server Error", f"File error: {e}")
            else:
                response = build_response("404 Not Found", "File not found")
        else:
            response = build_response("405 Method Not Allowed", "Method not allowed")
        # send response to clients
        c_socket.sendall(response)
        c_socket.close()
