import pygame
import random
import os

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Torre Medieval - Subida Pixel Art")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 28)

# Cores
STONE_GRAY = (100, 100, 100)
DARK_STONE = (70, 70, 70)
WOOD_BROWN = (139, 69, 19)
WOOD_LIGHT = (160, 82, 45)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)

POWERUP_TIME = 5
PLATFORM_SPACING = 100

# Load sprites
sprite_folder = "sprites"
sprites = [pygame.image.load(os.path.join(sprite_folder, f"sprite_{i}.png")).convert_alpha() for i in range(10)]

# Background
def draw_stone_background(surface):
    tile_size = 40
    for y in range(0, HEIGHT, tile_size):
        for x in range(0, WIDTH, tile_size):
            base_color = STONE_GRAY if (x // tile_size + y // tile_size) % 2 == 0 else DARK_STONE
            variation = random.randint(-10, 10)
            color = tuple(max(0, min(255, c + variation)) for c in base_color)
            pygame.draw.rect(surface, color, (x, y, tile_size, tile_size))
            pygame.draw.line(surface, DARK_STONE, (x + 5, y + 10), (x + 35, y + 10), 2)
            pygame.draw.line(surface, DARK_STONE, (x + 5, y + 30), (x + 35, y + 30), 2)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = sprites[0]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 70))
        self.vel_y = 0
        self.jumping = False
        self.powered_up = False
        self.powerup_end_time = 0
        self.anim_index = 0
        self.jump_anim = False
        self.anim_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            if self.rect.left < 0:
                self.rect.left = 0
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH

        self.vel_y += 0.5
        self.rect.y += self.vel_y

        if self.vel_y > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.jumping = False
                self.jump_anim = False
                self.image = sprites[0]

        power_hits = pygame.sprite.spritecollide(self, powerups, True)
        for p in power_hits:
            self.powered_up = True
            self.powerup_end_time = pygame.time.get_ticks() + POWERUP_TIME * 1000

        if self.powered_up and pygame.time.get_ticks() > self.powerup_end_time:
            self.powered_up = False

        if self.rect.top > HEIGHT:
            game_over()

        self.animate()

    def animate(self):
        if self.jump_anim:
            now = pygame.time.get_ticks()
            if now - self.anim_timer > 100:
                self.anim_index = (self.anim_index + 1) % 3
                self.image = sprites[3 + self.anim_index]
                self.anim_timer = now

    def jump(self):
        if not self.jumping:
            self.vel_y = -18 if self.powered_up else -12
            self.jumping = True
            self.jump_anim = True
            self.anim_index = 0
            self.anim_timer = pygame.time.get_ticks()
            self.image = sprites[3]

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w=80, h=20):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(x=x, y=y)
        self.draw_platform()

    def draw_platform(self):
        w, h = self.image.get_size()
        self.image.fill(WOOD_BROWN)
        pygame.draw.rect(self.image, (100, 50, 10), (0, 0, w, h), 1)
        for i in range(0, w, 12):
            pygame.draw.line(self.image, WOOD_LIGHT, (i, 0), (i, h), 1)
        for j in range(0, h, 5):
            pygame.draw.line(self.image, (110, 70, 40), (0, j), (w, j), 1)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x + 40, y - 15))
        self.draw_powerup()

    def draw_powerup(self):
        pygame.draw.circle(self.image, (200, 180, 50), (11, 11), 10)
        pygame.draw.circle(self.image, (255, 255, 120), (7, 7), 4)
        pygame.draw.rect(self.image, BLACK, (10, 4, 2, 14))
        pygame.draw.rect(self.image, BLACK, (4, 10, 14, 2))

def game_over():
    global running
    print("Game Over! Pontuação:", score // 10)
    running = False

def maybe_create_powerup(platform, chance=0.25):
    if random.random() < chance:
        p = PowerUp(platform.rect.x, platform.rect.y)
        all_sprites.add(p)
        powerups.add(p)

# Grupos
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Jogador
player = Player()
all_sprites.add(player)

# Plataformas iniciais
initial_heights = [HEIGHT - 50]
for i in range(1, 8):
    initial_heights.append(initial_heights[-1] - random.randint(80, 100))

for y in initial_heights:
    plat = Platform(random.randint(0, WIDTH - 80), y)
    platforms.add(plat)
    all_sprites.add(plat)

score = 0
max_height = player.rect.top
last_platform_y = min(p.rect.y for p in platforms)

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()

    all_sprites.update()
    draw_stone_background(screen)

    # Scroll da torre
    if player.rect.top < HEIGHT // 3:
        diff = HEIGHT // 3 - player.rect.top
        player.rect.top = HEIGHT // 3
        for plat in platforms:
            plat.rect.y += diff
        for pwr in powerups:
            pwr.rect.y += diff
        score += diff

    # Criar nova plataforma acima
    if player.rect.top < max_height - PLATFORM_SPACING:
        new_y = last_platform_y - random.randint(80, 100)
        new_x = random.randint(20, WIDTH - 100)
        new_p = Platform(new_x, new_y)
        platforms.add(new_p)
        all_sprites.add(new_p)
        maybe_create_powerup(new_p)
        last_platform_y = new_y
        max_height = player.rect.top

    # Limpeza
    for plat in platforms:
        if plat.rect.top > HEIGHT:
            plat.kill()
    for pwr in powerups:
        if pwr.rect.top > HEIGHT:
            pwr.kill()

    all_sprites.draw(screen)
    screen.blit(font.render(f"Pontuação: {score // 10}", True, WHITE), (10, 10))

    if player.powered_up:
        time_left = (player.powerup_end_time - pygame.time.get_ticks()) // 1000 + 1
        screen.blit(font.render(f"Power-up: {time_left}s", True, RED), (10, 50))

    pygame.display.flip()

pygame.quit()