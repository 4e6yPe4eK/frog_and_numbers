import pygame
import os
from random import choice, shuffle, randint
from math import acos, pi, sqrt
from time import sleep
pygame.init()
pygame.mixer.init()
size_x, size_y = 1155, 650
pygame.display.set_caption('Frog and numbers')
screen = pygame.display.set_mode((size_x, size_y))
font = pygame.font.Font(None, 48)


def load_image(name, color=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if color is not None:
        image = image.convert()
        if color == -1:
            color = image.get_at((0, 0))
        image.set_colorkey(color)
    else:
        image = image.convert_alpha()
    return image


class Lily(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('lily.png'), (int(size_x * 0.14), int(size_y * 0.21)))
    image_drown = pygame.transform.scale(load_image('boom.png'), (int(size_x * 0.14), int(size_y * 0.21)))

    def __init__(self, x, y, text):
        super().__init__()
        self.image = Lily.image.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.num = int(text)
        string_rendered = font.render(text, True, pygame.Color('black'))
        self.image.blit(string_rendered, (self.image.get_width() // 3, self.image.get_height() // 2))

    def collide(self, pos):
        mask = pygame.mask.from_surface(pygame.surface.Surface((1, 1)))
        offset = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        if self.mask.overlap_area(mask, offset):
            return True
        return False

    def update(self, *args):
        if args and type(args[0]) is tuple:
            self.rect = self.rect.move(*args[0])
        elif args and args[0] is None:
            if self != drowned:
                self.image = Lily.image_drown.copy()
        elif args and args[0].type == pygame.MOUSEBUTTONDOWN and self.collide(args[0].pos):
            jump.play(0)
            global ending, waiting, n, x, y, xe, ye, speed_x, speed_y, angle
            x, y = frog_coords
            xe = self.rect.x + (self.image.get_width() - frog.get_width()) // 2
            ye = self.rect.y + (self.image.get_height() - frog.get_height()) // 2
            speed_x, speed_y = abs(xe - x - frog.get_width()), ye - y
            ac = sqrt((xe - x) ** 2 + ye ** 2)
            ab = y
            bc = sqrt((xe - x) ** 2 + (ye - y) ** 2)
            angle = int(acos((ac ** 2 - ab ** 2 - bc ** 2) / (-2 * ab * bc)) / pi * -180)
            n = 0
            ending = True
            waiting = False
            clock.tick()
            global wrong
            if solution_type and args[1][0] + args[1][1] == self.num or\
                    not solution_type and args[1][0] - args[1][1] == self.num:
                wrong = 0
            else:
                wrong = 1


if __name__ == "__main__":
    win = pygame.mixer.Sound(os.path.join('data', 'win.wav'))
    lose = pygame.mixer.Sound(os.path.join('data', 'lose.wav'))
    bul = pygame.mixer.Sound(os.path.join('data', 'bul.wav'))
    jump = pygame.mixer.Sound(os.path.join('data', 'jump.wav'))
    background = pygame.transform.scale(load_image('water.jpg'),
                                        (size_x, size_y))
    frog = pygame.transform.scale(pygame.transform.rotate(load_image('frog.png'), -90),
                                  (int(0.06 * size_x), int(0.13 * size_y)))
    frog_jump = pygame.transform.scale(load_image('frog_jump.png'),
                                       (int(0.1 * size_x), int(0.2 * size_y)))
    all_score = 0
    running = True
    waiting = False
    ending = False
    win_animation = False
    starting = True
    lily_group = None
    start_lily = None
    start_lily_coords = None
    frog_coords = None
    solution = None
    wrong = 1
    score_out = None
    record_out = None
    solution_type = True
    drowned = None
    record, score = 0, 0
    lily_num = 3
    pairs = []
    for i in range(1, 100):
        for j in range(1, 100):
            pairs.append([i, j])
    clock = pygame.time.Clock()
    time = 12500
    angle = 0
    n = 0
    x, y, xe, ye = 0, 0, 0, 0
    speed_x, speed_y = 0, 0
    timer_size = (int(0.28 * size_x), 20, int(0.45 * size_x), 20)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if waiting:
                    lily_group.update(event, solution)

        screen.blit(background, (0, 0))
        if starting:
            n = 0
            time = int(time * 0.8)
            if randint(0, 1):
                solution_type = True
                some = choice(pairs)
                solution = (some[0], some[1])
                var = [some[0] + some[1]]
                for i in range(lily_num - 1):
                    some = choice(pairs)
                    while some[0] + some[1] in var:
                        some = choice(pairs)
                    var.append(some[0] + some[1])
            else:
                solution_type = False
                some = choice(pairs)
                if some[0] < some[1]:
                    some[0], some[1] = some[1], some[0]
                solution = (some[0], some[1])
                var = [some[0] - some[1]]
                for i in range(lily_num - 1):
                    some = choice(pairs)
                    if some[0] < some[1]:
                        some[0], some[1] = some[1], some[0]
                    while some[0] - some[1] in var:
                        some = choice(pairs)
                        if some[0] < some[1]:
                            some[0], some[1] = some[1], some[0]
                    var.append(some[0] - some[1])
            shuffle(var)
            start_lily = Lily.image.copy()
            start_lily_coords = (int(0.14 * size_x), int(0.4 * size_y))
            frog_coords = (int(0.18 * size_x), int(0.44 * size_y))
            lily_group = pygame.sprite.Group()
            # for i in range(lily_num):
            #     lily = Lily(randint(start_lily_coords[0] + Lily.image.get_width(),
            #                         size_x - Lily.image.get_width()),
            #                 randint(90, size_y - Lily.image.get_height() - 40), str(var[i]))
            #     f = True
            #     while f:
            #         for sprite in lily_group:
            #             if pygame.sprite.collide_mask(sprite, lily):
            #                 lily = Lily(randint(start_lily_coords[0] + Lily.image.get_width(),
            #                                     size_x - Lily.image.get_width()),
            #                             randint(90, size_y - Lily.image.get_height() - 40), str(var[i]))
            #                 break
            #         else:
            #             f = False
            #     lily_group.add(lily)
            lily_group.add(Lily(int(0.62 * size_x), size_y // 4 - int(size_y / 4.8) // 2, str(var[0])))
            lily_group.add(Lily(int(0.72 * size_x), size_y // 2 - int(size_y / 4.8) // 2, str(var[1])))
            lily_group.add(Lily(int(0.62 * size_x), size_y // 4 * 3 - int(size_y / 4.8) // 2, str(var[2])))
            for lily in lily_group:
                if solution_type:
                    if solution[0] + solution[1] == lily.num:
                        drowned = lily
                        break
                else:
                    if solution[0] - solution[1] == lily.num:
                        drowned = lily
                        break
            score_out = font.render(f'Счёт: {score}', False, pygame.color.Color('black'))
            record_out = font.render(f'Лучший: {record}', False, pygame.color.Color('black'))
            clock.tick()
            starting = False
            if not win_animation:
                waiting = True
        elif waiting:
            if n >= time:
                wrong = 2
                x, y = frog_coords
                waiting = False
            n += clock.tick()
            screen.fill((238, 238, 238), timer_size)
            screen.fill((255, 0, 0), (timer_size[0] + 3, 23, (timer_size[2] - 6) * n // time, 14))
            screen.blit(start_lily, start_lily_coords)
            screen.blit(frog, frog_coords)
            string_rendered = font.render(f"{solution[0]} {'+' if solution_type else '-'} "
                                          f"{solution[1]}", True, pygame.Color('black'))
            screen.blit(string_rendered, (timer_size[0], 45))
            lily_group.draw(screen)
            screen.blit(score_out, (0, size_y - 40))
            screen.blit(record_out, (int(size_x * 0.7), size_y - 40))
        elif ending:
            if x >= xe - frog.get_width():
                ending = False
                x = xe
            tick = clock.tick()
            x += speed_x * tick / 1000
            y += speed_y * tick / 1000
            screen.blit(start_lily, start_lily_coords)
            lily_group.draw(screen)
            screen.blit(pygame.transform.rotate(frog_jump, angle), (int(x), int(y)))
            screen.blit(score_out, (0, size_y - 40))
            screen.blit(record_out, (int(size_x * 0.7), size_y - 40))
        elif win_animation:
            if x <= xe:
                win_animation = False
                waiting = True
                x = xe
                clock.tick()
            tick = clock.tick()
            x += speed_x * tick / 1000
            y += speed_y * tick / 1000
            screen.blit(start_lily, (x - 0.04 * size_x, y - 0.04 * size_y))
            screen.blit(frog, (x, y))
            del_x = int(x - xe)
            del_y = int(y - ye)
            lily_group.update((del_x, del_y))
            lily_group.draw(screen)
            lily_group.update((-del_x, -del_y))
        else:
            screen.blit(score_out, (0, size_y - 40))
            screen.blit(record_out, (int(size_x * 0.7), size_y - 40))
            start_lily = Lily.image_drown.copy()
            lily_group.update(None)
            lily_group.draw(screen)
            screen.blit(start_lily, start_lily_coords)
            if not wrong:
                screen.blit(frog, (int(x), int(y)))
                pygame.display.flip()
                score += 1
                all_score += 1
                record = max(record, score)
                bul.play(0)
                sleep(0.5)
                win.play(0)
                sleep(1.5)
                xe, ye = frog_coords
                speed_x, speed_y = -speed_x, -speed_y
                win_animation = True
                starting = True
                clock.tick()
                start_lily = Lily.image.copy()
            else:
                pygame.display.flip()
                score = 0
                bul.play(0)
                sleep(0.5)
                lose.play(0)
                sleep(3)
                time = 12500
                starting = True

        pygame.display.flip()

    pygame.quit()