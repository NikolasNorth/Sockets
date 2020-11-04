import socket
import os
import time
from pathlib import Path

HOST = "localhost"
PORT = 9000
FILE_EXPIRE_TIME = 120  # seconds
PATH_TO_CWD = os.path.abspath(os.getcwd())


def main(host, port):
    # Bind proxy to socket and listen for requests
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((host, port))
    proxy_socket.listen(1)
    print(f"""Proxy listening on port {PORT}...""")

    while True:
        # Make TCP connection with client
        client_socket, client_address = proxy_socket.accept()

        # Receive request
        request = client_socket.recv(1024).decode()
        request_line = request.split('\n')[0]
        file = request_line.split(' ')[1]

        # Check if file is stored in cache
        if os.path.isfile("./files" + file):
            # File is stored in cache
            # Check if file is expired
            current_time = time.time()
            file_mtime = os.path.getmtime("./files" + file)
            if (current_time - file_mtime) < FILE_EXPIRE_TIME:
                # File is not expired
                pass
            else:
                # File is expired
                pass
        else:
            # File is not stored in cache
            # Make TCP connection with server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((host, 8000))

            # Send request to server
            server_socket.send(request.encode())

            # Receive response from server
            server_response_header = server_socket.recv(1024).decode()
            status_line = server_response_header.split('\n')[0]
            status_code = int(status_line.split(' ')[1])
            if status_code == 200:
                # Store file in cache
                filepath, filename = file.rsplit('/', 1)
                print(file)
                print(filepath, filename)
                if filepath:
                    os.makedirs("./files" + filepath, exist_ok=True)
                file_location = "./files" + filepath + '/' + filename
                with open(file_location, "wb") as new_file:
                    data = server_socket.recv(1024)
                    while data:
                        new_file.write(data)
                        data = server_socket.recv(1024)

            # Forward response to client
            client_socket.send(server_response_header.encode())
            with open(file_location, "rb") as file:
                data = file.read(1024)
                while data:
                    client_socket.send(data)
                    data = file.read(1024)

            # Close TCP connection with server and client
            server_socket.close()
            client_socket.shutdown(socket.SHUT_WR)


if __name__ == '__main__':
    main(HOST, PORT)
