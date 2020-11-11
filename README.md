# Sockets

## Description
Sockets implements a simplified web server and web downloader client. In response to a request, the server reads the 
contents of a named file and pushes it back over the same connection. Currently only GET requests using version 
`HTTP/1.1` are supported.

## How it works
### Without Cache
The client will open a TCP connection to the server. The client will issue a request such as `GET /index.html HTTP/1.1` 
with an appropriate `Host:` header. The server will open this file relative to its `files/` directory, read the contents, 
and send back the results. The client will save the file to disk to its own `files/` directory, and close the connection. 

### With Cache
The client will open a TCP connection to the proxy. The client will issue a GET request. Upon receiving the request, the
proxy checks to see if the file is stored in cache. That is, within its `files/` directory. If it's not, then the GET 
request is forwarded to the server. If it is then the proxy checks to see if the file is expired. If the file is expired, 
it forwards the GET request to the server. Upon receiving the response from the server, if a 404, 501 or 505 error 
occured, then the response is forwarded to the client. Otherwise, the cache downloads the file and sends it the client 
client as a response. If the file was not expired, then the proxy sends a conditional GET to the server to see if the 
file was updated. If it is then it receives the latest copy of the file and forwards it to the client. Otherwise, it 
receives a `304 Not Modified` as a response from the server and sends its cached copy to the client.

## Sending a GET Request
### Without Cache
#### 1. Start server
- `python3 server/main.py`

#### 2. Send request
- `python3 client/main.py localhost:8000/index.html`

If the response is `200` then `index.html` should be found within `client/files/`.

### With Cache
#### 1. Start server
- `python3 server/main.py`

#### 2. Start proxy
- `python3 cache/main.py`

#### 3. Send request
- `python3 client/main.py -proxy localhost:9000 localhost:8000/index.html`

If the response is `200` then `index.html` should be found within `cache/files/` and `client/files`.

## GET Request Errors
Currently the server only supports GET requests. Any other request will have a `501 Method Not Implemented` error 
issued as a response.

Similarly, the server only supports version `HTTP/1.1`. Any other version will have a `505 Version Not Supported` error 
issued as a response. 

If a request is sent to the server via a proxy and the server is not available, a `523 Origin Is Unreachable` error will 
be sent back the the client.
