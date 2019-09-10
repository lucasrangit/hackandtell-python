#!/usr/bin/env python3
from datetime import datetime
import time
import pygame
from pygame.locals import *
from stopwatch import Stopwatch

TIMER_DURATION_S = 5*60

def main():
    pygame.init()

    SIZE = SIZE_W, SIZE_H = (min(pygame.display.Info().current_w, 1024), min(pygame.display.Info().current_h, 600))
    print("Display size: %dx%d" % (SIZE_W, SIZE_H))

    screen = pygame.display.set_mode(SIZE)

    clock = pygame.time.Clock()

    signs_font = pygame.font.Font("OSP-DIN.ttf", 50)
    time_font = pygame.font.Font("OSP-DIN.ttf", 100)
    applause_font = pygame.font.Font("OSP-DIN.ttf", 200)

    time_left_header_text = signs_font.render("Time left", True, (0, 255, 0))
    time_current_header_text = signs_font.render("Current local time", True, (0, 255, 0))
    applause_text = applause_font.render("APPLAUSE", True, (0, 255, 0))

    pygame.display.set_caption("Hack + Tell Timer")

    timer = Stopwatch()
    timer.reset()

    show_applause = False

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONUP:
                print(pygame.mouse.get_pos())

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False

                elif event.key == pygame.K_r:
                    timer.stop()
                    timer.reset()

                elif event.key == pygame.K_SPACE:
                    if not timer.running and timer.duration < TIMER_DURATION_S:
                        timer.start()
                    else:
                        timer.stop()

                elif event.key == pygame.K_a:
                    show_applause = not show_applause

        if timer.running and timer.duration >= TIMER_DURATION_S:
            timer.stop()
            show_applause = True

        screen.fill((0, 0, 0))

        if show_applause:
            if (round(time.time()) % 2):
                screen.blit(applause_text, applause_text.get_rect(center=(SIZE_W//2, SIZE_H//2)))
            else:
                screen.fill((0, 0, 0))
        else:
            time_left = '{0:02.0f}:{1:06.3f}'.format(*divmod(timer.duration * 60, 60))
            time_left_text = time_font.render(time_left, True, (0, 255, 0))
            time_current_text = time_font.render(datetime.now().strftime("%H:%M:%S.%f")[:-3], True, (0, 255, 0))

            screen.blit(time_left_header_text, (SIZE_H//2, SIZE_W//10 - time_left_header_text.get_height()))
            screen.blit(time_left_text, (SIZE_H//2, SIZE_W//10))

            screen.blit(time_current_header_text, (SIZE_H//2, SIZE_W//3 - time_current_header_text.get_height()))
            screen.blit(time_current_text, (SIZE_H//2, SIZE_W//3))

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
