import socket

def Main():
    """
    Function: Set up server for client to connect, receive letter and send back capital letter to client
    Args: -
    Returns: -

    Created by: Mitchell de Keijzer
    Date: 28-3-2022
    """
    host = '192.168.0.3'
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print('Server Started')
    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print('Message from: ' + str(addr))
        print('From connected user: ' + data)
        data = data.upper()
        print('Sending: ' + data)
        s.sendto(data.encode('utf-8'), addr)
    s.close()

Main()