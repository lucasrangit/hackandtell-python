#!/usr/bin/env python3
from datetime import datetime
import fcntl
import time
import math
import os
import pygame
from pygame.locals import *
import requests
import socket
from stopwatch import Stopwatch
import struct
import threading

# handle systemd SIGHUP
import signal
def handler(signum, frame):
    pass
signal.signal(signal.SIGHUP, handler)

# from https://stackoverflow.com/a/24196955/388127
def get_ip_address(ifname):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ret = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])
    s.close()
    return ret

TIMER_S = 5*60.0

UDP_IPS = list()

if os.environ.get('MATELIGHT_IP') is not None:
    UDP_IPS.append(os.environ.get('MATELIGHT_IP'))
if os.environ.get('MATELIGHT_IP1') is not None:
    UDP_IPS.append(os.environ.get('MATELIGHT_IP1'))
if os.environ.get('MATELIGHT_IP2') is not None:
    UDP_IPS.append(os.environ.get('MATELIGHT_IP2'))
print("Matelight IPs:", UDP_IPS)

UDP_PORT = 1337
UDP_RATE_MS = 500

if os.environ.get('NETWORK_INTERFACE') is not None:
    NETWORK_INTERFACE = os.environ.get('NETWORK_INTERFACE')
else:
    NETWORK_INTERFACE = 'wlan0'
print("Network interface:", NETWORK_INTERFACE)

MATELIGHT_UDP_SEND_EVENT = pygame.USEREVENT + 0

votes = 0
winners = list()

def matelight_send(sock, surface):
    pixels = 0
    try:
        data = bytearray()
        for y in range(0, surface.get_height()):
            for x in range(0, surface.get_width()):
                pixel = surface.get_at((x, y))
                data.append(pixel.r)
                data.append(pixel.g)
                data.append(pixel.b)
                pixels += 1
        # TODO add optional chksum
        for _ in range(len(data), len(data)+4):
            data.append(0)
        for ip in UDP_IPS:
            sock.sendto(data, (ip, UDP_PORT))
    except Exception as e:
        print(e)
        pass

def get_winners(e):
    global winners
    while True:
        e.wait()
        r = requests.get(url='http://localhost:80/winners')
        winners = r.json()
        time.sleep(1.0)

def get_votes(e):
    global votes
    while True:
        e.wait()
        r = requests.get(url='http://localhost:80/count')
        votes = r.json()
        time.sleep(1.0)

