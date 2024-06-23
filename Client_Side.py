import socket
import threading
import struct


def client_setup():
    server_ip = input("Server ip: ")
    server_port = input("Server Port: ")
    server_address = (server_ip, server_port)
    print(server_ip, server_port)
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.connect(server_address)
        client_socket, client_address = server_socket.accept()
        return server_socket, client_socket

    except ConnectionRefusedError:
        print('Connection refused on address')

def client_loop():
    server_socket, client_socket = client_setup()


def protocol_handler(client_socket, header):
    print(header)
