import socket
import threading
import struct

servers_list = [("127.0.0.1", 9999), ("127.0.0.1", 9998), ("127.0.0.1", 9997), ("127.0.0.1", 9996), ("127.0.0.1", 9995)]
header_format = '>bbhh'


# 0 type 1byte , 1 subtype 1byte, 2 length 2bytes, 3 sublen 2bytes


def client_setup():
    server = int(input("Choose a server to connect to (0-4): "))
    server_address = (servers_list[server])

    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.connect(server_address)
        address = server_address[0] + ':' + str(server_address[1])
        server_sock.send(address.encode())
        return server_sock

    except ConnectionRefusedError:
        print('Connection refused on address')


def create_user():
    user_name = input("Enter your username: ")
    user_name = user_name.encode()
    server_socket.send(struct.pack(header_format, 2, 1, len(user_name), 0) + user_name)
    threading.Thread(target=handle_massage).start()
    send_massage()


def handle_massage():
    while True:
        try:
            data = server_socket.recv(1024)
            print("\nreceived massage: ")
            sender, massage, receiver = data.decode().split('\0')
            print(f'from: {sender}\n{massage} \nto: {receiver}')
            if not data:
                break
        except Exception as e:
            print(e)


def send_massage():
    while True:
        receiver, massage = input().split(" ", 1)
        massage += '\0'
        massage += receiver
        massage = massage.encode()
        if massage:
            server_socket.send(struct.pack(header_format, 3, 0, len(massage), len(receiver)) + massage)


server_socket = client_setup()
if server_socket:
    create_user()

