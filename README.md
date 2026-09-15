# Python Web Server

this web server is built for learning purposes only.

## Requirements

- Python 3.x
- [HTTPie](https://httpie.io/) (for the `http` command used in the examples)

## Run server

```bash
python main.py
```

## API Examples

### GET data

```console
$ http GET localhost:8080/
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

[
    { "id": 40, "name": "noreen" },
    { "id": 30, "name": "sehrish" },
    { "id": 20, "name": "maria" }
]
```

### POST data

```console
$ http POST localhost:8080/ id:=10 name=ali
HTTP/1.1 201 Created
Content-Type: text/plain; charset=utf-8

Data added successfully
```

### DELETE data

```console
$ http DELETE localhost:8080
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8

File has been Deleted
```
