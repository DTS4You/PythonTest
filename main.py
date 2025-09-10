import pygame

# Initialize Pygame
pygame.init()

# Set up the game window
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Hello Pygame")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            print("Spieler hat Taste gedrückt")

            # Taste für Spieler 1
            if event.key == pygame.K_UP:
                print("Pfeiltaste hoch gedrückt")
                spielfigur_1_bewegung = -6
            elif event.key == pygame.K_DOWN:
                print("Pfeiltaste runter gedrückt")
                spielfigur_1_bewegung = 6
            elif event.key == pygame.K_q:
                print("Taste Q gedrückt")
                running = False


# Quit Pygame
pygame.quit()

