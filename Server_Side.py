import socket
import struct
from icecream import ic
import threading

header_format = '>bbhh'
# 0 type 1byte , 1 subtype 1byte, 2 length 2bytes, 3 sublen 2bytes


def server_setup():
    # set up the listen socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(server_address)
    server_sock.listen(5)
    print(f'Server Socket Listening on {listen_address}')
    # add the server to the server_dict
    server_dict[listen_address] = server_sock
    ic(server_dict)


def server_accept_loop(server_sock):
    while True:
        peer_socket, add = server_sock.accept()
        print(f'Accepted connection from {add}')
        listen_add = peer_socket.recv(14)
        listen_add = listen_add.decode()
        if listen_add != listen_address:
            server_dict[listen_add] = peer_socket
        ic(server_dict)
        client_handler = threading.Thread(target=handle_connection, args=(peer_socket,))
        client_handler.start()


def connect_to_peer(ip, port):
    try:
        other_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        other_server.connect((ip, port))
        print(f'Connected to {ip}:{port}')
        other_server.send(listen_address.encode())
        other_server.send(struct.pack(header_format, 2, 0, 0, 0))
        server_dict[ip + ":" + str(port)] = other_server
        ic(server_dict)
        return other_server
    except ConnectionRefusedError:
        print(f'Failed to connect to {server_ip}:{port}')
    except Exception as e:
        print(f'Failed {e}')


def test_servers_connection():
    for port in ports:
        sock = connect_to_peer(server_ip, port)
        if sock:
            threading.Thread(target=handle_connection, args=(sock,)).start()
            sock.send(struct.pack(header_format, 0, 0, 0, 0))
            break


def connect_from_list(servers_list):
    print(servers_list)
    for address in servers_list:
        if address not in server_dict.keys():
            ip, port = address.split(":")
            sock = connect_to_peer(ip, int(port))
            threading.Thread(target=handle_connection, args=(sock,)).start()


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


def protocol_handler(client_socket, header):
    def check_client():
        pass

    match header[0]:
        case 0:
            # info request
            if header[1] == 0:
                # info on server request
                massage = ''
                addresses = server_dict.keys()
                ic(addresses)
                for address in addresses:
                    massage += address + '\0'
                package = massage.encode()
                ic(package)
                client_socket.send(struct.pack(header_format, 1, 0, len(package), 0) + package)
                # client_socket.send(package)

            elif header[1] == 1:
                # info on clients request
                massage = ''
                names = clients_dict.keys()
                for name in names:
                    massage += name + '\0'
                package = massage.encode()
                client_socket.send(struct.pack(header_format, 1, 1, len(package), 0) + package)
            else:
                print("unexpected protocol header")

        case 1:
            # info receive
            if header[1] == 0:
                # receive server info
                length = header[2]
                data = client_socket.recv(length)
                # server connect
                massage = data.decode()
                massage = massage.split('\0')
                massage.remove("")
                ic(massage)
                connect_from_list(massage)
                print(header)
            elif header[1] == 1:
                # receive client info
                length = header[2]
                data = client_socket.recv(length)
                print(data)
            else:
                print("unexpected protocol header")

        case 2:
            if header[1] == 0:
                # become a server
                ic(client_socket)
                print(header, "server")
            elif header[1] == 1:
                # become a client
                client_name = client_socket.recv(header[2]).decode()
                clients_dict[client_name] = client_socket
                ic(clients_dict)
            else:
                print("unexpected protocol header")

        case 3:
            # send the message
            if client_socket in clients_dict.values():
                for name, sock in clients_dict.items():
                    if sock == client_socket:
                        sender = name
                        ic(sender)
                        data = client_socket.recv(header[2]).decode()
                        massage, receiver = data.split('\0')
                        ic(massage, receiver)
                        massage = sender + "\0" + massage + '\0' + receiver
                        if receiver in clients_dict.keys():
                            receiver_socket = clients_dict[receiver]
                            ic(receiver_socket)
                            receiver_socket.send(massage.encode())
                            break
                        else:
                            for server in server_dict.values():

                                if server != server_socket:
                                    server.send(struct.pack(header_format, 3, 0, len(massage), len(receiver)) + massage.encode())
            if client_socket in server_dict.values():
                data = client_socket.recv(header[2] + header[3]).decode()
                sender, massage, receiver = data.split('\0')
                if receiver in clients_dict.keys():
                    clients_dict[receiver].send(data.encode())

        case _:
            print("unknown header")


server_ip = "127.0.0.1"
ports = [9999, 9998, 9997, 9996, 9995]
clients_dict = {}
server_dict = {}
print("ports: \n", ports)
server_port = ports[int(input("Server port (0 - 4): "))]
ports.remove(server_port)
server_address = (server_ip, server_port)
listen_address = server_address[0] + ":" + str(server_port)
server_setup()
server_socket = server_dict[listen_address]
threading.Thread(target=server_accept_loop, args=(server_socket,)).start()
test_servers_connection()


