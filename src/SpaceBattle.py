import pygame
import sys
import random
import math
from pygame.math import Vector2

pygame.init()
pygame.mixer.init()

# Caricamento suoni
sparo = pygame.mixer.Sound("sounds/shot.mp3")
colonna_sonora = pygame.mixer.Sound("sounds/colonna_sonora.mp3")
game_over_sound = pygame.mixer.Sound("sounds/game_over.mp3")
menu_enter_sound = pygame.mixer.Sound("sounds/menu_enter.mp3")
menu_exit_sound = pygame.mixer.Sound("sounds/menu_exit.mp3")

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Battle")
clock = pygame.time.Clock()
FPS = 60

# Imposta timer per spawn
pygame.time.set_timer(pygame.USEREVENT+1, 1500)  # Nemici ogni 1.5 sec
pygame.time.set_timer(pygame.USEREVENT+2, 10000) # Cuori ogni 10 sec
pygame.time.set_timer(pygame.USEREVENT+3, 20000) # Congelamento (snowflake) ogni 20 sec
pygame.time.set_timer(pygame.USEREVENT+5, 40000) # Scudi ogni 40 sec

# Immagine di sfondo
background_image = pygame.image.load("images/bg.png").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 50, 50)
NEON_BLUE = (0, 255, 255)
NEON_YELLOW = (255, 255, 0)
NEON_PURPLE = (200, 0, 200)

# Colori proiettili
BULLET_COLORS = {
    1: (255, 255, 0),
    2: (0, 255, 255),
    3: (255, 165, 0),
    4: (144, 238, 144),
    5: (255, 0, 255)
}

# Variabili globali
kill_count = 0
enemy_freeze_end_time = 0
freeze_duration = 5000

# Variabili per spawn basato sui kill
next_fire_spawn = 50      # Ogni 50 kill compare il power-up "fuoco"
next_shooter_spawn = 100  # Ogni 100 kill compare il nemico speciale che spara

