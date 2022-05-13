import socket

def Main():
    """
    Function: Send letter to other computer and receive capital letter back from server
    Args: -
    Returns: -

    Created by: Mitchell de Keijzer
    Date: 28-3-2022
    """
    host = '192.168.0.3'
    port = 4003

    server = ('192.168.0.5', 4000)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    message = input('-> ')
    while message != 'q':
        s.sendto(message.encode('utf-8'), server)
        print('Message sent')
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print('Received from server: ' + data)
        message = input('-> ')
    s.close()

Main()