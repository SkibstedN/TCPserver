#! /usr/bin/python
from socket import *
import datetime

# Funktion til at få nuværende tid i Apache-logformat
def get_time_in_apache_format():
    return datetime.datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')

# Funktion til at logge en forespørgsel
def log_request(client_ip, request_line, response_code, content_length):
    with open("server.log", "a") as log_file:  # Åbner logfilen i append-tilstand
        try:
            method, path, version = request_line.split(' ')
        except ValueError:  # Håndterer tilfælde, hvor parsing fejler
            method, path, version = "-", "-", "-"
        # Opbygger loglinjen i Apache-format
        log_line = f"{client_ip} - - [{get_time_in_apache_format()}] \"{method} {path} {version}\" {response_code} {content_length}\n"
        # Skriver loglinjen til filen
        log_file.write(log_line)

server_port = 15000
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(("", server_port))
server_socket.listen(1)
print("The server is ready to receive.")

while True:
    connection_socket, addr = server_socket.accept()
    client_ip = addr[0]  # Gem klientens IP-adresse
    request_data = connection_socket.recv(2048)
    request = request_data.decode()
    
    if not request:
        print("Received an empty request")
        connection_socket.close()
        continue

    request_lines = request.split('\r\n')
    request_line = request_lines[0]  # Antager første linje er request-linjen
    try:
        method, requested_file_path, version = request_line.split(' ')
    except ValueError:
        method, requested_file_path, version = "-", "-", "-"

    if requested_file_path == "/":
        requested_file_path = "/index.html"

    try:
        file_path = requested_file_path[1:]
        with open(file_path, 'rb') as file:
            response_content = file.read()
            header = 'HTTP/1.1 200 OK\r\n'
            header += 'Content-Type: text/html; charset=UTF-8\r\n'
            content_length = len(response_content)
            header += f'Content-Length: {content_length}\r\n'
            header += '\r\n'  # Empty line to separate headers from the body
            response_code = 200
    except FileNotFoundError:
        response_content = b"<html><body><h1>404 Not Found</h1></body></html>"
        header = 'HTTP/1.1 404 Not Found\r\n'
        header += 'Content-Type: text/html; charset=UTF-8\r\n'
        content_length = len(response_content)
        header += f'Content-Length: {content_length}\r\n'
        header += '\r\n'
        response_code = 404

    final_response = header.encode() + response_content
    connection_socket.send(final_response)
    connection_socket.close()
    
    # Logger hver forespørgsel
    log_request(client_ip, request_line, response_code, content_length)
