import pygame
import os
import random


def lvl_choose(lvl, up):
    if lvl < Progress().get_char()[5] and up:
        lvl += 1
    elif lvl > 1 and not up:
        lvl -= 1
    return lvl


class Progress:
    def __init__(self):
        # sp[dc, hc, hp, damage, money, lvl, bul_count]
        with open(f"levels/chars.txt", "r") as file:
            sp = file.readlines()
            self.sp = [int(i.split()[2]) for i in sp]

    def get_char(self):
        return self.sp

    def change(self, choice):
        if choice == 1:
            if self.sp[0] <= self.sp[4]:
                self.sp[3] += 20
                self.sp[0] += 50
                self.sp[4] -= 50
        if choice == 2:
            if self.sp[2] <= self.sp[4]:
                self.sp[1] += 50
                self.sp[2] += 20
                self.sp[4] -= 50
        self.save()

    def money_earn(self, money):
        self.sp[4] = money
        self.save()

    def bullets(self, n):
        self.sp[6] += n
        self.save()

    def save(self):
        with open(f"levels/chars.txt", "w") as filew:
            filew.write(f"""dc = {self.sp[0]}
hc = {self.sp[1]}
hp = {self.sp[2]}
damage = {self.sp[3]}
money = {self.sp[4]}
lvl = {self.sp[5]}
bul_c = {self.sp[6]}""")


class LoadLevel:
    def __init__(self, num):
        # sp[mob_counts, weapon_power, enemy_health]
        with open(f"levels/level {num}.txt", "r") as file:
            sp = file.readlines()
            self.sp = [i.split()[2] for i in sp]

    def mob_counter(self):
        return int(self.sp[0])

    def weapon_power(self):
        return int(self.sp[1])

    def enemy_health(self):
        return int(self.sp[2])


def load_image(name, colorkey=None):
    fullname = os.path.join("sprites", name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
    image = pygame.image.load(fullname)
    return image


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__(bullet_sprites)
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("gray"), (2, 2), 2)
        self.rect = pygame.Rect(x - speed + 15, y, 4, 4)
        self.vx = 1 * speed * random.uniform(0.7, 1)
        self.vy = 1 * speed // 10
        self.damage = 40

    def update(self):
        if (0 < self.rect.x < 1920 or 0 < self.rect.y < 1000) and not pygame.sprite.spritecollideany(self, enemies_sprites):
            self.damage *= 0.995
            self.rect = self.rect.move(self.vx, self.vy)
            return False
        else:
            return True

    def get_damage(self):
        return self.damage


class Crime:
    pass


