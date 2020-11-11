"""Web Server

This script allows the user to start a server and can be executed by the
following:
    `python3 server/main.py`

This script requires python3 to be installed.
"""

import socket
import os
from datetime import datetime

HOST = "localhost"
PORT = 8000
BUFFER_SIZE = 1024


def get_content_length(file):
    """Returns the size (in bytes) of a file.

    Args:
        file: Filename (relative to server/)

    Returns:
        Size (in bytes) of file.
    """
    return os.stat(file).st_size


def get_content_type(file_ext):
    """Returns the content type of a file.

    Args:
        file_ext: File extension

    Returns:
        Content type associated with file extension. Default is "text/html".
    """
    if file_ext in ["jpg", "jpeg"]:
        return "image/jpeg"
    elif file_ext == "gif":
        return "image/gif"
    else:
        return "text/html"


def main():
    """Main function of the script.

    TCP socket will be created and bound to the specified port number on host.
    The server will listen to for incoming TCP requests. When a valid request
    for a file is received, a response will be sent back to the client with the
    file as payload. If the request is not valid, or requested file does not
    exist then an appropriate error code will be sent back as response.

    If a client uses a version other than HTTP/1.1 in their request, a 505
    error will be sent as a response.
    If a client uses a request method other than GET, a 501 error will be
    sent as a response.
    If a client requests a file that does not exist, a 404 error will be sent
    as a response.
    Otherwise, the requested file will be sent back, along with 202 status code.

    Returns:
        None
    """
    # Bind server to socket and listen for requests
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"""Server listening on port {PORT}...""")

    while True:
        # Make TCP connection with client
        client_socket, client_address = server_socket.accept()

        # Receive request from client
        request = client_socket.recv(BUFFER_SIZE).decode()
        split_request = request.split('\n')

        request_line = split_request[0]
        method, requested_file, protocol = request_line.split(' ')
        file = "./files" + requested_file
        file_ext = file.rsplit('.', 1)[-1]

        # Prepare response
        if protocol.strip('\r') != "HTTP/1.1":
            response_header = "HTTP/1.1 505 Version Not Supported\r\n\r"
            response_body = "files/errors/505.html"
        elif method != "GET":
            response_header = "HTTP/1.1 501 Method Not Implemented\r\n\r"
            response_body = "files/errors/501.html"
        elif os.path.isfile(file):
            server_last_modified_str = datetime.strftime(
                datetime.fromtimestamp(os.path.getmtime(file)),
                "%a, %w %b %Y %H:%M:%S"
            )
            if len(split_request) == 4:
                # Conditional GET
                # Get datetime for last modification
                server_last_modified_dt = datetime.strptime(
                    server_last_modified_str,
                    "%a, %w %b %Y %H:%M:%S"
                )
                # Retrieve date from request string
                if_modified_date = split_request[2].split(' ', 1)[1]
                if_modified_date = if_modified_date.rsplit(' ', 1)[0]
                client_last_modified_dt = datetime.strptime(
                    if_modified_date,
                    "%a, %w %b %Y %H:%M:%S"
                )
                if client_last_modified_dt < server_last_modified_dt:
                    response_header = f"""HTTP/1.1 200 OK\r
Last-Modified: {server_last_modified_str}\r
\r"""
                    response_body = file
                else:
                    response_header = f"""HTTP/1.1 304 Not Modified\r
Last-Modified: {server_last_modified_str}\r
\r"""
                    response_body = None
            else:
                content_length = get_content_length(file)
                content_type = get_content_type(file_ext)
                response_header = f"""HTTP/1.1 200 OK\r
Content-Length: {content_length}\r
Content-Type: {content_type}\r
\r"""
                response_body = file
        else:
            response_header = """HTTP/1.1 404 Not Found\r\n\r"""
            response_body = "files/errors/404.html"

        # Send response
        client_socket.send(response_header.encode())
        if response_body:
            with open(response_body, "rb") as file:
                data = file.read(BUFFER_SIZE)
                while data:
                    client_socket.send(data)
                    data = file.read(BUFFER_SIZE)
        client_socket.shutdown(socket.SHUT_WR)


if __name__ == '__main__':
    main()