def main():
    global votes
    global winners

    pygame.init()

    pygame.display.set_caption("Hack + Tell Timer")

    SIZE = SIZE_W, SIZE_H = (min(pygame.display.Info().current_w, 1024), min(pygame.display.Info().current_h, 600))

    screen = pygame.display.set_mode(SIZE)
    matelight_screen = pygame.Surface((40, 16))

    clock = pygame.time.Clock()

    signs_font = pygame.font.Font("OSP-DIN.ttf", 50)
    time_font = pygame.font.Font("OSP-DIN.ttf", 100)
    applause_font = pygame.font.Font("OSP-DIN.ttf", 200)
    status_font = pygame.font.Font("OSP-DIN.ttf", 20)
    matelight_font = pygame.font.Font("unscii-16-full.ttf", 15)

    time_left_header_text = signs_font.render("Time left", True, (0, 255, 0))
    time_current_header_text = signs_font.render("Current local time", True, (0, 255, 0))

    try:
        ip_address = get_ip_address(NETWORK_INTERFACE)
    except Exception as e:
        print("Could not determine {} IP address: {}".format(NETWORK_INTERFACE, e))
        ip_address = "Unknown IP"
    status_text = status_font.render(ip_address, True, (0, 255, 0))

    timer = Stopwatch()
    timer.reset()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    votes_event = threading.Event()
    votes_thread = threading.Thread(name='votes', target=get_votes, args=(votes_event,))
    votes_thread.daemon = True
    votes_thread.start()

    winners_event = threading.Event()
    winners_thread = threading.Thread(name='winners', target=get_winners, args=(winners_event,))
    winners_thread.daemon = True
    winners_thread.start()

    pygame.time.set_timer(MATELIGHT_UDP_SEND_EVENT, UDP_RATE_MS)

    show_applause = False
    show_preview = False
    show_votes = False
    show_winners = False

    run = True
    while run:
        if (TIMER_S - timer.duration) > 0:
            time_left_m, time_left_s = divmod(TIMER_S - timer.duration, 60)
            time_left_s = math.floor(time_left_s)
        else:
            time_left_m, time_left_s = 0, 0
        time_left = '{0:02.0f}:{1:02.0f}'.format(time_left_m, time_left_s)
        time_left_text = time_font.render(time_left, True, (0, 255, 0))
        time_current_text = time_font.render(datetime.now().strftime("%H:%M:%S"), True, (0, 255, 0))

        if timer.running and timer.duration >= TIMER_S:
            timer.stop()
            show_applause = True

        if show_applause:
            if (round(time.time()) % 2):
                background = (0, 255, 0)
                foreground = (0, 0, 0)
            else:
                background = (0, 0, 0)
                foreground = (0, 255, 0)
            screen.fill(background)
            applause_text = applause_font.render("APPLAUSE", True, foreground)
            screen.blit(applause_text, applause_text.get_rect(center=(SIZE_W//2, SIZE_H//2)))

        else:
            screen.fill((0, 0, 0))

            screen.blit(time_left_header_text, (SIZE_H//2, SIZE_W//10 - time_left_header_text.get_height()))
            screen_time_left_rect = screen.blit(time_left_text, (SIZE_H//2, SIZE_W//10))

            screen.blit(time_current_header_text, (SIZE_H//2, SIZE_W//3 - time_current_header_text.get_height()))
            screen.blit(time_current_text, (SIZE_H//2, SIZE_W//3))

            screen.blit(status_text, (0, SIZE_H - status_text.get_height()))

        if show_winners:
            winners_text = "&".join(winners)
            matelight_text = matelight_font.render(winners_text, True, (150, 0, 150))

        elif show_applause:
            if (round(time.time()) % 2):
                matelight_text = matelight_font.render("CLAP", False, (150, 0, 150))
            else:
                matelight_text = matelight_font.render("NOW", False, (150, 0, 150))

        elif show_votes:
            matelight_text = matelight_font.render(str(votes), True, (150, 0, 150))

        else:
            matelight_text = matelight_font.render(time_left[:5], True, (150, 0, 150))

        if show_preview:
            screen.blit(matelight_text, (SIZE_W - matelight_text.get_width(), SIZE_H - matelight_text.get_height()))

        matelight_screen.fill((0, 0, 0))
        matelight_screen.blit(matelight_text, matelight_text.get_rect(center=(matelight_screen.get_width()//2, matelight_screen.get_height()//2)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONUP:
                if show_applause:
                    show_applause = False
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    if screen_time_left_rect.collidepoint(mouse_pos):
                        if not timer.running and timer.duration < TIMER_S:
                            timer.start()
                        else:
                            timer.stop()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    show_applause = not show_applause

                elif event.key == pygame.K_p:
                    show_preview = not show_preview

                # TODO change to control-c
                elif event.key == pygame.K_q:
                    run = False

                elif event.key == pygame.K_r:
                    timer.stop()
                    timer.reset()

                elif event.key == pygame.K_v:
                    show_votes = not show_votes
                    if show_votes:
                        votes_event.set()
                    else:
                        votes_event.clear()

                elif event.key == pygame.K_w:
                    show_winners = not show_winners
                    if show_winners:
                        winners_event.set()
                    else:
                        winners_event.clear()

                elif event.key == pygame.K_SPACE:
                    if not timer.running and timer.duration < TIMER_S:
                        timer.start()
                    else:
                        timer.stop()

            if event.type == MATELIGHT_UDP_SEND_EVENT:
                matelight_send(sock, matelight_screen)

        clock.tick(15)

    sock.close()

    pygame.quit()

if __name__ == '__main__':
    main()
