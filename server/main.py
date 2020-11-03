"""Web Server

This script allows the user to start a server and can be executed by the
following:
    `python3 server/main.py`

This script requires python3 to be installed.
"""

import socket
import os

HOST = "localhost"
PORT = 12000


def is_file_found(filename, filepath):
    """Searches for file relative to current directory.

    Args:
        filename: Name of file
        filepath: Path to file

    Returns:
        True, if file is found.
        False, otherwise.
    """
    PATH_TO_CWD = os.path.abspath(os.getcwd())
    try:
        for file in os.listdir(PATH_TO_CWD + filepath):
            if file == filename:
                return True
        return False  # filename does not exist
    except FileNotFoundError:  # filepath does not exist
        return False


def get_content_length(filename):
    """Returns the size (in bytes) of a file.

    Args:
        filename: Filename (including directories in path relative to Sockets/)

    Returns:
        Size (in bytes) of file.
    """
    return os.stat(filename).st_size


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


def main(host, port):
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

    Args:
        host: Host name
        port: Port number

    Returns:
        None
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(1024).decode()
        request_line = request.split('\n')[0]
        method, file, protocol = request_line.split(' ')
        filepath, filename = file.rsplit('/', 1)
        filepath = "".join(filepath) if filepath else '/'
        file_ext = filename.rsplit('.', 1)[-1]

        if protocol.strip('\r') != "HTTP/1.1":
            response_header = "HTTP/1.1 505 Version Not Supported\r\n\r"
            response_body = "server_files/errors/505.html"
        elif method != "GET":
            response_header = "HTTP/1.1 501 Method Not Implemented\r\n\r"
            response_body = "server_files/errors/501.html"
        elif is_file_found(filename, filepath):
            content_length = get_content_length(file[1:])
            content_type = get_content_type(file_ext)
            response_header = f"""HTTP/1.1 200 OK\r
Content-Length: {content_length}\r
Content-Type: {content_type}\r
\r"""
            response_body = file[1:]
        else:
            response_header = """HTTP/1.1 404 Not Found\r\n\r"""
            response_body = "server_files/errors/404.html"

        client_socket.send(response_header.encode())
        with open(response_body, "rb") as file:
            data = file.read(1024)
            while data:
                client_socket.send(data)
                data = file.read(1024)
        client_socket.shutdown(socket.SHUT_WR)


if __name__ == '__main__':
    main(HOST, PORT)