class Narco(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemies_sprites)
        self.frames = []
        self.cut_sheet(load_image("zombie_anim.png"), 16, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 2000
        self.rect.y = random.randint(20, 900)
        self.y = self.rect.y
        self.speed = None
        self.vx = x
        self.vy = y
        self.hp = 120

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if not pygame.sprite.spritecollideany(self, bullet_sprites):
            self.rect = self.rect.move(self.vx, self.vy)
        elif self.hp:
            self.hp -= 40
            self.rect = self.rect.move(self.vx, self.vy)
        elif 0 < self.rect.x < 2100:
            return "-hp"
        else:
            return True


class Gun(pygame.sprite.Sprite):
    image = load_image("char.png")

    def __init__(self):
        super().__init__(all_sprites)
        # self.char[hp, power]
        self.char = [0, 0]
        self.image = Gun.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y
        if pygame.sprite.spritecollideany(self, enemies_sprites):
            self.char[0] -= 30
            return "d"
        if self.char[0] < 0:
            return True

    def change_stats(self, stat):
        self.char[0] = stat[0]
        self.char[1] = stat[1]

    def get_char(self):
        return self.char


def end(stat, killed):
    size = width, height = 1000, 1000
    pygame.init()
    screen = pygame.display.set_mode(size)
    font = pygame.font.Font(None, 25)
    if not killed:
        text = font.render(f"Конец игры, вы расстреляли {stat} зомби из страйкбольного оружия", True, (0, 255, 255))
    else:
        text = font.render(f"Вас побили дубинкой", True, (0, 255, 255))
    text1 = font.render(f"Выйти отсюда", True, (0, 255, 255))
    pygame.draw.rect(screen, "green", (350, 400, 300, 50), 2)
    pygame.draw.rect(screen, "green", (350, 465, 300, 50), 2)
    pygame.draw.rect(screen, "green", (350, 530, 300, 50), 2)
    screen.blit(text, (300, 350))
    screen.blit(font.render(f"Статистика", True, (0, 255, 255)), (350, 465))
    screen.blit(text1, (350, 400))
    screen.blit(font.render(f"в главное меню", True, (0, 255, 255)), (350, 530))
    pygame.mouse.set_visible(True)
    pygame.display.flip()
    run = True
    mode = 0
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                mode = 3
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 350 < event.pos[0] < 650 and 400 < event.pos[1] < 450:
                    run = False
                    mode = 3
                if 350 < event.pos[0] < 650 and 465 < event.pos[1] < 515:
                    run = False
                    mode = 2
                if 350 < event.pos[0] < 650 and 530 < event.pos[1] < 580:
                    run = False
                    mode = 0
    pygame.quit()
    return mode


def start():
    size = width, height = 1000, 1000
    pygame.init()
    screen = pygame.display.set_mode(size)
    global lvl
    font = pygame.font.Font(None, 50)
    text = font.render("начать", True, (0, 255, 255))
    text1 = font.render(f"Выйти отсюда", True, (0, 255, 255))
    text2 = font.render("Страйкбольный ак 47 против зомби", True, (0, 255, 255))
    pygame.display.flip()
    run = True
    mode = 0
    while run:
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, "green", (350, 400, 300, 50), 2)
        pygame.draw.rect(screen, "green", (350, 465, 300, 50), 2)
        pygame.draw.rect(screen, "green", (350, 530, 300, 50), 2)
        screen.blit(text2, (200, 300))
        screen.blit(text, (350, 400))
        screen.blit(font.render(f"статистика", True, (0, 255, 255)), (350, 465))
        screen.blit(text1, (350, 530))
        screen.blit(font.render(f"выбор уровня", True, (0, 255, 255)), (375, 590))
        pygame.draw.rect(screen, "blue", (300, 620, 50, 50), 0)
        pygame.draw.rect(screen, "blue", (650, 620, 50, 50), 0)
        pygame.draw.polygon(screen, "green", [(345, 625), (305, 645), (345, 665)], 0)
        pygame.draw.polygon(screen, "green", [(655, 625), (695, 645), (655, 665)], 0)
        screen.blit(font.render(f"{lvl}", True, (0, 255, 255)), (485, 630))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                mode = 3
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 350 < event.pos[0] < 650 and 400 < event.pos[1] < 450:
                    run = False
                    mode = 1
                if 350 < event.pos[0] < 650 and 465 < event.pos[1] < 515:
                    run = False
                    mode = 2
                if 350 < event.pos[0] < 650 and 530 < event.pos[1] < 580:
                    run = False
                    mode = 3
                if 300 < event.pos[0] < 350 and 620 < event.pos[1] < 670:
                    lvl = lvl_choose(lvl, False)
                elif 650 < event.pos[0] < 700 and 620 < event.pos[1] < 670:
                    lvl = lvl_choose(lvl, True)
        pygame.display.flip()
    pygame.quit()
    return mode


def statistics():
    size = width, height = 1000, 1000
    pygame.init()
    screen = pygame.display.set_mode(size)
    run = True
    stats = Progress()
    font = pygame.font.Font(None, 50)
    while run:
        screen.blit(font.render(f"пуль выпущено : {stats.get_char()[6]}", True, (0, 255, 0)), (30, 161 * 0 + 30))
        screen.blit(font.render(f"урон от оружия: {stats.get_char()[3]}", True, (0, 255, 0)), (30, 161 * 1 + 30))
        screen.blit(font.render(f"Деньги: {stats.get_char()[4]}", True, (0, 255, 0)), (30, 161 * 2 + 30))
        screen.blit(font.render(f"Доступные уровни: {stats.get_char()[5]}", True, (0, 255, 0)), (30, 161 * 3 + 30))
        screen.blit(font.render(f"", True, (0, 255, 0)), (30, 161 * 4 + 30))
        screen.blit(font.render(f"", True, (0, 255, 0)), (30, 161 * 5 + 30))
        screen.blit(font.render(f"", True, (0, 255, 0)), (30, 161 * 6 + 30))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.flip()
    pygame.quit()
    return 0


