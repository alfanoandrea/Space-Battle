import pygame, random, globals
from config import WIDTH, HEIGHT, FPS, NEON_YELLOW
from utils import load_highscore
from sprites import *
from screens import *

# Inizializzazione di Pygame e del mixer audio
pygame.init()
pygame.mixer.init()

# Caricamento suoni – assegnali al modulo globals
globals.sparo = pygame.mixer.Sound("assets/sounds/shot.mp3")
globals.colonna_sonora = pygame.mixer.Sound("assets/sounds/colonna_sonora.mp3")
globals.game_over_sound = pygame.mixer.Sound("assets/sounds/game_over.mp3")
globals.menu_enter_sound = pygame.mixer.Sound("assets/sounds/menu_enter.mp3")
globals.menu_exit_sound = pygame.mixer.Sound("assets/sounds/menu_exit.mp3")

# Impostazione della finestra di gioco
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Battle")
clock = pygame.time.Clock()

# Caricamento e ridimensionamento dell'immagine di sfondo
background_image = pygame.image.load("assets/images/bg.png").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Impostazione dei timer per lo spawn degli oggetti
pygame.time.set_timer(pygame.USEREVENT+1, 1500)  # Nemici ogni 1.5 sec
pygame.time.set_timer(pygame.USEREVENT+2, 10000) # Cuori ogni 10 sec
pygame.time.set_timer(pygame.USEREVENT+3, 20000) # Congelamento (snowflake) ogni 20 sec
pygame.time.set_timer(pygame.USEREVENT+5, 40000) # Scudi ogni 40 sec

# Inizializzazione delle variabili globali
globals.kill_count = 0
globals.enemy_freeze_end_time = 0
globals.freeze_duration = 5000
globals.next_fire_spawn = 50
globals.next_shooter_spawn = 100
globals.highscore = load_highscore()

