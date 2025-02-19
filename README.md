# Space Battle

**Space Battle** è un gioco di combattimento spaziale sviluppato con Python e Pygame. Il giocatore pilota una navicella spaziale, affrontando ondate di nemici e raccogliendo power-up per potenziare le proprie abilità. Il gioco è stato progettato con un'architettura modulare che permette di gestire in maniera separata grafica, suoni, controlli (con supporto nativo per Windows e per dispositivi Raspberry Pi) e logica di gioco.

---

## Indice

- [Caratteristiche del Gioco](#caratteristiche-del-gioco)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Struttura del Progetto](#struttura-del-progetto)
- [Dettagli Tecnici](#dettagli-tecnici)
  - [Architettura e Moduli](#architettura-e-moduli)
  - [Gestione degli Eventi](#gestione-degli-eventi)
  - [Controlli e Integrazione Hardware](#controlli-e-integrazione-hardware)
  - [Gestione degli Asset](#gestione-degli-asset)
- [Utilizzo](#utilizzo)
- [Credits](#credits)

---

## Caratteristiche del Gioco

- **Grafica Accattivante**: Sfondo animato con stelle e una navicella che ruota dinamicamente.
- **Suoni Coinvolgenti**: Colonna sonora di sottofondo ed effetti sonori per azioni chiave (sparo, game over, menu, ecc.).
- **Power-Up**: Vari power-up (cuori, fiocchi di neve, poteri del fuoco e scudi) che modificano le abilità del giocatore.
- **Nemici Vari**: Nemici standard e boss, con dinamiche di salute, velocità e pattern di movimento differenziati.
- **Schermate Interattive**: Schermata iniziale, schermata di pausa e schermata di game over con animazioni e transizioni fluide.
- **Controlli Multipiattaforma**: Supporto per tastiera/mouse su Windows e per input hardware (bottoni e segnale analogico) su Raspberry Pi.

---

## Requisiti

- **Linguaggio**: Python 3.x
- **Librerie**:
  - [Pygame](https://www.pygame.org/) – per grafica, eventi e gestione audio.
  - *(Opzionale su Raspberry Pi)* [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) – per la gestione degli input hardware.
  - *(Opzionale su Raspberry Pi)* [spidev](https://pypi.org/project/spidev/) – per la lettura del segnale analogico da un ADC (es. MCP3008).
- **Sistema Operativo**: Windows per la modalità standard, Linux (Raspberry Pi) per la modalità hardware.

---

## Installazione

1. **Clona il repository**:
    ```sh
    git clone https://github.com/alfanoandrea/Space-Battle.git
    cd Space-Battle
    ```

2. **Installa le dipendenze**:
    ```sh
    pip install pygame
    ```
    Se utilizzi un Raspberry Pi e intendi usare i controlli hardware:
    ```sh
    pip install RPi.GPIO spidev
    ```

3. **Verifica la struttura delle cartelle**:  
   Assicurati che le immagini, i suoni e i font siano posizionati correttamente nelle cartelle `assets/` e `fonts/`.

---

## Struttura del Progetto

```plaintext
Space-Battle/
├── assets/
│   ├── images/
│   │   ├── bg.png
│   │   ├── boss.png
│   │   ├── enemy.png
│   │   ├── fire.png
│   │   ├── heart.png
│   │   ├── player.png
│   │   ├── shield.png
│   │   └── snowflake.png
│   └── sounds/
│       ├── background.mp3
│       ├── colonna_sonora.mp3
│       ├── game_over.mp3
│       ├── menu_enter.mp3
│       ├── menu_exit.mp3
│       └── shot.mp3
├── fonts/
│   └── space_age.ttf
├── src/
│   ├── main.py
│   ├── sprites.py
│   ├── screens.py
│   ├── utils.py
│   ├── globals.py
│   ├── controls.py
│   └── config.py
├── highscore.txt 
└── README.md
```

---

## Dettagli Tecnici

### Architettura e Moduli

Il progetto è strutturato in moduli distinti, ognuno dei quali si occupa di un aspetto specifico del gioco:

- **config.py**: Definisce costanti globali (dimensioni della finestra, colori, FPS).
- **utils.py**: Funzioni di utilità (ad esempio, caricamento immagini e gestione del record).
- **globals.py** *(se implementato)*: Contiene variabili globali condivise (gruppi di sprite, variabili di stato).
- **sprites.py**: Definisce le classi per il giocatore, i nemici, i proiettili e i power-up, gestendo anche collisioni, animazioni e logica di movimento.
- **screens.py**: Gestisce le schermate di gioco (home, pause, game over) con animazioni e interazioni.
- **controls.py**: Implementa una classe astratta per la gestione degli input, supportando sia l'input standard (tastiera/mouse) che l'input hardware su Raspberry Pi.
- **main.py**: Punto d'ingresso del gioco, dove viene gestito il loop principale, l'aggiornamento degli sprite e la logica complessiva.

### Gestione degli Eventi

- **Eventi Pygame**: Il gioco sfrutta il sistema di eventi di Pygame per gestire input da tastiera e mouse, oltre a timer personalizzati per lo spawn di nemici e power-up.
- **Loop di Gioco**: Ad ogni iterazione, il loop aggiorna lo stato degli sprite, controlla collisioni, gestisce l'input e ridisegna la scena.

### Controlli e Integrazione Hardware

- **Modalità Windows**: I controlli sono gestiti tramite tastiera (W, A, S, D) per il movimento e il mouse per la direzione e lo sparo.
- **Modalità Raspberry Pi**:  
  - I movimenti vengono rilevati tramite bottoni collegati ai pin GPIO.  
  - La direzione viene determinata da un segnale analogico letto da un ADC (es. MCP3008) tramite la libreria spidev, mappato su una scala 0–360 gradi.  
  - Lo sparo può essere attivato da un bottone dedicato (ad es. integrato nell'analogico).

Il modulo **controls.py** implementa metodi quali `get_movement()`, `get_rotation()`, e `is_shooting()` per astrarre i dettagli hardware, permettendo alla logica di gioco di rimanere indipendente dal dispositivo in uso.

### Gestione degli Asset

- **Immagini e Suoni**: Tutti gli asset grafici e audio sono organizzati nelle cartelle `assets/images` e `assets/sounds`. Le immagini vengono caricate dinamicamente con supporto al ridimensionamento, mentre i suoni vengono inizializzati all'avvio del gioco.
- **Font**: Il font personalizzato `space_age.ttf` viene utilizzato per le schermate di pausa e per la grafica testuale, garantendo uno stile coerente con il tema spaziale.

---

## Utilizzo

1. **Avvio del Gioco**:  
   Esegui il comando seguente dalla cartella principale:
   ```sh
   python src/main.py
   ```

2. **Schermata Iniziale**:  
   Premi un tasto qualsiasi per avviare il gioco.

3. **Controlli di Gioco**:
   - **Movimento**:  
     - Windows: `W`, `A`, `S`, `D`  
     - Raspberry Pi: Bottoni collegati ai pin GPIO.
   - **Sparo**:  
     - Windows: Clic sinistro del mouse.  
     - Raspberry Pi: Bottone dedicato (o click analogico).
   - **Rotazione**:  
     - Windows: Basata sulla posizione del mouse.  
     - Raspberry Pi: Lettura del segnale analogico mappato in gradi.
   - **Pausa**: Premi `P` per mettere in pausa e accedere al menu di pausa.

---

## Credits

- **Sviluppo**: Andrea Alfano & Gabriele Merelli
- **Libreria Principale**: [Pygame](https://www.pygame.org/)
- **Asset Grafici e Audio**: Immagini AI, Fonts Google, Suoni creati con FL-Studio da Andrea Alfano.
- **Ispirazione**: Il design e la dinamica di gioco sono ispirati ai classici arcade di sparatutto spaziali.
- **Programmazione**: Il codice non originale o generato è evidenziato attraverso i commenti
- **Formattazione**: Il codice usa la formattazione tipica del Code Formatter di VSCode

---