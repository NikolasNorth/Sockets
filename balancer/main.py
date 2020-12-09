import socket
import json
import random
import time

HOST = 'localhost'
PORT = 8500
BUFFER_SIZE = 1024
TIMEOUT_LEN = 10.0  # seconds


def performance_test(server_list):
    """Runs performance test on all provided servers.

    Args:
        server_list: List of servers

    Returns:
        List of available servers, sorted by speed of processing requests in
        descending order (where is the first element takes the most amount of
        time)
    """
    for server in server_list:
        try:
            t_start = time.time_ns()
            # Connect to server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server['host'], server['port']))
        except ConnectionRefusedError:
            server['isAvailable'] = False
        else:
            server['isAvailable'] = True
            print(f"Running performance test on Server {server['id']}...")

            req = f"""GET /test.jpg HTTP/1.1\r
Host: {server['host']}:{server['port']}\r
\r"""
            server_socket.send(req.encode())

            while True:
                res = server_socket.recv(BUFFER_SIZE).decode()
                print(res)
                data = server_socket.recv(BUFFER_SIZE)
                while data:
                    data = server_socket.recv(BUFFER_SIZE)
                if res:
                    break
            server['time'] = time.time_ns() - t_start
            print(f"Complete. ({server['time']} ns)\n")
            server_socket.close()
    # Remove unavailable servers
    server_list = [server for server in servers if server['isAvailable']]
    # Sort by time descending
    return sorted(server_list, key=lambda k: k['time'], reverse=True)


def select_server(server_list):
    """Chooses a server based off performance test.

    The server_list array is sorted from slowest to fastest, where the slowest
    server is at index 0. Servers with greater indices will receive an
    increasingly greater chance of being selected. The number of 'tickets' the
    server will have in the lottery system will be equal to its index position
    in server_list + 1. For example, server at position 0 will receive (0 + 1)
    tickets, server at position 5 will receive (5 + 1) tickets. A random number
    will be chosen between (0, len(lottery)).

    Args:
        server_list: List of servers (sorted by performance)

    Returns:
        Server
    """
    lottery = []
    n = 1
    for server in server_list:
        lottery += [server] * n
        n += 1
    i = random.randint(0, len(lottery) - 1)
    return lottery[i]


def main(server_list):
    balancer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    balancer_socket.bind((HOST, PORT))
    balancer_socket.listen(1)
    print(f"""Load balancer listening on port {PORT}...\n""")
    server_list = performance_test(server_list)
    balancer_socket.settimeout(TIMEOUT_LEN)

    while True:
        try:
            # Connect to client
            client_socket, client_address = balancer_socket.accept()
            request = client_socket.recv(BUFFER_SIZE).decode()
            if request:
                # Cancel timeout
                balancer_socket.settimeout(None)
                # Choose a server based on performance test
                server = select_server(server_list)
                req_info, server_info, _ = request.split('\n')
                file = req_info.split(' ')[1].lstrip('/')
                server_host = server['host']
                server_port = server['port']
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
                # Restart timeout
                balancer_socket.settimeout(TIMEOUT_LEN)
        except socket.timeout:
            # Run performance test
            server_list = performance_test(server_list)


if __name__ == '__main__':
    with open('./config.json') as f:
        data = json.load(f)
        servers = data['servers']
    main(servers)
