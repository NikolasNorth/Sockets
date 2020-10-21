# Sockets

### Description
Sockets implements a simplified web server and web downloader client. In response to a request, the server reads the 
contents of a named file and pushes it back over the same connection. Currently only GET requests using version 
`HTTP/1.1` are supported.

### How it works
The client will open a TCP connection to the server. The client will issue a request such as `GET /index.html HTTP/1.1` 
with an appropriate `Host:` header. The server will open this file relative to its current directory, read the contents, 
and send back the results. The client will save the file to disk to its own current directory, and close the connection.

### Sending a GET Request
**1. Open Terminal**

**2. Navigate to `Sockets` directory**

**3. Start the server**  
```commandline
python3 server.py
```

**4. Issue GET request from client**  
You can issue a GET request by either executing `client.py` script with or without a URL argument. If you choose not to 
enter a URL, you will be prompted to enter the localhost, port number and desired file name.  
  
**With URL:**  
```commandline
python3 client.py localhost:12000/server_files/index.html
```
  
**Without URL:**  
```commandline
python3 client.py

Hostname: localhost
Port Number: 12000
File: server_files/index.html
```

**Note:**  
* Since this runs on localhost, files located on the 'server' are stored under `server_files/` as to not get mixed up 
with the files downloaded to the client's filesystem. Currently there are some demonstration files stored under 
`server_files`, however feel free to use your own.
* Server is bound to port `12000`

### GET Request Errors
Currently the server only supports GET requests. Any other request will have a `501 Method Not Implemented` error 
issued as a response.

Similarly, the server only supports version `HTTP/1.1`. Any other version will have a `505 Version Not Supported` error 
issued as a response. 
