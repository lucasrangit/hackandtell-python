#!/usr/bin/env python3
import random
import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 1337

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    try:
        data = bytearray()
        for y in range(0, 16):
            for x in range(0, 40):
                r = int(random.random() * 256)
                g = int(random.random() * 256)
                b = int(random.random() * 256)
                data.append(r)
                data.append(g)
                data.append(b)
        sock.sendto(data, (UDP_IP, UDP_PORT))
    except KeyboardInterrupt:
        break
    time.sleep(0.01)

sock.close()
