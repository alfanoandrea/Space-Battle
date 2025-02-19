import pygame

# Gruppi di sprite
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
hearts = pygame.sprite.Group()
snowflakes = pygame.sprite.Group()
firepowers = pygame.sprite.Group()
shieldpowers = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Variabili globali condivise
kill_count = 0            # Numero di nemici uccisi
player = None             # Riferimento al giocatore

enemy_freeze_end_time = 0 # Tempo di fine del power-up "freeze"
freeze_duration = 5000    # Durata del power-up "freeze" (5 secondi)
next_fire_spawn = 50      # Ogni 50 kill compare il power-up "fuoco"
next_shooter_spawn = 100  # Ogni 100 kill compare il nemico speciale che spara

highscore = 0

# Variabili per i suoni (verranno inizializzate in main.py)
sparo = None
colonna_sonora = None
game_over_sound = None
menu_enter_sound = None
menu_exit_sound = None
