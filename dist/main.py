import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Initialize mixer
pygame.mixer.init()

# Load background music
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Load sound effects
shoot_sound = pygame.mixer.Sound("shoot.wav")
destroy_sound = pygame.mixer.Sound("destroy.wav")

# Set up display
width, height = 600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Shooter")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# Load assets
background_image = pygame.image.load("background_image.png")
background_image = pygame.transform.scale(background_image, (width, height))

player_image = pygame.image.load("player_spaceship.png")
player_width, player_height = 50, 40
player_image = pygame.transform.scale(player_image, (player_width, player_height))

# Load asteroid images
asteroid_images = [
    pygame.image.load(f"asteroid_{i}.png") for i in range(1, 9)
]

# Scale asteroid images
asteroid_images = [pygame.transform.scale(img, (50, 40)) for img in asteroid_images]

# Player setup
player = pygame.Rect(width // 2 - player_width // 2, height - 60, player_width, player_height)
player_speed = 7

# Bullets
bullets = []
bullet_speed = 10

# Enemies
enemies = []
enemy_speed = 3
enemy_timer = 0

# Power-ups
power_ups = []
power_up_timer = 0
power_up_effect_duration = 300
player_speed_boost = False
boost_timer = 0

# Add new power-up types
shield_active = False
shield_timer = 0
shield_duration = 300

double_shot_active = False
double_shot_timer = 0
double_shot_duration = 300

# Player health
player_health = 100
max_health = 100

# Score and timer
score = 0
timer = 0

# Clock
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)

# Draw health bar
def draw_health_bar():
    bar_width = 200
    bar_height = 20
    health_ratio = player_health / max_health
    pygame.draw.rect(screen, (255, 0, 0), (10, 40, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (10, 40, bar_width * health_ratio, bar_height))

# Game loop
while True:
    clock.tick(60)  # 60 FPS

    # Draw the background
    screen.blit(background_image, (0, 0))

    # Increment timer
    timer += 1
    elapsed_time = timer // 60  # Convert frames to seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Key handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < width:
        player.x += player_speed
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= player_speed
    if keys[pygame.K_DOWN] and player.bottom < height:
        player.y += player_speed
    if keys[pygame.K_SPACE]:
        if len(bullets) < 5:
            bullet = pygame.Rect(player.centerx - 2, player.top, 5, 10)
            bullets.append(bullet)
            if double_shot_active:
                bullet2 = pygame.Rect(player.centerx - 2, player.top - 15, 5, 10)
                bullets.append(bullet2)
            shoot_sound.play()

    # Update bullets
    for bullet in bullets[:]:
        bullet.y -= bullet_speed
        if bullet.bottom < 0:
            bullets.remove(bullet)

    # Spawn enemies
    enemy_timer += 1
    if enemy_timer > 30:
        enemy = pygame.Rect(random.randint(0, width - 50), -40, 50, 40)
        enemy_type = random.choice(asteroid_images)
        enemies.append((enemy, enemy_type))
        enemy_timer = 0

    # Update enemies
    for enemy, enemy_type in enemies[:]:
        enemy.y += enemy_speed
        if enemy.top > height:
            enemies.remove((enemy, enemy_type))

    # Check for collisions
    for enemy, enemy_type in enemies[:]:
        for bullet in bullets[:]:
            if enemy.colliderect(bullet):
                enemies.remove((enemy, enemy_type))
                bullets.remove(bullet)
                score += 10
                destroy_sound.play()
                break
        if enemy.colliderect(player):
            if not shield_active:
                enemies.remove((enemy, enemy_type))
                player_health -= 20
                if player_health <= 0:
                    # Reset game state
                    player_health = max_health
                    player.x = width // 2 - player_width // 2
                    bullets.clear()
                    enemies.clear()
                    power_ups.clear()
                    player_speed_boost = False
                    player_speed = 7
                    score = 0
                    timer = 0
                    break

    # Spawn power-ups
    power_up_timer += 1
    if power_up_timer > 500:
        power_up = pygame.Rect(random.randint(0, width - 30), random.randint(0, height - 30), 30, 30)
        power_ups.append(power_up)
        power_up_timer = 0

    # Update power-up collection logic
    for power_up in power_ups[:]:
        if player.colliderect(power_up):
            power_ups.remove(power_up)
            power_up_type = random.choice(['speed', 'shield', 'double_shot'])
            if power_up_type == 'speed':
                player_speed_boost = True
                boost_timer = power_up_effect_duration
            elif power_up_type == 'shield':
                shield_active = True
                shield_timer = shield_duration
            elif power_up_type == 'double_shot':
                double_shot_active = True
                double_shot_timer = double_shot_duration

    # Apply power-up effect
    if player_speed_boost:
        player_speed = 10
        boost_timer -= 1
        if boost_timer <= 0:
            player_speed_boost = False
            player_speed = 7

    # Apply shield effect
    if shield_active:
        shield_timer -= 1
        if shield_timer <= 0:
            shield_active = False

    # Apply double-shot effect
    if double_shot_active:
        double_shot_timer -= 1
        if double_shot_timer <= 0:
            double_shot_active = False

    # Draw player
    screen.blit(player_image, (player.x, player.y))

    # Draw shield effect
    if shield_active:
        pygame.draw.circle(screen, (0, 255, 255), player.center, player_width // 2, 2)

    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, red, bullet)

    # Draw enemies
    for enemy, enemy_type in enemies:
        screen.blit(enemy_type, (enemy.x, enemy.y))

    # Draw power-ups
    for power_up in power_ups:
        pygame.draw.rect(screen, (0, 0, 255), power_up)

    # Render and display score
    score_text = font.render(f"Score: {score}", True, white)
    screen.blit(score_text, (10, 70))

    # Render and display timer
    timer_text = font.render(f"Time: {elapsed_time}s", True, white)
    screen.blit(timer_text, (10, 100))

    # Render and display kill count
    kill_count_text = font.render(f"Enemies shot: {score // 10}", True, white)
    screen.blit(kill_count_text, (10, 10))

    # Draw health bar
    draw_health_bar()

    # Update display
    pygame.display.flip()