def game():
    # pygame init
    size = 1920, 1080
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.flip()
    fps = 60
    run = True
    SPAWN_MOBS = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_MOBS, 500)
    clock = pygame.time.Clock()

    # sprites
    up_x_coords = 235
    up_y_coords = 960
    global ups_sprites
    global bullet_sprites
    global all_sprites
    global lvl
    gun = Gun()
    hp_up = pygame.sprite.Sprite()
    bullet_up = pygame.sprite.Sprite()
    bullet_up.image = load_image("bullet.png")
    bullet_up.rect = bullet_up.image.get_rect()
    bullet_up.rect.x = up_x_coords + 80
    bullet_up.rect.y = up_y_coords + 30
    all_sprites.add(bullet_up)
    hp_up.image = load_image("hp_up.png")
    hp_up.rect = hp_up.image.get_rect()
    hp_up.rect.x = up_x_coords
    hp_up.rect.y = up_y_coords + 30
    all_sprites.add(hp_up)

    # logic
    bullets = []
    enemies = []
    kill = False
    level = LoadLevel(lvl)
    c = 0
    enemies.append(Narco(-3, 0))
    shoot = False
    stats = Progress()
    gun.change_stats([stats.get_char()[2], stats.get_char()[3]])
    money_val = stats.get_char()[4]
    bul_c = 0
    killed = False
    while run:
        screen.fill((255, 255, 255))
        all_sprites.draw(screen)
        enemies_sprites.draw(screen)
        bullet_sprites.draw(screen)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            stats.change(2)
            gun.change_stats([stats.get_char()[2], stats.get_char()[3]])
            money_val = stats.get_char()[4]
        elif keys[pygame.K_2]:
            stats.change(1)
            gun.change_stats([stats.get_char()[2], stats.get_char()[3]])
            money_val = stats.get_char()[4]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                shoot = True
            if event.type == pygame.MOUSEMOTION:
                pygame.mouse.set_visible(False)
                ug = gun.update(event.pos[0] - 33, event.pos[1] - 23)
                if ug == 'd':
                    kill = True
                elif ug:
                    run = False
                    killed = True

            if event.type == pygame.MOUSEBUTTONUP:
                shoot = False
            if event.type == SPAWN_MOBS:
                enemies.append(Narco(-3, 0))
            if shoot and event.type != SPAWN_MOBS:
                bul_c += 1
                bullets.append(Bullet(event.pos[0] + 99, event.pos[1] - 28, gun.get_char()[1]))
        for i in bullets:
            if i.update():
                i.kill()
                bullets.remove(i)
        for i in enemies:
            if i.update() or kill:
                i.kill()
                enemies.remove(i)
                kill = False
                c += 1
                money_val += 10
                stats.money_earn(money_val)

        # upgrade interface
        font = pygame.font.Font(None, 50)
        screen.blit(font.render(f"1", True, (0, 255, 0)), (up_x_coords + 15, up_y_coords))
        pygame.draw.rect(screen, "green", (up_x_coords, up_y_coords + 30, 50, 50), 3)
        screen.blit(font.render(f"2", True, (0, 255, 0)), (up_x_coords + 95, up_y_coords))
        pygame.draw.rect(screen, "green", (up_x_coords + 80, up_y_coords + 30, 50, 50), 3)
        screen.blit(pygame.font.Font(None, 30).render(f"{stats.get_char()[0]}", True, (0, 255, 0)), (up_x_coords + 90, up_y_coords + 90))
        screen.blit(pygame.font.Font(None, 30).render(f"{stats.get_char()[1]}", True, (0, 255, 0)),
                    (up_x_coords + 10, up_y_coords + 90))
        text = font.render(f"HP: {gun.get_char()[0]}", True, (0, 255, 0))
        screen.blit(text, (500, 1000))
        text = font.render(f"MOBs: {level.mob_counter() - c}", True, (0, 255, 0))
        screen.blit(text, (700, 1000))

        # stat interface
        screen.blit(font.render(f"money: {money_val}", True, (0, 255, 0)), (30, 1000))

        # pygame init
        clock.tick(fps)
        pygame.display.flip()
        if c == level.mob_counter():
            run = False

    pygame.quit()
    stats.bullets(bul_c)
    return end(c, killed)


lvl = 1
if __name__ == "__main__":
    mode = 0
    while mode != 3:
        if mode == 0:
            mode = start()
        if mode == 1:
            ups_sprites = pygame.sprite.Group()
            enemies_sprites = pygame.sprite.Group()
            bullet_sprites = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            mode = game()
        elif mode == 2:
            mode = statistics()