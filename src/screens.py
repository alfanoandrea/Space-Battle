# screens.py
import pygame, sys, random, math, globals
from config import WIDTH, HEIGHT, BLACK, WHITE, NEON_GREEN, NEON_BLUE, NEON_RED
from sprites import Player
from utils import save_highscore

# Funzione per caricare il font personalizzato
def load_custom_font(size):
    try:
        return pygame.font.Font("fonts/space_age.ttf", size)
    except:
        return pygame.font.SysFont("Arial", size, bold=True)

# ==================================
# Funzione per la schermata iniziale
# ==================================
def home_screen():
    # Genera stelle casuali per l'animazione di sfondo
    stars = [{'pos': [random.randint(0, WIDTH), random.randint(0, HEIGHT)], 'speed': random.randint(1, 3)} for _ in range(100)]
    ship_angle = 0
    globals.colonna_sonora.play(-1)  # Riproduce la colonna sonora in loop
    
    while True:
        screen = pygame.display.get_surface()
        screen.fill(BLACK)
        
        # Anima le stelle
        for star in stars:
            star['pos'][1] += star['speed']
            if star['pos'][1] > HEIGHT:
                star['pos'] = [random.randint(0, WIDTH), 0]
            pygame.draw.circle(screen, WHITE, star['pos'], 1)
        
        # Disegna il titolo del gioco
        title_font = load_custom_font(72)
        title_text = title_font.render("SPACE BATTLE", True, NEON_GREEN)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        
        # Disegna i nomi degli autori
        authors_font = load_custom_font(18)
        authors_text = authors_font.render("by Andrea Alfano & Gabriele Merelli", True, NEON_BLUE)
        screen.blit(authors_text, (WIDTH // 2 - authors_text.get_width() // 2, HEIGHT // 3 + 50))
        
        # Anima la navicella rotante
        ship_img = Player().original_image
        ship_angle = (ship_angle + 2) % 360
        rotated_ship = pygame.transform.rotate(ship_img, ship_angle)
        screen.blit(rotated_ship, (WIDTH // 2 - rotated_ship.get_width() // 2, HEIGHT // 2))
        
        # Disegna il testo lampeggiante per iniziare
        font = load_custom_font(24)
        text = font.render("Premi un tasto per iniziare", True, WHITE)
        if pygame.time.get_ticks() % 1000 < 500:
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))
        
        pygame.display.flip()
        
        # Gestione degli eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                globals.colonna_sonora.stop()
                return

# ======================================
# Funzione per la schermata di game over
# ======================================
def game_over_screen(final_score):
    # Aggiorna il record se il punteggio finale è superiore
    if final_score > globals.highscore:
        globals.highscore = final_score
        save_highscore(globals.highscore)
    
    # Genera stelle casuali per l'animazione di sfondo
    stars = [{'pos': [random.randint(0, WIDTH), random.randint(0, HEIGHT)], 'speed': random.randint(1, 3)} for _ in range(100)]
    globals.game_over_sound.play(-1)  # Riproduce il suono di game over in loop
    
    while True:
        screen = pygame.display.get_surface()
        screen.fill(BLACK)
        
        # Anima le stelle
        for star in stars:
            star['pos'][1] += star['speed']
            if star['pos'][1] > HEIGHT:
                star['pos'] = [random.randint(0, WIDTH), 0]
            pygame.draw.circle(screen, WHITE, star['pos'], 1)
        
        # Disegna il titolo "GAME OVER"
        title_font = load_custom_font(60)
        title_text = title_font.render("GAME OVER", True, NEON_RED)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        
        # Disegna il punteggio finale e il record
        info_font = load_custom_font(24)
        info_text = info_font.render(f"Punteggio: {final_score}    Record: {globals.highscore}", True, WHITE)
        screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 50)))
        
        # Disegna il testo per riprovare
        sub_text = info_font.render("Premi un tasto per riprovare", True, WHITE)
        screen.blit(sub_text, sub_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
        
        pygame.display.flip()
        
        # Gestione degli eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                globals.game_over_sound.stop()
                return

# ==================================
# Funzione per la schermata di pausa
# ==================================
def pause_game():
    paused = True
    return_to_home = False
    
    # Carica i font personalizzati, se disponibili
    title_font = load_custom_font(72)
    button_font = load_custom_font(32)
    
    # Crea un overlay trasparente per la pausa
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    
    # Testo del titolo "PAUSA"
    title_text = title_font.render("PAUSA", True, NEON_BLUE)
    title_glow = title_font.render("PAUSA", True, (100, 100, 255))
    
    # Rettangoli per i pulsanti del menu
    menu_rect = pygame.Rect(0, 0, 400, 400)
    menu_rect.center = (WIDTH // 2, HEIGHT // 2)
    
    resume_button = pygame.Rect(0, 0, 300, 60)
    resume_button.center = (WIDTH // 2, HEIGHT // 2 - 30)
    home_button = pygame.Rect(0, 0, 300, 60)
    home_button.center = (WIDTH // 2, HEIGHT // 2 + 60)
    
    angle = 0
    globals.menu_enter_sound.play()
    clock = pygame.time.Clock()
    
    while paused:
        mouse_pos = pygame.mouse.get_pos()
        angle += 2
        current_time = pygame.time.get_ticks()
        screen = pygame.display.get_surface()
        
        screen.blit(overlay, (0, 0))
        
        # Disegna il bordo animato del menu
        border_surface = pygame.Surface((menu_rect.w + 10, menu_rect.h + 10), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, NEON_BLUE, (0, 0, border_surface.get_width(), border_surface.get_height()), border_radius=20)
        rotated_border = pygame.transform.rotate(border_surface, math.sin(angle * 0.02) * 3)
        screen.blit(rotated_border, rotated_border.get_rect(center=menu_rect.center))
        
        pygame.draw.rect(screen, (0, 0, 30), menu_rect, border_radius=20)
        pygame.draw.rect(screen, NEON_BLUE, menu_rect, 3, border_radius=20)
        
        # Disegna il testo del titolo con effetto glow
        for i in range(5):
            offset = math.sin(angle * 0.02 + i) * 3
            screen.blit(title_glow, (WIDTH // 2 - title_glow.get_width() // 2 + offset, HEIGHT // 3 - 50 + offset))
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        
        # Disegna il pulsante "RIPRENDI"
        resume_color = NEON_GREEN if resume_button.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(screen, resume_color, resume_button, border_radius=15)
        pygame.draw.rect(screen, NEON_GREEN, resume_button, 3, border_radius=15)
        resume_label = button_font.render("RIPRENDI", True, WHITE)
        screen.blit(resume_label, resume_label.get_rect(center=resume_button.center))
        
        # Disegna il pulsante "TORNA ALLA HOME"
        home_color = NEON_RED if home_button.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(screen, home_color, home_button, border_radius=15)
        pygame.draw.rect(screen, NEON_RED, home_button, 3, border_radius=15)
        home_label = button_font.render("TORNA ALLA HOME", True, WHITE)
        screen.blit(home_label, home_label.get_rect(center=home_button.center))
        
        # Disegna il testo informativo
        info_font = load_custom_font(18)
        info_text = info_font.render("Usa il mouse per selezionare le opzioni", True, WHITE)
        screen.blit(info_text, info_text.get_rect(center=(WIDTH // 2, HEIGHT - 50)))
        
        pygame.display.flip()
        
        # Gestione degli eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    globals.menu_exit_sound.play()
                    paused = False
                if event.key == pygame.K_h:
                    globals.menu_exit_sound.play()
                    paused = False
                    return_to_home = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if resume_button.collidepoint(event.pos):
                        globals.menu_exit_sound.play()
                        paused = False
                    if home_button.collidepoint(event.pos):
                        globals.menu_exit_sound.play()
                        paused = False
                        return_to_home = True
        clock.tick(60)
    
    return return_to_home