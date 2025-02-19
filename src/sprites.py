import pygame, random, math
from pygame.math import Vector2
from utils import load_image
from config import WIDTH, HEIGHT, NEON_GREEN, NEON_RED, NEON_BLUE, NEON_YELLOW, NEON_PURPLE, BULLET_COLORS
from globals import all_sprites, bullets, kill_count, enemy_freeze_end_time, player
from controls import Controls

# ==========================
# Classe Player (Giocatore)
# ==========================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Carica l'immagine del giocatore
        self.original_image = load_image("assets/images/player.png", scale=(50, 50))
        if self.original_image is None:
            self.original_image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, NEON_GREEN, [(20, 0), (0, 40), (40, 40)])
        self.image = self.original_image.copy() # Copia dell'immagine originale
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2)) # Posizione iniziale
        self.pos = Vector2(self.rect.center) # Posizione come vettore
        self.speed = 5 # Velocità di movimento
        self.lives = 3 # Vite iniziali
        self.shoot_delay = 250  # Spara ogni 0.25 sec
        self.last_shot = pygame.time.get_ticks() 
        self.fire_level = 1 # Livello di fuoco iniziale
        self.bullet_speed = 10 # Velocità dei proiettili
        self.mask = pygame.mask.from_surface(self.image)
        self.invincible_end_time = 0 # Tempo di fine invincibilità
        self.hit_anim_end_time = 0 # Tempo di fine animazione "hit"
        self.shield_end_time = 0 # Tempo di fine dello scudo

        # Inizializza il gestore dei controlli
        self.controls = Controls()

    def update(self):
        current_time = pygame.time.get_ticks()

        # Movimento: ottiene dx e dy dal modulo dei controlli
        dx, dy = self.controls.get_movement()
        if dx != 0 or dy != 0:
            velocity = Vector2(dx, dy)
            if velocity.length() > 0:
                velocity = velocity.normalize() * self.speed
            self.pos += velocity
            self.pos.x = max(0, min(WIDTH, self.pos.x))
            self.pos.y = max(0, min(HEIGHT, self.pos.y))
            self.rect.center = self.pos

        # Rotazione: se disponibile l'analogico su Raspberry, altrimenti usa il mouse
        rotation_angle = self.controls.get_rotation()
        if rotation_angle is None:
            mouse_pos = Vector2(pygame.mouse.get_pos())
            direction = mouse_pos - self.pos
            angle = math.degrees(math.atan2(direction.y, direction.x)) - 90
        else:
            angle = rotation_angle

        # Animazione "hit"
        if current_time < self.hit_anim_end_time:
            base_image = self.original_image.copy()
            if (current_time // 100) % 2 == 0:
                base_image.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
        else:
            base_image = self.original_image.copy()

        self.image = pygame.transform.rotate(base_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        # Se siamo su Raspberry e si preme il bottone di sparo, esegue shoot()
        if self.controls.is_raspberry and self.controls.is_shooting():
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            from globals import sparo
            sparo.play()
            # Su Windows usa il mouse per determinare la direzione, su Raspberry usa il valore analogico
            if not self.controls.is_raspberry:
                mouse_pos = Vector2(pygame.mouse.get_pos())
                direction = mouse_pos - self.pos
                base_angle = math.degrees(math.atan2(direction.y, direction.x))
            else:
                base_angle = self.controls.get_rotation() or 0

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
                from globals import all_sprites, bullets
                all_sprites.add(bullet)
                bullets.add(bullet)

# ==========================
# Classe Bullet (Proiettile)
# ==========================
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

# =====================
# Classe Enemy (Nemico)
# =====================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, is_boss=False):
        super().__init__()
        self.is_boss = is_boss
        if not self.is_boss:
            self.image = load_image("assets/images/enemy.png", scale=(30, 30))
            if self.image is None:
                self.size = random.randint(20, 30)
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, NEON_RED, (self.size // 2, self.size // 2), self.size // 2)
            else:
                self.size = self.image.get_width()
            base_health = 1
            from globals import kill_count, player
            health_increase = kill_count // 50
            fire_bonus = (player.fire_level - 1) if player is not None else 0
            self.health = base_health + health_increase + fire_bonus
            base_speed = 1
            speed_increase = kill_count / 500.0
            fire_speed_bonus = (player.fire_level - 1) * 0.2 if player is not None else 0
            raw_speed = base_speed + speed_increase + fire_speed_bonus
            self.speed = min(raw_speed, 5 * 0.9)
        else:
            self.image = load_image("assets/images/boss.png", scale=(60, 60))
            if self.image is None:
                self.size = 60
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, NEON_PURPLE, (self.size // 2, self.size // 2), self.size // 2)
            else:
                self.size = self.image.get_width()
            base_health = 5
            from globals import kill_count, player
            health_increase = kill_count // 50
            fire_bonus = (player.fire_level - 1) * 2 if player is not None else 0
            self.health = base_health + health_increase + fire_bonus
            base_speed = 0.5
            speed_increase = kill_count / 800.0
            fire_speed_bonus = (player.fire_level - 1) * 0.1 if player is not None else 0
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
            from config import WIDTH, HEIGHT
            self.rect.centerx = random.randint(0, WIDTH)
            self.rect.y = -self.size
        elif side == "bottom":
            from config import WIDTH, HEIGHT
            self.rect.centerx = random.randint(0, WIDTH)
            self.rect.y = HEIGHT + self.size
        elif side == "left":
            from config import HEIGHT
            self.rect.x = -self.size
            self.rect.centery = random.randint(0, HEIGHT)
        elif side == "right":
            from config import WIDTH, HEIGHT
            self.rect.x = WIDTH + self.size
            self.rect.centery = random.randint(0, HEIGHT)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        from globals import enemy_freeze_end_time, player
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

# ======================================
# Classe ShooterEnemy (Nemico che spara)
# ======================================
class ShooterEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("assets/images/shooter.gif", scale=(80, 80))
        if self.image is None:
            self.size = 80
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(self.image, NEON_PURPLE, (0, 0, self.size, self.size))
        else:
            self.size = self.image.get_width()
        self.rect = self.image.get_rect()
        from config import WIDTH, HEIGHT
        self.pos = Vector2(random.randint(self.size, WIDTH - self.size), random.randint(self.size, HEIGHT - self.size))
        base_health = 20
        from globals import kill_count, player
        health_increase = kill_count // 50
        fire_bonus = (player.fire_level - 1) * 2 if player is not None else 0
        self.health = base_health + health_increase + fire_bonus
        self.max_health = self.health
        base_speed = 2
        speed_increase = kill_count / 800.0
        fire_speed_bonus = (player.fire_level - 1) * 0.2 if player is not None else 0
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
        from config import WIDTH, HEIGHT
        if self.pos.x < self.size / 2 or self.pos.x > WIDTH - self.size / 2:
            self.direction.x *= -1
        if self.pos.y < self.size / 2 or self.pos.y > HEIGHT - self.size / 2:
            self.direction.y *= -1
        self.rect.center = self.pos
        if current_time - self.last_shot >= self.shoot_delay:
            self.last_shot = current_time
            from globals import all_sprites, enemy_bullets, player
            bullet = EnemyBullet(self.pos, player.pos)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

# ==========================================
# Classe EnemyBullet (Proiettile del nemico)
# ==========================================
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
        from config import WIDTH, HEIGHT
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()

# ===============================
# Classe Heart (Cuore - Power-up)
# ===============================
class Heart(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("assets/images/heart.png", scale=(20, 20))
        if self.image is None:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, NEON_RED, [(10, 0), (20, 7), (16, 18), (4, 18), (0, 7)])
        self.rect = self.image.get_rect()
        from config import WIDTH, HEIGHT
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)

# ============================================
# Classe Snowflake (Fiocco di neve - Power-up)
# ============================================
class Snowflake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("assets/images/snowflake.png", scale=(30, 30))
        if self.image is None:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            for angle in range(0, 360, 45):
                x = 15 + 10 * math.cos(math.radians(angle))
                y = 15 + 10 * math.sin(math.radians(angle))
                pygame.draw.line(self.image, NEON_BLUE, (15, 15), (x, y), 2)
        self.rect = self.image.get_rect()
        from config import WIDTH, HEIGHT
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        pass

# ==============================================
# Classe FirePower (Potere del fuoco - Power-up)
# ==============================================
class FirePower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("assets/images/fire.png", scale=(30, 30))
        if self.image is None:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 165, 0), [(15, 0), (5, 25), (15, 20), (25, 25)])
        self.rect = self.image.get_rect()
        from config import WIDTH, HEIGHT
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        pass

# =====================================
# Classe ShieldPower (Scudo - Power-up)
# =====================================
class ShieldPower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("assets/images/shield.png", scale=(30, 30))
        if self.image is None:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)
        self.rect = self.image.get_rect()
        from config import WIDTH, HEIGHT
        self.rect.center = (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        pass