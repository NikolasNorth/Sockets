import socket
import sys


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        host, _ = url.split(':')
        port, file = _.split('/', 1)
    else:
        host = input("Hostname: ")
        port = input("Port Number: ")
        file = input("File: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, int(port)))

    request = f"""GET /{file} HTTP/1.1\r
Host: {host}\r
\r"""
    client_socket.send(request.encode())
    response = client_socket.recv(1024).decode()
    status_line = response.split('\n')[0]
    status_code = int(status_line.split(' ')[1])
    if status_code == 200:
        print(response)
        filename = file.rsplit('/', 1)[-1]
        with open(filename, "wb") as new_file:
            data = client_socket.recv(1024)
            while data:
                new_file.write(data)
                data = client_socket.recv(1024)
    else:
        print(response)
        data = client_socket.recv(1024)
        while data:
            print(data.decode())
            data = client_socket.recv(1024)

    client_socket.close()


if __name__ == '__main__':
    main()
