from socket import *
import struct
import time
import math

src = '127.0.0.1'
port = 9500
dir = '/home/highside/com1_screen'

def screen_listener(module, properties):
    src = properties['src']
    port = properties['port']
    dir = properties['in']
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((src, port))

    try:
        while True:
            filename = f'{dir}/{math.floor(time.time())}.jpeg'
            with open(filename, 'wb') as fw:
                full_data = b''
                while True:
                    data, adr = s.recvfrom(2048)
                    if not data:
                        break
                    msg_length = struct.unpack('>I', data[:4])[0]
                    full_data += data[4:(msg_length + 4)]
                    fw.write(data)
                fw.close()
    except KeyboardInterrupt:
        s.close()