# Funzioni per il record
def load_highscore():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_highscore(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

highscore = load_highscore()

# Gruppi di sprite
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
hearts = pygame.sprite.Group()
snowflakes = pygame.sprite.Group()
firepowers = pygame.sprite.Group()
shieldpowers = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()  # Proiettili dei nemici speciali

# ------------------ FUNZIONE DI CARICAMENTO IMMAGINI ------------------
def load_image(path, scale=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except Exception as e:
        print(f"Errore nel caricamento dell'immagine {path}: {e}")
        return None

# ------------------ CLASSI ------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image("images/player.png", scale=(50, 50))
        if self.original_image is None:
            self.original_image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, NEON_GREEN, [(20, 0), (0, 40), (40, 40)])
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.pos = Vector2(self.rect.center)
        self.speed = 5
        self.lives = 3
        self.shoot_delay = 250  # cooldown in ms
        self.last_shot = pygame.time.get_ticks()
        self.fire_level = 1
        self.bullet_speed = 10
        self.mask = pygame.mask.from_surface(self.image)
        self.invincible_end_time = 0
        self.hit_anim_end_time = 0
        self.shield_end_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        velocity = Vector2(0, 0)
        if keys[pygame.K_w]:
            velocity.y = -1
        if keys[pygame.K_s]:
            velocity.y = 1
        if keys[pygame.K_a]:
            velocity.x = -1
        if keys[pygame.K_d]:
            velocity.x = 1

        if velocity.length() > 0:
            velocity = velocity.normalize() * self.speed
        self.pos += velocity
        self.pos.x = max(0, min(WIDTH, self.pos.x))
        self.pos.y = max(0, min(HEIGHT, self.pos.y))
        self.rect.center = self.pos

        # Animazione hit
        if current_time < self.hit_anim_end_time:
            base_image = self.original_image.copy()
            if (current_time // 100) % 2 == 0:
                base_image.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
        else:
            base_image = self.original_image.copy()

        # Rotazione verso il mouse
        mouse_pos = Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - self.pos
        angle = math.degrees(math.atan2(direction.y, direction.x)) - 90
        self.image = pygame.transform.rotate(base_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            sparo.play()
            mouse_pos = Vector2(pygame.mouse.get_pos())
            direction = mouse_pos - self.pos
            base_angle = math.degrees(math.atan2(direction.y, direction.x))
            bullet_angles = []
            if self.fire_level == 1:
                bullet_angles = [base_angle]
            elif self.fire_level == 2:
                bullet_angles = [base_angle - 10, base_angle + 10]
            elif self.fire_level == 3:
                bullet_angles = [base_angle - 10, base_angle, base_angle + 10]
            elif self.fire_level == 4:
                bullet_angles = [base_angle - 15, base_angle - 7.5, base_angle + 7.5, base_angle + 15]
            elif self.fire_level >= 5:
                bullet_angles = [base_angle - 15, base_angle - 7.5, base_angle, base_angle + 7.5, base_angle + 15]
            for angle in bullet_angles:
                bullet = Bullet(self.pos, angle, self.fire_level, speed=self.bullet_speed)
                all_sprites.add(bullet)
                bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, fire_level, speed=10):
        super().__init__()
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        color = BULLET_COLORS.get(fire_level, NEON_YELLOW)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.speed = speed
        rad = math.radians(angle)
        self.velocity = Vector2(math.cos(rad), math.sin(rad)) * self.speed
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = fire_level

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, is_boss=False):
        super().__init__()
        self.is_boss = is_boss
        # Per il calcolo, usiamo il valore corrente di kill_count e del livello di fuoco del player.
        if not self.is_boss:
            self.image = load_image("images/enemy.png", scale=(30, 30))
            if self.image is None:
                self.size = random.randint(20, 30)
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, NEON_RED, (self.size // 2, self.size // 2), self.size // 2)
            else:
                self.size = self.image.get_width()
            base_health = 1
            health_increase = kill_count // 50
            # Se il player esiste già, aumenta la salute in funzione del suo fire_level
            fire_bonus = (player.fire_level - 1) if 'player' in globals() else 0
            self.health = base_health + health_increase + fire_bonus
            base_speed = 1
            speed_increase = kill_count / 500.0
            fire_speed_bonus = (player.fire_level - 1) * 0.2 if 'player' in globals() else 0
            raw_speed = base_speed + speed_increase + fire_speed_bonus
            # Limitiamo la velocità al 90% della velocità del player (che è 5)
            self.speed = min(raw_speed, 5 * 0.9)
        else:
            self.image = load_image("images/boss.png", scale=(60, 60))
            if self.image is None:
                self.size = 60
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, NEON_PURPLE, (self.size // 2, self.size // 2), self.size // 2)
            else:
                self.size = self.image.get_width()
            base_health = 5
            health_increase = kill_count // 50
            fire_bonus = (player.fire_level - 1) * 2 if 'player' in globals() else 0
            self.health = base_health + health_increase + fire_bonus
            base_speed = 0.5
            speed_increase = kill_count / 800.0
            fire_speed_bonus = (player.fire_level - 1) * 0.1 if 'player' in globals() else 0
            raw_speed = base_speed + speed_increase + fire_speed_bonus
            self.speed = min(raw_speed, 5 * 0.7)
        self.max_health = self.health
        self.rect = self.image.get_rect()
        self.spawn_from_edge()
        self.pos = Vector2(self.rect.center)
        self.original_image = self.image.copy()
        self.mask = pygame.mask.from_surface(self.image)
    
    def spawn_from_edge(self):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.rect.centerx = random.randint(0, WIDTH)
            self.rect.y = -self.size
        elif side == "bottom":
            self.rect.centerx = random.randint(0, WIDTH)
            self.rect.y = HEIGHT + self.size
        elif side == "left":
            self.rect.x = -self.size
            self.rect.centery = random.randint(0, HEIGHT)
        elif side == "right":
            self.rect.x = WIDTH + self.size
            self.rect.centery = random.randint(0, HEIGHT)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time < enemy_freeze_end_time:
            effective_speed = self.speed * 0.5
            self.image = self.original_image.copy()
            self.image.fill((100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            effective_speed = self.speed
            self.image = self.original_image.copy()
        self.mask = pygame.mask.from_surface(self.image)
        direction = player.pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * effective_speed
        self.rect.center = self.pos

class ShooterEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("images/shooter.gif", scale=(80, 80))
        if self.image is None:
            self.size = 80
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(self.image, NEON_PURPLE, (0, 0, self.size, self.size))
        else:
            self.size = self.image.get_width()
        self.rect = self.image.get_rect()
        self.pos = Vector2(random.randint(self.size, WIDTH - self.size), random.randint(self.size, HEIGHT - self.size))
        base_health = 20
        health_increase = kill_count // 50
        fire_bonus = (player.fire_level - 1) * 2 if 'player' in globals() else 0
        self.health = base_health + health_increase + fire_bonus
        self.max_health = self.health
        base_speed = 2
        speed_increase = kill_count / 800.0
        fire_speed_bonus = (player.fire_level - 1) * 0.2 if 'player' in globals() else 0
        raw_speed = base_speed + speed_increase + fire_speed_bonus
        self.speed = min(raw_speed, 5 * 0.8)
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 1000  # Spara ogni 1 sec
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        self.change_dir_time = pygame.time.get_ticks() + random.randint(1000, 3000)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time > self.change_dir_time:
            self.direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
            self.change_dir_time = current_time + random.randint(1000, 3000)
        self.pos += self.direction * self.speed
        if self.pos.x < self.size / 2 or self.pos.x > WIDTH - self.size / 2:
            self.direction.x *= -1
        if self.pos.y < self.size / 2 or self.pos.y > HEIGHT - self.size / 2:
            self.direction.y *= -1
        self.rect.center = self.pos
        if current_time - self.last_shot >= self.shoot_delay:
            self.last_shot = current_time
            bullet = EnemyBullet(self.pos, player.pos)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, speed=7):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_RED, (4, 4), 4)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        direction = target_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * speed
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = 1

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

class Heart(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("images/heart.png", scale=(20, 20))
        if self.image is None:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, NEON_RED, [(10, 0), (20, 7), (16, 18), (4, 18), (0, 7)])
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)

class Snowflake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("images/snowflake.png", scale=(30, 30))
        if self.image is None:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            for angle in range(0, 360, 45):
                x = 15 + 10 * math.cos(math.radians(angle))
                y = 15 + 10 * math.sin(math.radians(angle))
                pygame.draw.line(self.image, NEON_BLUE, (15, 15), (x, y), 2)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        pass

class FirePower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("images/fire.png", scale=(30, 30))
        if self.image is None:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 165, 0), [(15, 0), (5, 25), (15, 20), (25, 25)])
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        pass

