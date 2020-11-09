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


def main(server_host, server_port, file, proxy_host=None, proxy_port=None):
    """Main function of the script.

    Creates TCP socket for server and connects to specified port on host. Sends
    request for a specified file. If a 200 response was received, then the
    client downloads the file to its current working directory. Otherwise,
    the client prints out the contents of the error response. Regardless of the
    response status code, the client will quit the connection thereafter.

    Args:
        host: Hostname
        port: Port number
        file: Filename
        proxy_host: Hostname of proxy
        proxy_port: Port number of proxy

    Returns:
        None
    """
    # Make TCP connection with server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if proxy_host and proxy_port:
        server_socket.connect((proxy_host, int(proxy_port)))
    else:
        server_socket.connect((server_host, int(server_port)))

    # Send request
    request = f"""GET /{file} HTTP/1.1\r
Host: {server_host}:{server_port}\r
\r"""
    server_socket.send(request.encode())

    # Receive response
    response = server_socket.recv(1024).decode()
    status_line = response.split('\n')[0]
    status_code = int(status_line.split(' ')[1])
    if status_code == 200:
        print(response)
        filename = file.rsplit('/', 1)[-1]
        with open("./files/" + filename, "wb") as new_file:
            data = server_socket.recv(1024)
            while data:
                new_file.write(data)
                data = server_socket.recv(1024)
    else:
        print(response)
        data = server_socket.recv(1024)
        while data:
            print(data.decode())
            data = server_socket.recv(1024)

    # Close TCP connection with server
    server_socket.close()


if __name__ == '__main__':
    proxy_host = None
    proxy_port = None
    if len(sys.argv) > 1:
        # Extract request info from command
        if "-proxy" in sys.argv:
            # With caching
            url = sys.argv[3]
            server_host, _ = url.split(':')
            server_port, file = _.split('/', 1)
            proxy_url = sys.argv[2]
            proxy_host, proxy_port = proxy_url.split(':')
        else:
            # Without caching
            url = sys.argv[1]
            server_host, _ = url.split(':')
            server_port, file = _.split('/', 1)
    else:
        # Prompt user for request info
        server_host = input("Hostname: ")
        server_port = input("Port Number: ")
        file = input("File: ")
        proxy_host = input("Proxy Hostname: ")
        proxy_port = input("Proxy Port Number: ")

    if proxy_host and proxy_port:
        main(server_host, server_port, file, proxy_host, proxy_port)
    else:
        main(server_host, server_port, file)
