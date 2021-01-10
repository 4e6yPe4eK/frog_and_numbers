import pygame
import os
from random import choice, shuffle, randint
from math import acos, pi, sqrt
from time import sleep
import menuu
pygame.init()
pygame.mixer.init()
size_x, size_y = 1155, 650
pygame.display.set_caption('Frog and numbers')
screen = pygame.display.set_mode((size_x, size_y))
font = pygame.font.Font(os.path.join('data', 'font.ttf'), 48)


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

    def __init__(self, x, y, text, par):
        super().__init__()
        self.par = par
        self.image = Lily.image.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.num = int(text)
        string_rendered = font.render(text, True, pygame.Color('blue'))
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
            if self != self.par.drowned:
                self.image = Lily.image_drown.copy()
        elif args and args[0].type == pygame.MOUSEBUTTONDOWN and self.collide(args[0].pos):
            self.par.jump.play(0)
            self.par.x, self.par.y = self.par.frog_coords
            self.par.xe = self.rect.x + (self.image.get_width() - self.par.frog.get_width()) // 2
            self.par.ye = self.rect.y + (self.image.get_height() - self.par.frog.get_height()) // 2
            self.par.speed_x = abs(self.par.xe - self.par.x - self.par.frog.get_width())
            self.par.speed_y = self.par.ye - self.par.y
            ac = sqrt((self.par.xe - self.par.x) ** 2 + self.par.ye ** 2)
            ab = self.par.y
            bc = sqrt((self.par.xe - self.par.x) ** 2 + (self.par.ye - self.par.y) ** 2)
            self.par.angle = int(acos((ac ** 2 - ab ** 2 - bc ** 2) / (-2 * ab * bc)) / pi * -180)
            self.par.n = 0
            self.par.ending = True
            self.par.waiting = False
            self.par.clock.tick()
            if self.par.solution_type and args[1][0] + args[1][1] == self.num or\
                    not self.par.solution_type and args[1][0] - args[1][1] == self.num:
                self.par.wrong = 0
            else:
                self.par.wrong = 1