class ShieldPower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("images/shield.png", scale=(30, 30))
        if self.image is None:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        pass

# ------------------ SCHERMATE ------------------
def home_screen():
    stars = [{'pos': [random.randint(0, WIDTH), random.randint(0, HEIGHT)], 'speed': random.randint(1, 3)} for _ in range(100)]
    ship_angle = 0
    colonna_sonora.play(-1)
    while True:
        screen.fill(BLACK)
        for star in stars:
            star['pos'][1] += star['speed']
            if star['pos'][1] > HEIGHT:
                star['pos'] = [random.randint(0, WIDTH), 0]
            pygame.draw.circle(screen, WHITE, star['pos'], 1)
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        title_text = title_font.render("SPACE BATTLE", True, NEON_GREEN)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        authors_font = pygame.font.SysFont("Console", 18)
        authors_text = authors_font.render("by Andrea Alfano & Gabriele Merelli", True, NEON_BLUE)
        screen.blit(authors_text, (WIDTH // 2 - authors_text.get_width() // 2, HEIGHT // 3 + 50))
        ship_img = Player().original_image
        ship_angle = (ship_angle + 2) % 360
        rotated_ship = pygame.transform.rotate(ship_img, ship_angle)
        screen.blit(rotated_ship, (WIDTH // 2 - rotated_ship.get_width() // 2, HEIGHT // 2))
        font = pygame.font.SysFont("Arial", 24)
        text = font.render("Premi un tasto per iniziare", True, WHITE)
        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                colonna_sonora.stop()
                return

def game_over_screen(final_score):
    global highscore
    if final_score > highscore:
        highscore = final_score
        save_highscore(highscore)
    stars = [{'pos': [random.randint(0, WIDTH), random.randint(0, HEIGHT)], 'speed': random.randint(1, 3)} for _ in range(100)]
    game_over_sound.play(-1)
    while True:
        screen.fill(BLACK)
        for star in stars:
            star['pos'][1] += star['speed']
            if star['pos'][1] > HEIGHT:
                star['pos'] = [random.randint(0, WIDTH), 0]
            pygame.draw.circle(screen, WHITE, star['pos'], 1)
        title_font = pygame.font.SysFont("Arial", 60)
        title_text = title_font.render("GAME OVER", True, NEON_RED)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        info_font = pygame.font.SysFont("Arial", 24)
        info_text = info_font.render(f"Punteggio: {final_score}    Record: {highscore}", True, WHITE)
        screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 50)))
        sub_text = info_font.render("Premi un tasto per riprovare", True, WHITE)
        screen.blit(sub_text, sub_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                game_over_sound.stop()
                return

def pause_game():
    paused = True
    return_to_home = False
    
    # Carica un font personalizzato se disponibile
    try:
        title_font = pygame.font.Font("fonts/space_age.ttf", 72)
        button_font = pygame.font.Font("fonts/space_age.ttf", 32)
    except:
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        button_font = pygame.font.SysFont("Arial", 32, bold=True)
    
    # Effetti visivi
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Sfondo semi-trasparente
    
    # Testo del titolo con effetto glow
    title_text = title_font.render("PAUSA", True, NEON_BLUE)
    title_glow = title_font.render("PAUSA", True, (100, 100, 255))
    
    # Elementi del menù
    menu_rect = pygame.Rect(0, 0, 400, 400)
    menu_rect.center = (WIDTH//2, HEIGHT//2)
    
    # Pulsanti
    resume_button = pygame.Rect(0, 0, 300, 60)
    resume_button.center = (WIDTH//2, HEIGHT//2 - 30)
    home_button = pygame.Rect(0, 0, 300, 60)
    home_button.center = (WIDTH//2, HEIGHT//2 + 60)
    
    # Animazioni
    angle = 0
    menu_enter_sound.play()
    
    while paused:
        mouse_pos = pygame.mouse.get_pos()
        angle += 2
        current_time = pygame.time.get_ticks()
        
        # Disegna overlay
        screen.blit(overlay, (0, 0))
        
        # Disegna bordo animato
        border_surface = pygame.Surface((menu_rect.w+10, menu_rect.h+10), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, NEON_BLUE[0], (0, 0, border_surface.get_width(), border_surface.get_height()), 
                         border_radius=20)
        rotated_border = pygame.transform.rotate(border_surface, math.sin(angle*0.02)*3)
        screen.blit(rotated_border, rotated_border.get_rect(center=menu_rect.center))
        
        # Disegna sfondo menù
        pygame.draw.rect(screen, (0, 0, 30), menu_rect, border_radius=20)
        pygame.draw.rect(screen, NEON_BLUE, menu_rect, 3, border_radius=20)
        
        # Effetto titolo
        for i in range(5):
            offset = math.sin(angle*0.02 + i)*3
            screen.blit(title_glow, (WIDTH//2 - title_glow.get_width()//2 + offset, 
                                    HEIGHT//3 - 50 + offset))
        screen.blit(title_text, title_text.get_rect(center=(WIDTH//2, HEIGHT//3)))
        
        # Pulsante Resume
        resume_color = NEON_GREEN if resume_button.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(screen, resume_color, resume_button, border_radius=15)
        pygame.draw.rect(screen, NEON_GREEN, resume_button, 3, border_radius=15)
        resume_label = button_font.render("RIPRENDI", True, WHITE)
        screen.blit(resume_label, resume_label.get_rect(center=resume_button.center))
        
        # Pulsante Home
        home_color = NEON_RED if home_button.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(screen, home_color, home_button, border_radius=15)
        pygame.draw.rect(screen, NEON_RED, home_button, 3, border_radius=15)
        home_label = button_font.render("TORNA ALLA HOME", True, WHITE)
        screen.blit(home_label, home_label.get_rect(center=home_button.center))
        
        # Istruzioni
        info_font = pygame.font.SysFont("Arial", 18)
        info_text = info_font.render("Usa il mouse per selezionare le opzioni", True, WHITE)
        screen.blit(info_text, info_text.get_rect(center=(WIDTH//2, HEIGHT - 50)))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    menu_exit_sound.play()
                    paused = False
                if event.key == pygame.K_h:
                    menu_exit_sound.play()
                    paused = False
                    return_to_home = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if resume_button.collidepoint(event.pos):
                        menu_exit_sound.play()
                        paused = False
                    if home_button.collidepoint(event.pos):
                        menu_exit_sound.play()
                        paused = False
                        return_to_home = True
        clock.tick(FPS)
    
    return return_to_home

def main():
    global kill_count, player, next_fire_spawn, next_shooter_spawn, enemy_freeze_end_time
    home_screen()
    # Avvia la musica di sottofondo in loop durante la partita
    pygame.mixer.music.load("sounds/background.mp3")
    pygame.mixer.music.play(-1)
    kill_count = 0
    next_fire_spawn = 50
    next_shooter_spawn = 100

    all_sprites.empty()
    bullets.empty()
    enemies.empty()
    hearts.empty()
    snowflakes.empty()
    firepowers.empty()
    shieldpowers.empty()
    enemy_bullets.empty()

    global player
    player = Player()
    all_sprites.add(player)

    exit_to_home = False
    running = True
    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if pause_game():
                        exit_to_home = True
                        running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.shoot()
            if event.type == pygame.USEREVENT+1:
                if random.random() < 0.1:
                    enemy = Enemy(is_boss=True)
                else:
                    enemy = Enemy(is_boss=False)
                all_sprites.add(enemy)
                enemies.add(enemy)
            elif event.type == pygame.USEREVENT+2:
                if player.lives < 3:
                    heart = Heart()
                    all_sprites.add(heart)
                    hearts.add(heart)
            elif event.type == pygame.USEREVENT+3:
                snowflake = Snowflake()
                all_sprites.add(snowflake)
                snowflakes.add(snowflake)
            elif event.type == pygame.USEREVENT+5:
                shield = ShieldPower()
                all_sprites.add(shield)
                shieldpowers.add(shield)

        all_sprites.update()

        hits = pygame.sprite.groupcollide(enemies, bullets, False, True, collided=pygame.sprite.collide_mask)
        for enemy, hit_list in hits.items():
            for bullet in hit_list:
                enemy.health -= bullet.damage
                if enemy.health <= 0:
                    enemy.kill()
                    kill_count += 1

        enemy_bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True, collided=pygame.sprite.collide_mask)
        if enemy_bullet_hits and current_time >= player.invincible_end_time:
            player.lives -= sum(b.damage for b in enemy_bullet_hits)
            if player.lives <= 0:
                running = False
            else:
                player.invincible_end_time = current_time + 2000
                player.hit_anim_end_time = current_time + 2000

        enemy_hits = pygame.sprite.spritecollide(player, enemies, False, collided=pygame.sprite.collide_mask)
        if enemy_hits and current_time >= player.invincible_end_time:
            player.lives -= 1
            if player.lives <= 0:
                running = False
            else:
                player.invincible_end_time = current_time + 2000
                player.hit_anim_end_time = current_time + 2000

        for heart in pygame.sprite.spritecollide(player, hearts, True):
            if player.lives < 3:
                player.lives += 1
        for snow in pygame.sprite.spritecollide(player, snowflakes, True):
            enemy_freeze_end_time = current_time + freeze_duration
        for fire in pygame.sprite.spritecollide(player, firepowers, True):
            if player.fire_level < 5:
                player.fire_level += 1
                player.bullet_speed = 10 + (player.fire_level - 1) * 2
            else:
                player.bullet_speed += 1
        for shield in pygame.sprite.spritecollide(player, shieldpowers, True):
            player.shield_end_time = current_time + 3000
            player.invincible_end_time = max(player.invincible_end_time, current_time + 3000)

        if kill_count >= next_fire_spawn:
            fire = FirePower()
            all_sprites.add(fire)
            firepowers.add(fire)
            next_fire_spawn += 50

        if kill_count >= next_shooter_spawn:
            shooter = ShooterEnemy()
            all_sprites.add(shooter)
            enemies.add(shooter)
            next_shooter_spawn += 100

        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)
        for enemy in enemies:
            bar_width = enemy.rect.width
            bar_height = 5
            health_ratio = enemy.health / enemy.max_health if enemy.max_health > 0 else 0
            bar_x = enemy.rect.x
            bar_y = enemy.rect.y - bar_height - 2
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            fill_color = (0, 191, 255) if current_time < enemy_freeze_end_time else (0, 255, 0)
            pygame.draw.rect(screen, fill_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))
        info_font = pygame.font.SysFont("Arial", 24)
        score_text = info_font.render(f"Kill: {kill_count}", True, WHITE)
        lives_text = info_font.render(f"Vite: {player.lives}", True, WHITE)
        record_text = info_font.render(f"Record: {highscore}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(record_text, (10, 70))
        if current_time < player.shield_end_time:
            aura_radius = int(max(player.rect.width, player.rect.height) * 0.75 + 15)
            pygame.draw.circle(screen, NEON_YELLOW, player.rect.center, aura_radius, 3)
        pygame.display.flip()

    pygame.mixer.music.stop()
    if exit_to_home:
        home_screen()
    game_over_screen(kill_count)
    main()

if __name__ == "__main__":
    main()
