import socket
import struct
from icecream import ic
import threading


header_format = '>bbhh'
server_dict = {}


def server_setup(address):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(address)
    server_sock.listen(5)
    for port in ports:
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((address, port))
            peer_socket.send(struct.pack(header_format, 0, 0, 0, 0))
            handle_connection(server_sock)
        except ConnectionRefusedError as e:
            print(f"Connection refused on port: {port}")
    return server_sock


def connect_to_others(server_info):
    print(server_info)
    for address, sock in server_info.items():
        sock.connect(address)


def handle_connection(listen_socket):
    while True:
        try:
            header = listen_socket.recv(6)
            if not header:
                break
            # 0 type 1byte , 1 subtype 1byte, 2 length 2bytes, 3 sublen 2bytes
            header = struct.unpack(header_format, header)
            protocol_handler(listen_socket, header)
        except struct.error as e:
            print(f"Error: {e}")


def dict_manager(case_id, dic=None, msg=None, server_info=None):
    match case_id:
        case 0:
            # server info to send
            address = dic.items()
            massage = b''
            for ip, port in server_address:
                massage += ip + ":" + port + '\0'
            print(massage)
            return massage
        case 1:
            # clients info to send
            names = dic.keys()
            massage = b''
            for name in names:
                massage += name + '\0'
            return massage
        case 2:
            # server info receive and connect
            massage = msg.split('\0').decode()
            connect_to_others(massage)
        case 3:
            # client info receive and update
            massage = msg.split('\0').decode()
            for name in massage:
                clients_dict[name] = server_info
        case _:
            print("unknown type")


def protocol_handler(client_socket, header):
    match header[0]:
        case 0:
            if header[1] == 0:
                # info on server request
                client_socket.send(struct.pack(header_format, 1, 0, len(server_dict), 0))
                package = dict_manager(header[1], server_dict)
                client_socket.send(package)
            elif header[1] == 1:
                # info on clients request
                package = dict_manager(header[1], clients_dict)
                client_socket.send(package)
            else:
                print("unexpected protocol header")

        case 1:
            if header[1] == 0:
                # receive server info
                length = header[2]
                client_socket.recv(length)
                dict_manager(2, msg=client_socket.recv(length))
                print(header)
            elif header[1] == 1:
                # receive client info
                length = header[2]
                dict_manager(3, msg=client_socket.recv(length), server_info=server_dict[client_socket])
                print(clients_dict)

        case 2:
            if header[1] == 0:
                # become a server
                server_dict[server_socket] = server_address
                print(header, "server")
            elif header[1] == 1:
                # become a client
                length = header[2]
                client_name = client_socket.recv(length)
                clients_dict[client_name] = server_dict[server_socket]

        case 3:
            # send the message
            if client_socket == server_socket:
                data = client_socket.recv(1024)
                for sock in server_dict:
                    sock.send(struct.pack(header_format, 1, 0, len(server_dict), 0))
                    sock.send(data)
            else:
                data = client_socket.recv(1024)
                print(data.decode())
            print(header, "massage")

        case _:
            print("unknown header")


server_ip = "127.0.0.1"
ports = [9999, 9998, 9997, 9996, 9995, 9994, 9993, 9992, 9991, 9990]
print("ports: \n", ports)
server_port = int(input("Server port: "))
server_address = (server_ip, server_port)
server_socket = server_setup(server_address)
clients_dict = {}