class FrogGame:
    def __init__(self, vol0, vol1):
        self.win = pygame.mixer.Sound(os.path.join('data', 'win.wav'))
        self.win.set_volume(vol0)
        self.lose = pygame.mixer.Sound(os.path.join('data', 'lose.wav'))
        self.lose.set_volume(vol0)
        self.bul = pygame.mixer.Sound(os.path.join('data', 'bul.wav'))
        self.bul.set_volume(vol0)
        self.jump = pygame.mixer.Sound(os.path.join('data', 'jump.wav'))
        self.jump.set_volume(vol0)
        self.background = pygame.transform.scale(load_image('water_bresk.jpeg'),
                                                 (size_x, size_y))
        self.frog = pygame.transform.scale(pygame.transform.rotate(load_image('frog.png'), -90),
                                           (int(0.06 * size_x), int(0.13 * size_y)))
        self.frog_jump = pygame.transform.scale(load_image('frog_jump.png'),
                                                (int(0.1 * size_x), int(0.2 * size_y)))
        self.exit = pygame.transform.scale(load_image('exit.png'),
                                           (50, 50))
        self.all_score = 0
        self.running = True
        self.waiting = False
        self.ending = False
        self.win_animation = False
        self.starting = True
        self.lily_group = None
        self.start_lily = None
        self.start_lily_coords = None
        self.frog_coords = None
        self.solution = None
        self.wrong = 1
        self.score_out = None
        self.record_out = None
        self.solution_type = True
        self.drowned = None
        self.record, self.score = 0, 0
        self.lily_num = 3
        self.pairs = []
        for i in range(1, 100):
            for j in range(1, 100):
                self.pairs.append([i, j])
        self.clock = pygame.time.Clock()
        self.time = 12500
        self.angle = 0
        self.n = 0
        self.x, self.y, self.xe, self.ye = int(0.18 * size_x), int(0.44 * size_y), 0, 0
        self.speed_x, self.speed_y = 0, 0
        self.timer_size = (int(0.28 * size_x), 20, int(0.45 * size_x), 20)
        self.handler()

    def starting_event(self):
        self.n = 0
        self.time = int(self.time * 0.8)
        if randint(0, 1):
            self.solution_type = True
            some = choice(self.pairs)
            self.solution = (some[0], some[1])
            var = [some[0] + some[1]]
            for i in range(2):
                some = choice(self.pairs)
                while some[0] + some[1] in var:
                    some = choice(self.pairs)
                var.append(some[0] + some[1])
        else:
            self.solution_type = False
            some = choice(self.pairs)
            if some[0] < some[1]:
                some[0], some[1] = some[1], some[0]
            self.solution = (some[0], some[1])
            var = [some[0] - some[1]]
            for i in range(2):
                some = choice(self.pairs)
                if some[0] < some[1]:
                    some[0], some[1] = some[1], some[0]
                while some[0] - some[1] in var:
                    some = choice(self.pairs)
                    if some[0] < some[1]:
                        some[0], some[1] = some[1], some[0]
                var.append(some[0] - some[1])
        shuffle(var)
        self.start_lily = Lily.image.copy()
        self.start_lily_coords = (int(0.18 * size_x - 0.04 * size_x), int(self.y - 0.04 * size_y))
        self.frog_coords = (int(0.18 * size_x), self.y)
        self.lily_group = pygame.sprite.Group()
        self.lily_group.add(Lily(int(0.62 * size_x), size_y // 4 - int(size_y / 4.8) // 2, str(var[0]), self))
        self.lily_group.add(Lily(int(0.72 * size_x), size_y // 2 - int(size_y / 4.8) // 2, str(var[1]), self))
        self.lily_group.add(Lily(int(0.62 * size_x), size_y // 4 * 3 - int(size_y / 4.8) // 2, str(var[2]), self))
        for lily in self.lily_group:
            if self.solution_type:
                if self.solution[0] + self.solution[1] == lily.num:
                    self.drowned = lily
                    break
            else:
                if self.solution[0] - self.solution[1] == lily.num:
                    self.drowned = lily
                    break
        self.score_out = font.render(f'Счёт: {self.score}', False, pygame.color.Color('blue'))
        self.record_out = font.render(f'Лучший: {self.record}', False, pygame.color.Color('blue'))
        self.clock.tick()
        self.starting = False
        if not self.win_animation:
            self.waiting = True

    def waiting_event(self):
        if self.n >= self.time:
            self.wrong = 2
            self.x, self.y = self.frog_coords
            self.waiting = False
        self.n += self.clock.tick()
        screen.fill((238, 238, 238), self.timer_size)
        screen.fill((255, 0, 0), (self.timer_size[0] + 3, 23, (self.timer_size[2] - 6) * self.n // self.time, 14))
        screen.blit(self.start_lily, self.start_lily_coords)
        screen.blit(self.frog, self.frog_coords)
        string_rendered = font.render(f"{self.solution[0]} {'+' if self.solution_type else '-'} "
                                      f"{self.solution[1]}", True, pygame.Color('blue'))
        screen.blit(string_rendered, (self.timer_size[0], 45))
        self.lily_group.draw(screen)
        screen.blit(self.score_out, (10, size_y - 60))
        screen.blit(self.record_out, (int(size_x * 0.75), size_y - 60))
        screen.blit(self.exit, (0, 0))

    def ending_event(self):
        if self.x >= self.xe - self.frog.get_width():
            self.ending = False
            self.x = self.xe
        tick = self.clock.tick()
        self.x += self.speed_x * tick / 1000
        self.y += self.speed_y * tick / 1000
        screen.blit(self.start_lily, self.start_lily_coords)
        self.lily_group.draw(screen)
        screen.blit(pygame.transform.rotate(self.frog_jump, self.angle), (int(self.x), int(self.y)))
        screen.blit(self.score_out, (10, size_y - 60))
        screen.blit(self.record_out, (int(size_x * 0.75), size_y - 60))

    def win_animation_event(self):
        if self.x <= self.xe:
            self.win_animation = False
            self.waiting = True
            self.x = self.xe
            self.clock.tick()
        tick = self.clock.tick()
        self.x += self.speed_x * tick / 1000
        screen.blit(self.start_lily, (self.x - 0.04 * size_x, self.y - 0.04 * size_y))
        screen.blit(self.frog, (self.x, self.y))
        del_x = int(self.x - self.xe)
        self.lily_group.update((del_x, 0))
        self.lily_group.draw(screen)
        self.lily_group.update((-del_x, 0))

    def scoring_event(self):
        screen.blit(self.score_out, (10, size_y - 60))
        screen.blit(self.record_out, (int(size_x * 0.75), size_y - 60))
        self.start_lily = Lily.image_drown.copy()
        self.lily_group.update(None)
        self.lily_group.draw(screen)
        screen.blit(self.start_lily, self.start_lily_coords)
        if not self.wrong:
            screen.blit(self.frog, (int(self.x), int(self.y)))
            pygame.display.flip()
            self.score += 1
            self.all_score += 1
            self.record = max(self.record, self.score)
            self.bul.play(0)
            sleep(0.5)
            self.win.play(0)
            sleep(1.5)
            self.xe, self.ye = self.frog_coords
            self.speed_x, self.speed_y = -self.speed_x, -self.speed_y
            self.win_animation = True
            self.starting = True
            self.clock.tick()
            self.start_lily = Lily.image.copy()
        else:
            pygame.display.flip()
            self.score = 0
            self.bul.play(0)
            sleep(0.5)
            self.lose.play(0)
            sleep(3)
            self.time = 12500
            self.x, self.y = int(0.18 * size_x), int(0.44 * size_y)
            self.starting = True

    def handler(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.waiting:
                        self.lily_group.update(event, self.solution)
                    if event.pos[0] <= 50 and event.pos[1] <= 50:
                        menuu.Menu()
                        self.running = False
            screen.blit(self.background, (0, 0))
            if self.starting:
                self.starting_event()
            elif self.waiting:
                self.waiting_event()
            elif self.ending:
                self.ending_event()
            elif self.win_animation:
                self.win_animation_event()
            else:
                self.scoring_event()
            pygame.display.flip()


if __name__ == "__main__":
    FrogGame(1, 1)
    pygame.quit()