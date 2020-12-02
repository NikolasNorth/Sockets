"""Web Client

This script allows the user to send a request to the 'server'.

This script allows for a url to be passed in as argument in the form of:
    `python3 client/main.py <host>:<port>/<file>`

Otherwise, you may execute this script without any url argument and be prompted
to enter the host, port and file.

For example, to send a request for `index.html` (located in `server_files/`)
using localhost on port 12000:
    `python3 client/main.py localhost:12000/server/files/index.html`

This script requires python3 to be installed.
"""

import socket
import sys

BUFFER_SIZE = 1024


def main(server_host, server_port, file, proxy_host=None, proxy_port=None):
    """Main function of the script.

    Creates TCP socket for server and connects to specified port on host. Sends
    request for a specified file. If a 200 response was received, then the
    client downloads the file to its current working directory. Otherwise,
    the client prints out the contents of the error response. Regardless of the
    response status code, the client will quit the connection thereafter.

    Args:
        server_host: Hostname of server
        server_port: Port number for server
        file: Filename
        proxy_host: Hostname of proxy
        proxy_port: Port number for proxy

    Returns:
        None
    """
    try:
        # Make TCP connection with server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if proxy_host and proxy_port:
            server_socket.connect((proxy_host, int(proxy_port)))
        else:
            server_socket.connect((server_host, int(server_port)))
    except ConnectionRefusedError:
        print("Error: Could not connect to server")
        sys.exit(1)

    # Send request
    request = f"""GET /{file} HTTP/1.1\r
Host: {server_host}:{server_port}\r
\r"""
    server_socket.send(request.encode())

    # Receive response
    response = server_socket.recv(BUFFER_SIZE).decode()
    status_line = response.split('\n')[0]
    status_code = int(status_line.split(' ')[1])
    if status_code == 200:
        print(response)
        filename = file.rsplit('/', 1)[-1]
        with open("./files/" + filename, "wb") as new_file:
            data = server_socket.recv(BUFFER_SIZE)
            while data:
                new_file.write(data)
                data = server_socket.recv(BUFFER_SIZE)
    elif status_code == 301:
        print(response)
        data = server_socket.recv(BUFFER_SIZE)
        while data:
            print(data.decode())
            data = server_socket.recv(BUFFER_SIZE)
    else:
        print(response)
        data = server_socket.recv(BUFFER_SIZE)
        while data:
            print(data.decode())
            data = server_socket.recv(BUFFER_SIZE)

    # Close TCP connection with server
    server_socket.close()


if __name__ == '__main__':
    try:
        proxy_host, proxy_port = None, None
        # Extract request info from command
        if "-proxy" in sys.argv:
            url = sys.argv[3]
            server_host, _ = url.split(':')
            server_port, file = _.split('/', 1)
            proxy_url = sys.argv[2]
            proxy_host, proxy_port = proxy_url.split(':')
            main(server_host, server_port, file, proxy_host, proxy_port)
        elif "-balancer" in sys.argv:
            url = sys.argv[2]
            server_host, _ = url.split(':')
            server_port, file = _.split('/', 1)
            main(server_host, server_port, file)
        else:
            url = sys.argv[1]
            server_host, _ = url.split(':')
            server_port, file = _.split('/', 1)
            main(server_host, server_port, file)
    except IndexError:
        print("Error: Please provide server name, port number and file.")
