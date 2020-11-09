import os
import socket
import time
from datetime import datetime

HOST = "localhost"
PORT = 9000
FILE_EXPIRE_TIME = 120  # seconds


def is_file_cached(filepath):
    """Checks to see if given file is stored in cache.

    Args:
        filepath: Path to file stored in cache (without leading slash '/')
            eg: localhost_8000/styles/main.css

    Returns:
        If yes, returns True
        If no, returns False
    """
    return os.path.isfile("files/" + filepath)


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
        while data := server_socket.recv(1024):
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
        while data := f.read(1024):
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

        # Process request from client
        request = client_socket.recv(1024).decode()
        split_request = request.split("\r\n")
        request_info = split_request[0]
        host_info = split_request[1]
        _, host_info = host_info.split(' ')

        # Server host, port and requested file
        requested_file = request_info.split(' ')[1]
        server_host, server_port = host_info.split(':')
        file = f"""{server_host}_{server_port}""" + requested_file

        # Make TCP connection with server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_host, int(server_port)))

        if is_file_cached(file):
            # Check if file in cache is expired
            current_t = time.time()
            file_mt = os.path.getmtime("./files/" + file)
            if current_t - file_mt > FILE_EXPIRE_TIME:
                # Forward request to server
                server_socket.send(request.encode())

                # Extract status code from server response
                server_response_header = server_socket.recv(1024).decode()
                status_code = get_status_code(server_response_header)
                filepath, filename = file.rsplit('/', 1)
                if status_code == 200:
                    # Store file in cache
                    cache(filepath, filename, server_socket)
                    # Send response to client
                    send_200_response(
                        server_response_header,
                        filepath,
                        filename,
                        client_socket
                    )
                    # TESTED
                elif status_code == 404:
                    os.remove("./files/" + file)
                    if not os.listdir("./files/" + filepath):
                        os.rmdir("./files/" + filepath)
                    client_socket.send(server_response_header.encode())
                    while data := server_socket.recv(1024):
                        client_socket.send(data)
                    # TESTED
                else:
                    client_socket.send(server_response_header.encode())
                    while data := server_socket.recv(1024):
                        client_socket.send(data)
                    # TESTED
            else:
                last_modified = datetime.strftime(
                    datetime.fromtimestamp(file_mt),
                    "%a, %w %b %Y %H:%M:%S"
                )
                conditional_get = f"""GET {requested_file} HTTP/1.1\r
Host: {server_host}:{server_port}\r
If-modified-since: {last_modified} GMT\r
\r"""
                server_socket.send(conditional_get.encode())
                # Extract status code from response
                server_response_header = server_socket.recv(1024).decode()
                print(server_response_header)
                status_code = get_status_code(server_response_header)
                filepath, filename = file.rsplit('/', 1)
                if status_code == 200:
                    cache(filepath, filename, server_socket)
                content_len = os.stat("./files/" + file).st_size
                content_type = 'text/html'
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
            # Forward request to server
            server_socket.send(request.encode())

            # Extract status code from server response
            server_response_header = server_socket.recv(1024).decode()
            status_code = get_status_code(server_response_header)
            if status_code == 200:
                filepath, filename = file.rsplit('/', 1)
                # Store file in cache
                cache(filepath, filename, server_socket)
                # Send response to client
                send_200_response(
                    server_response_header,
                    filepath,
                    filename,
                    client_socket
                )
            else:
                # Forward error response to client
                client_socket.send(server_response_header.encode())
                while data := server_socket.recv(1024):
                    client_socket.send(data)
            # TESTED

        # Shutdown TCP connection with server
        server_socket.close()
        # Shutdown TCP connection with client
        client_socket.shutdown(socket.SHUT_WR)


if __name__ == '__main__':
    main()
