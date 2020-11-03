"""Web Client

This script allows the user to send a request to the 'server'.

This script allows for a url to be passed in as argument in the form of:
    `python3 client/main.py <host>:<port>/<file>`

Otherwise, you may execute this script without any url argument and be prompted
to enter the host, port and file.

For example, to send a request for `index.html` (located in `server_files/`)
using localhost on port 12000:
    `python3 client/main.py localhost:12000/server_files/index.html`

This script requires python3 to be installed.
"""

import socket
import sys


def main(host, port, file):
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

    Returns:
        None
    """
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
    try:
        if len(sys.argv) > 1:
            # Extract request info from command
            if "-proxy" in sys.argv:
                # With caching
                proxy = True
                url = sys.argv[3]
                hostname, _ = url.split(':')
                port_number, filename = _.split('/', 1)
                proxy_url = sys.argv[2]
                proxy_hostname, proxy_port_number = proxy_url.split(':')
            else:
                # Without caching
                proxy = False
                url = sys.argv[1]
                hostname, _ = url.split(':')
                port_number, filename = _.split('/', 1)
        else:
            # Prompt user for request info
            hostname = input("Hostname: ")
            port_number = input("Port Number: ")
            filename = input("File: ")
            proxy_hostname = input("Proxy Hostname: ")
            proxy_port = input("Proxy Port Number: ")
            proxy = True if (proxy_hostname and proxy_port) else False

        if proxy:
            print("Request w/ proxy")
        else:
            print("Request w/o proxy")
        # main(hostname, port_number, filename)
    except:
        print("Invalid command.")
