"""Prompt: Make Flappy bird in python"""

import pygame
import sys
import random

# --- Game setup ---
WIDTH, HEIGHT = 400, 600
FLOOR_HEIGHT = 80

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird in Python")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# --- Bird ---
bird_rect = pygame.Rect(50, HEIGHT // 2 - 15, 34, 24)
bird_movement = 0
gravity = 0.4
jump_power = -8

# --- Pipes ---
PIPE_WIDTH = 60
PIPE_GAP = 150
PIPE_SPEED = 3
pipe_list = []

SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1300)

# --- Game state ---
game_active = True
score = 0
high_score = 0
can_score = True


def create_pipe():
    """Create a pair of top and bottom pipes."""
    center_y = random.randint(150, HEIGHT - 150)
    top_pipe = pygame.Rect(
        WIDTH,
        center_y - PIPE_GAP // 2 - HEIGHT,
        PIPE_WIDTH,
        HEIGHT
    )
    bottom_pipe = pygame.Rect(
        WIDTH,
        center_y + PIPE_GAP // 2,
        PIPE_WIDTH,
        HEIGHT - (center_y + PIPE_GAP // 2)
    )
    return top_pipe, bottom_pipe


def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, (0, 255, 0), pipe)


def check_collision(pipes):
    # Collide with pipes
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False

    # Collide with top or floor
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT - FLOOR_HEIGHT:
        return False

    return True


def update_score(pipes):
    global score, can_score, high_score

    if pipes:
        for pipe in pipes:
            # Only count bottom pipes (those touching/near the floor)
            if pipe.bottom >= HEIGHT - FLOOR_HEIGHT:
                if pipe.centerx < bird_rect.centerx and can_score:
                    score += 1
                    can_score = False
                    if score > high_score:
                        high_score = score
    else:
        can_score = True


def draw_floor():
    floor_rect = pygame.Rect(0, HEIGHT - FLOOR_HEIGHT, WIDTH, FLOOR_HEIGHT)
    pygame.draw.rect(screen, (222, 184, 135), floor_rect)


def show_text_center(text, y):
    surface = font.render(text, True, (255, 255, 255))
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)


# --- Main loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_active:
                    bird_movement = jump_power
                else:
                    # Restart game
                    game_active = True
                    pipe_list.clear()
                    bird_rect.centery = HEIGHT // 2
                    bird_movement = 0
                    score = 0
                    can_score = True

        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())

    screen.fill((135, 206, 235))  # sky blue

    if game_active:
        # Bird physics
        bird_movement += gravity
        bird_rect.centery += int(bird_movement)

        # Move pipes and reset scoring when a pair leaves
        new_pipes = []
        for pipe in pipe_list:
            pipe.x -= PIPE_SPEED
            if pipe.right > 0:
                new_pipes.append(pipe)
            else:
                # When a bottom pipe goes off screen, allow scoring again
                if pipe.bottom >= HEIGHT - FLOOR_HEIGHT:
                    can_score = True
        pipe_list = new_pipes

        # Draw objects
        draw_pipes(pipe_list)
        draw_floor()
        pygame.draw.rect(screen, (255, 255, 0), bird_rect)  # bird

        # Collisions
        game_active = check_collision(pipe_list)

        # Score
        update_score(pipe_list)
        score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_surface, (10, 10))
    else:
        # Game over screen
        draw_floor()
        pygame.draw.rect(screen, (255, 0, 0), bird_rect)  # bird as red when dead
        show_text_center("Game Over", HEIGHT // 2 - 40)
        show_text_center(f"Score: {score}", HEIGHT // 2)
        show_text_center(f"Best: {high_score}", HEIGHT // 2 + 40)
        show_text_center("Press SPACE to play again", HEIGHT // 2 + 90)

    pygame.display.update()
    clock.tick(60)
