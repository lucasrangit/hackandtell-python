#!/usr/bin/env python3
from datetime import datetime
import time
import pygame
from pygame.locals import *
import socket
from stopwatch import Stopwatch

TIMER_S = 5*60.0

UDP_IP = "0.0.0.0"
UDP_PORT = 1337

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
        sock.sendto(data, (UDP_IP, UDP_PORT))
    except Exception as e:
        print(e)
        pass


def main():
    pygame.init()

    pygame.display.set_caption("Hack + Tell Timer")

    SIZE = SIZE_W, SIZE_H = (min(pygame.display.Info().current_w, 1024), min(pygame.display.Info().current_h, 600))

    screen = pygame.display.set_mode(SIZE)
    matelight_screen = pygame.Surface((40, 16))

    clock = pygame.time.Clock()

    signs_font = pygame.font.Font("OSP-DIN.ttf", 50)
    time_font = pygame.font.Font("OSP-DIN.ttf", 100)
    applause_font = pygame.font.Font("OSP-DIN.ttf", 200)
    matelight_font = pygame.font.Font("unscii-16-full.ttf", 15)

    time_left_header_text = signs_font.render("Time left", True, (0, 255, 0))
    time_current_header_text = signs_font.render("Current local time", True, (0, 255, 0))

    timer = Stopwatch()
    timer.reset()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    show_applause = False
    show_preview = False

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONUP:
                # print(pygame.mouse.get_pos())
                pass

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    show_applause = not show_applause

                elif event.key == pygame.K_p:
                    show_preview = not show_preview

                elif event.key == pygame.K_q:
                    run = False

                elif event.key == pygame.K_r:
                    timer.stop()
                    timer.reset()

                elif event.key == pygame.K_SPACE:
                    if not timer.running and timer.duration < TIMER_S:
                        timer.start()
                    else:
                        timer.stop()

        if (TIMER_S - timer.duration) > 0:
            time_left_m, time_left_s = divmod(TIMER_S - timer.duration, 60)
        else:
            time_left_m, time_left_s = 0, 0
        time_left = '{0:02.0f}:{1:06.3f}'.format(time_left_m, time_left_s)
        time_left_text = time_font.render(time_left, True, (0, 255, 0))
        time_current_text = time_font.render(datetime.now().strftime("%H:%M:%S.%f")[:-3], True, (0, 255, 0))

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
            screen.blit(time_left_text, (SIZE_H//2, SIZE_W//10))

            screen.blit(time_current_header_text, (SIZE_H//2, SIZE_W//3 - time_current_header_text.get_height()))
            screen.blit(time_current_text, (SIZE_H//2, SIZE_W//3))

        matelight_text = matelight_font.render(time_left[:5], True, (150, 0, 150))

        if show_preview:
            screen.blit(matelight_text, (SIZE_W - matelight_text.get_width(), SIZE_H - matelight_text.get_height()))

        matelight_screen.fill((0, 0, 0))
        matelight_screen.blit(matelight_text, matelight_text.get_rect(center=(matelight_screen.get_width()//2, matelight_screen.get_height()//2)))

        pygame.display.flip()

        matelight_send(sock, matelight_screen)

        clock.tick(60)

    sock.close()

    pygame.quit()

if __name__ == '__main__':
    main()
