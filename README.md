# Sockets

To run load balancer for **Assignment 4**, see sections below titled: "With Load Balancer".

## Description
Sockets implements a simplified web server and web downloader client. In response to a request, the server reads the 
contents of a named file and pushes it back over the same connection. Currently only GET requests using version 
`HTTP/1.1` are supported.

## How it works
### Without Cache
The client will open a TCP connection to the server. The client will issue a `GET` request such as `GET /index.html HTTP/1.1` 
with an appropriate `Host:` header. The server will open this file relative to its `files/` directory, read the contents, 
and send back the results. The client will save the file to disk to its own `files/` directory, and close the connection. 

### With Cache
The client will open a TCP connection to the proxy. The client will issue a `GET` request. Upon receiving the request, the
proxy checks to see if the file is stored in cache. That is, within its `files/` directory. If it's not, then the GET 
request is forwarded to the server. If it is then the proxy checks to see if the file is expired. If the file is expired, 
it forwards the GET request to the server. Upon receiving the response from the server, if a 404, 501 or 505 error 
occured, then the response is forwarded to the client. Otherwise, the cache downloads the file and sends it the client 
client as a response. If the file was not expired, then the proxy sends a conditional GET to the server to see if the 
file was updated. If it is then it receives the latest copy of the file and forwards it to the client. Otherwise, it 
receives a `304 Not Modified` as a response from the server and sends its cached copy to the client.

### With Load Balancer
The client will open a TCP connection to the load balancer. The client will issue a `GET` request. Upon receiving the 
request, the load balancer will run a 'performance test' on the servers. A simple transfer request will be made to each 
server and the time to complete each request will be measured. After running the performance test, your load balancer 
will rank the servers in terms of their transfer times. The number of client requests sent to different servers will be 
proportional to its performance. The higher performing servers will receive relatively more requests compared to the 
lower performing ones.

When a client issues a request, the load balancer will select a server to handle the request depending on a sorting 
criteria mentioned above. The load balancer will redirect the client to the server by returning a `301 Moved Permanently` 
response to the client with the `Location` header set to the selected server to retrieve the file.

The load balancer will periodically run the performance test and update the the priority for each server depending on 
the results.

When performing a performance test, if the load balancer notices a server is unavailable then it will be removed from 
the list of available servers and no clients will be redirected.

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

### With Load Balancer
#### 1. Start all servers
- `cd server/`
- `python3 server8000.py`
- `python3 server8100.py`
- `python3 server8200.py`

#### 2. Start load balancer
- `cd balancer/`
- `python3 main.py`

#### 3. Send request
- `cd client/`
- `python3 main.py -balancer localhost:8000/index.html`

## GET Request Errors
Currently the server only supports GET requests. Any other request will have a `501 Method Not Implemented` error 
issued as a response.

Similarly, the server only supports version `HTTP/1.1`. Any other version will have a `505 Version Not Supported` error 
issued as a response. 

If a request is sent to the server via a proxy and the server is not available, a `523 Origin Is Unreachable` error will 
be sent back the the client.
