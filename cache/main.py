"""Cache

This script allows the user to cache valid responses and can be executed by the
following:
    `python3 cache/main.py`

"""

import os
import sys
import socket
import time
from datetime import datetime

HOST = "localhost"
PORT = 9000
FILE_EXPIRE_TIME = 86400  # seconds in 24hrs
BUFFER_SIZE = 1024


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


def get_status_code(response_header):
    """Returns the status code found in response header.

    Args:
        response_header: Valid HTTP/1.1 response header

    Returns:
        HTTP status code (int)
    """
    status_line = response_header.split('\n')[0]
    return int(status_line.split(' ')[1])


def cache(filepath, filename, server_socket):
    """Reads in data from server socket and saves file to cache

    Args:
        filepath: Cached file path
        filename: Cached file name
        server_socket: Server socket instance

    Returns:
        None
    """
    if os.path.isfile("./files/" + filepath + '/' + filename):
        os.remove("./files/" + filepath + '/' + filename)
    os.makedirs("./files/" + filepath, exist_ok=True)
    with open("./files/" + filepath + "/" + filename, "wb") as f:
        while data := server_socket.recv(BUFFER_SIZE):
            f.write(data)


def send_200_response(header, filepath, filename, client_socket):
    """Sends 200 response to client with an HTTP/1.1 header and file as body.

    Args:
        header: HTTP header
        filepath: Path to file
        filename: File name
        client_socket: Client socket instance

    Returns:
        None
    """
    client_socket.send(header.encode())
    with open("./files/" + filepath + "/" + filename, "rb") as f:
        while data := f.read(BUFFER_SIZE):
            client_socket.send(data)


def main():
    # Bind proxy to socket and listen for requests from client
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((HOST, PORT))
    proxy_socket.listen(1)
    print(f"""Proxy listening on port {PORT}...""")

    while True:
        # Make TCP connection with client
        client_socket, client_address = proxy_socket.accept()

        # Receive request from client
        request = client_socket.recv(BUFFER_SIZE).decode()
        split_request = request.split("\r\n")
        request_info = split_request[0]
        host_info = split_request[1]
        _, host_info = host_info.split(' ')

        requested_file = request_info.split(' ')[1]
        server_host, server_port = host_info.split(':')
        file = f"""{server_host}_{server_port}""" + requested_file
        try:
            # Make TCP connection with server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_host, int(server_port)))
        except ConnectionRefusedError:
            response_header = "HTTP/1.1 523 Origin Is Unreachable\r\n\r"
            response_body = "files/errors/523.html"
            client_socket.send(response_header.encode())
            with open(response_body, "rb") as f:
                while data := f.read(BUFFER_SIZE):
                    client_socket.send(data)
            client_socket.shutdown(socket.SHUT_WR)
            sys.exit(1)
        if os.path.isfile("files/" + file):
            # File is cached, check if expired
            current_t = time.time()
            file_mt = os.path.getmtime("./files/" + file)
            if current_t - file_mt > FILE_EXPIRE_TIME:
                # File is expired, forward request to the server
                server_socket.send(request.encode())

                # Receive response
                server_response_header = server_socket.recv(
                    BUFFER_SIZE).decode()
                status_code = get_status_code(server_response_header)
                filepath, filename = file.rsplit('/', 1)
                if status_code == 200:
                    # Cache file and send response to client
                    cache(filepath, filename, server_socket)
                    send_200_response(
                        server_response_header,
                        filepath,
                        filename,
                        client_socket
                    )
                elif status_code == 404:
                    # Remove file from cache, forward response to client
                    os.remove("./files/" + file)
                    if not os.listdir("./files/" + filepath):
                        os.rmdir("./files/" + filepath)
                    client_socket.send(server_response_header.encode())
                    while data := server_socket.recv(BUFFER_SIZE):
                        client_socket.send(data)
                else:
                    # Forward response to client
                    client_socket.send(server_response_header.encode())
                    while data := server_socket.recv(BUFFER_SIZE):
                        client_socket.send(data)
            else:
                # File is not expired, send conditional GET
                last_modified = datetime.strftime(
                    datetime.fromtimestamp(file_mt),
                    "%a, %w %b %Y %H:%M:%S"
                )
                conditional_get = f"""GET {requested_file} HTTP/1.1\r
Host: {server_host}:{server_port}\r
If-modified-since: {last_modified} GMT\r
\r"""
                server_socket.send(conditional_get.encode())

                # Receive response
                server_response_header = server_socket.recv(
                    BUFFER_SIZE).decode()
                status_code = get_status_code(server_response_header)
                filepath, filename = file.rsplit('/', 1)
                if status_code == 200:
                    cache(filepath, filename, server_socket)

                content_len = os.stat("./files/" + file).st_size
                file_ext = file.rsplit('.', 1)
                content_type = get_content_type(file_ext)
                server_response_header = f"""HTTP/1.1 200 OK\r
Content-Length: {content_len}\r
Content-Type: {content_type}\r
\r"""
                send_200_response(
                    server_response_header,
                    filepath,
                    filename,
                    client_socket
                )
        else:
            # File is not cached, forward request to the server
            server_socket.send(request.encode())

            # Receive response
            server_response_header = server_socket.recv(BUFFER_SIZE).decode()
            status_code = get_status_code(server_response_header)
            if status_code == 200:
                # Cache file and send response
                filepath, filename = file.rsplit('/', 1)
                cache(filepath, filename, server_socket)
                send_200_response(
                    server_response_header,
                    filepath,
                    filename,
                    client_socket
                )
            else:
                # Forward response to client
                client_socket.send(server_response_header.encode())
                while data := server_socket.recv(BUFFER_SIZE):
                    client_socket.send(data)

        server_socket.close()
        client_socket.shutdown(socket.SHUT_WR)


if __name__ == '__main__':
    main()
