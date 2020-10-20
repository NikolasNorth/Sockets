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


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(1024).decode()
        request_line, _, _ = request.split('\n')
        method, file, protocol = request_line.split(' ')
        filepath, filename = file.rsplit('/', 1)
        filepath = "".join(filepath) if filepath else '/'
        _, file_ext = filename.rsplit('.', 1)
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
    main()
