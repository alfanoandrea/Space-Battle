import sys
import pygame

# Determina se il sistema è Windows oppure Linux (assumiamo che se non è Windows allora sia Raspberry Pi)
IS_RASPBERRY = False if sys.platform.startswith("win") else True

class Controls:
    def __init__(self):
        self.is_raspberry = IS_RASPBERRY
        if self.is_raspberry:
            try:
                import RPi.GPIO as GPIO 
                self.GPIO = GPIO
                # Configurazione dei pin per i bottoni (modifica i valori in base al tuo setup)
                self.UP_PIN = 17      # Pin per il movimento in alto
                self.DOWN_PIN = 18    # Pin per il movimento in basso
                self.LEFT_PIN = 27    # Pin per il movimento a sinistra
                self.RIGHT_PIN = 22   # Pin per il movimento a destra
                self.SHOOT_PIN = 23   # Bottone per sparare
                GPIO.setmode(GPIO.BCM) 
                GPIO.setup(self.UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
                GPIO.setup(self.DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(self.LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(self.RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.setup(self.SHOOT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            except ImportError:
                print("RPi.GPIO non disponibile. I controlli per Raspberry Pi non funzioneranno correttamente.")
                self.is_raspberry = False
            # Inizializza l'interfaccia SPI per leggere il segnale analogico da un MCP3008
            try: # non originale, preso da GitHub
                import spidev
                self.spidev = spidev.SpiDev()
                self.spidev.open(0, 0)  # Bus 0, device 0
                self.spidev.max_speed_hz = 1350000
                self.ANALOG_CHANNEL = 0  # Canale dell'ADC per il controllo dell'angolo
            except ImportError:
                print("spidev non disponibile. Il controllo analogico non funzionerà.")
                self.spidev = None

    def get_movement(self):
        """
        Ritorna una tupla (dx, dy) per il movimento:
         - Su Windows: usa i tasti W, A, S, D.
         - Su Raspberry Pi: legge lo stato dei bottoni collegati ai pin GPIO.
        """
        if not self.is_raspberry:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_s]:
                dy += 1
            if keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_d]:
                dx += 1
            return dx, dy
        else:
            dx, dy = 0, 0
            if not self.GPIO.input(self.UP_PIN):
                dy -= 1
            if not self.GPIO.input(self.DOWN_PIN):
                dy += 1
            if not self.GPIO.input(self.LEFT_PIN):
                dx -= 1
            if not self.GPIO.input(self.RIGHT_PIN):
                dx += 1
            return dx, dy

    def read_adc(self, channel): # non originale, preso da GitHub
        """
        Legge il valore analogico dal canale specificato dell'MCP3008.
        Ritorna un valore tra 0 e 1023.
        """
        if self.spidev is None:
            return 0
        if channel < 0 or channel > 7:
            return -1
        # Protocollo MCP3008: invia [start, (8+channel)<<4, 0]
        adc = self.spidev.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def get_rotation(self): # non originale, preso da GitHub
        """
        Ritorna l'angolo di rotazione in gradi:
         - Su Windows: restituisce None (la rotazione verrà calcolata tramite il mouse).
         - Su Raspberry Pi: legge il valore analogico e lo mappa in gradi (0-360).
        """
        if not self.is_raspberry:
            return None
        else:
            raw_value = self.read_adc(self.ANALOG_CHANNEL)  # Valore 0-1023
            angle = (raw_value / 1023.0) * 360  # Mappa linearmente a 0-360°
            return angle

    def is_shooting(self):
        """
        Ritorna True se si sta sparando:
         - Su Windows: lo sparo è gestito tramite il click del mouse.
         - Su Raspberry Pi: legge lo stato del bottone (con pull-up, premuto → False).
        """
        if not self.is_raspberry:
            return False
        else:
            return not self.GPIO.input(self.SHOOT_PIN)