def main():
    # Inizializzazione del giocatore e delle schermate
    globals.player = None
    home_screen()
    pygame.mixer.music.load("assets/sounds/background.mp3")
    pygame.mixer.music.play(-1)
    globals.kill_count = 0
    globals.next_fire_spawn = 50
    globals.next_shooter_spawn = 100

    # Reset dei gruppi di sprite
    globals.all_sprites.empty() 
    globals.bullets.empty()
    globals.enemies.empty()
    globals.hearts.empty()
    globals.snowflakes.empty()
    globals.firepowers.empty()
    globals.shieldpowers.empty()
    globals.enemy_bullets.empty()

    # Creazione del giocatore e aggiunta al gruppo di sprite
    globals.player = Player()
    globals.all_sprites.add(globals.player)

    exit_to_home = False
    running = True
    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        # Gestione degli eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if pause_game():
                        exit_to_home = True
                        running = False
            # Su Windows lo sparo va tramite il click del mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not globals.player.controls.is_raspberry and event.button == 1:
                    globals.player.shoot()
            if event.type == pygame.USEREVENT+1:
                if random.random() < 0.1:
                    enemy = Enemy(is_boss=True)
                else:
                    enemy = Enemy(is_boss=False)
                globals.all_sprites.add(enemy)
                globals.enemies.add(enemy)
            elif event.type == pygame.USEREVENT+2:
                if globals.player.lives < 3:
                    heart = Heart()
                    globals.all_sprites.add(heart)
                    globals.hearts.add(heart)
            elif event.type == pygame.USEREVENT+3:
                snowflake = Snowflake()
                globals.all_sprites.add(snowflake)
                globals.snowflakes.add(snowflake)
            elif event.type == pygame.USEREVENT+5:
                shield = ShieldPower()
                globals.all_sprites.add(shield)
                globals.shieldpowers.add(shield)

        # Aggiornamento degli sprite
        globals.all_sprites.update()

        # Gestione delle collisioni (tempo perso ad imprecare: 27 ore)
        hits = pygame.sprite.groupcollide(globals.enemies, globals.bullets, False, True, collided=pygame.sprite.collide_mask)
        for enemy, hit_list in hits.items():
            for bullet in hit_list:
                enemy.health -= bullet.damage
                if enemy.health <= 0:
                    enemy.kill()
                    globals.kill_count += 1

        enemy_bullet_hits = pygame.sprite.spritecollide(globals.player, globals.enemy_bullets, True, collided=pygame.sprite.collide_mask)
        if enemy_bullet_hits and current_time >= globals.player.invincible_end_time:
            globals.player.lives -= sum(b.damage for b in enemy_bullet_hits)
            if globals.player.lives <= 0:
                running = False
            else:
                globals.player.invincible_end_time = current_time + 2000
                globals.player.hit_anim_end_time = current_time + 2000

        enemy_hits = pygame.sprite.spritecollide(globals.player, globals.enemies, False, collided=pygame.sprite.collide_mask)
        if enemy_hits and current_time >= globals.player.invincible_end_time:
            globals.player.lives -= 1
            if globals.player.lives <= 0:
                running = False
            else:
                globals.player.invincible_end_time = current_time + 2000
                globals.player.hit_anim_end_time = current_time + 2000

        # Gestione dei power-up
        for heart in pygame.sprite.spritecollide(globals.player, globals.hearts, True):
            if globals.player.lives < 3:
                globals.player.lives += 1
        for snow in pygame.sprite.spritecollide(globals.player, globals.snowflakes, True):
            globals.enemy_freeze_end_time = current_time + globals.freeze_duration
        for fire in pygame.sprite.spritecollide(globals.player, globals.firepowers, True):
            if globals.player.fire_level < 5:
                globals.player.fire_level += 1
                globals.player.bullet_speed = 10 + (globals.player.fire_level - 1) * 2
            else:
                globals.player.bullet_speed += 1
        for shield in pygame.sprite.spritecollide(globals.player, globals.shieldpowers, True):
            globals.player.shield_end_time = current_time + 3000
            globals.player.invincible_end_time = max(globals.player.invincible_end_time, current_time + 3000)

        # Spawn dei power-up e nemici speciali basato sui kill
        if globals.kill_count >= globals.next_fire_spawn:
            fire = FirePower()
            globals.all_sprites.add(fire)
            globals.firepowers.add(fire)
            globals.next_fire_spawn += 50

        if globals.kill_count >= globals.next_shooter_spawn:
            shooter = ShooterEnemy()
            globals.all_sprites.add(shooter)
            globals.enemies.add(shooter)
            globals.next_shooter_spawn += 100

        # Disegno degli elementi sullo schermo
        screen.blit(background_image, (0, 0))
        globals.all_sprites.draw(screen)
        for enemy in globals.enemies:
            bar_width = enemy.rect.width
            bar_height = 5
            health_ratio = enemy.health / enemy.max_health if enemy.max_health > 0 else 0
            bar_x = enemy.rect.x
            bar_y = enemy.rect.y - bar_height - 2
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            fill_color = (0, 191, 255) if current_time < globals.enemy_freeze_end_time else (0, 255, 0)
            pygame.draw.rect(screen, fill_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))
        info_font = pygame.font.SysFont("Arial", 24)
        score_text = info_font.render(f"Kill: {globals.kill_count}", True, (255, 255, 255))
        lives_text = info_font.render(f"Vite: {globals.player.lives}", True, (255, 255, 255))
        record_text = info_font.render(f"Record: {globals.highscore}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(record_text, (10, 70))
        if current_time < globals.player.shield_end_time:
            aura_radius = int(max(globals.player.rect.width, globals.player.rect.height) * 0.75 + 15)
            pygame.draw.circle(screen, NEON_YELLOW, globals.player.rect.center, aura_radius, 3)
        pygame.display.flip()

    # Fine del gioco (finalmente)
    pygame.mixer.music.stop()
    if exit_to_home:
        home_screen()
    game_over_screen(globals.kill_count)
    main()

if __name__ == "__main__":
    main()