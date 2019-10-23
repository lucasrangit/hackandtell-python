#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import board
from rpi_ws281x import PixelStrip, Color
import select
import socket

SIZE_W = 40
SIZE_H = 16

# LED strip configuration:
LED_COUNT = SIZE_W * SIZE_H
LED_BRIGHTNESS = 32   # 0 for darkest and 255 for brightest
# GPIO pin connected to the pixels (18 uses PWM!).
# GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_PIN = 18          # board.D18
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_FREQ_HZ = 800000  # LED signal frequency in hertz
LED_DMA = 10          # DMA channel to use for generating signal
LED_INVERT = False    # True to invert the signal (e.g. when using NPN transistor level shift)

PACKET_SIZE = SIZE_W * SIZE_H * 3 # + 4

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 1337


def wait_for_data(sock, matrix):
    """
    Grab the next frame and put it on the matrix.
    """
    select.select([], [sock], [])
    try:
        data, addr = sock.recvfrom(PACKET_SIZE)
    except socket.error:
        pass
    else:
        if len(data) == PACKET_SIZE:
            for i in range(LED_COUNT):
                matrix[i] = Color(data[i * 3], data[i * 3 + 1], data[i * 3 + 2])

def display_data(matrix, pixels):
    """
    Generate the output from the matrix.
    """
    for i in range(LED_COUNT):
        pixels.setPixelColor(i, matrix[i])
    pixels.show()

def display_clear(pixels):
    for i in range(LED_COUNT):
        pixels.setPixelColor(i, Color(0, 0, 0))
    pixels.show()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))

    matrix = list()
    for i in range(SIZE_W * SIZE_H * 3):
        matrix.append(0)

    pixels = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    pixels.begin()
    display_clear(pixels)

    try:
        while True:
            wait_for_data(sock, matrix)
            display_data(matrix, pixels)
    except KeyboardInterrupt:
        display_clear(pixels)
        sock.close()

if __name__ == '__main__':
    main()
