import socket

HOST = 'localhost'
PORT = 8500
BUFFER_SIZE = 1024


def main():
    balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    balancer_socket.bind((HOST, PORT))
    balancer_socket.listen(1)
    print(f"""Load balancer listening on port {PORT}...""")

    while True:
        client_socket, client_address = balancer_socket.accept()
        request = client_socket.recv(BUFFER_SIZE).decode()
        req_info, server_info, _ = request.split('\n')
        file = req_info.split(' ')[1].lstrip('/')
        server_info = server_info.split(' ')[1]
        server_host, server_port = server_info.split(':')
        server_port = int(server_port)  # remove escape chars
        response_header = f"""HTTP/1.1 301 Moved Permanently\r
Location: {server_host}:{server_port}/{file}\r
\r"""
        client_socket.send(response_header.encode())
        with open('files/301.html', 'rb') as f:
            data = f.read(BUFFER_SIZE)
            while data:
                client_socket.send(data)
                data = f.read(BUFFER_SIZE)

        client_socket.shutdown(socket.SHUT_WR)


if __name__ == '__main__':
    main()
