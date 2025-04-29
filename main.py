import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Initialize mixer
pygame.mixer.init()

# Load background music
pygame.mixer.music.load("assets/music/background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Load sound effects
shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")
destroy_sound = pygame.mixer.Sound("assets/sounds/destroy.wav")
damage_sound = pygame.mixer.Sound("assets/music/damage-sound.mp3")

# Set up display
width, height = 600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Shooter")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# Load assets
background_image = pygame.image.load("assets/images/background_image.png")
background_image = pygame.transform.scale(background_image, (width, height))

player_image = pygame.image.load("assets/images/player_spaceship.png")
player_width, player_height = 50, 40
player_image = pygame.transform.scale(player_image, (player_width, player_height))

# Load asteroid images
asteroid_images = [
    pygame.image.load(f"assets/images/asteroid_{i}.png") for i in range(1, 9)
]

# Scale asteroid images
asteroid_images = [pygame.transform.scale(img, (50, 40)) for img in asteroid_images]

# Load explosion image
explosion_image = pygame.image.load("assets/images/explostion_asteroid.png")
explosion_image = pygame.transform.scale(explosion_image, (50, 50))

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

# Update power-up colors
power_up_colors = {
    'speed': (0, 255, 0),  # Green for speed
    'shield': (0, 255, 255),  # Cyan for shield
    'double_shot': (255, 255, 0)  # Yellow for double shot
}

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

# Define a custom class for explosions
class Explosion:
    def __init__(self, x, y, timer):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.timer = timer

# Update explosions list to use the Explosion class
explosions = []

# Draw health bar
def draw_health_bar():
    bar_width = 200
    bar_height = 20
    health_ratio = player_health / max_health
    pygame.draw.rect(screen, (255, 0, 0), (10, 40, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (10, 40, bar_width * health_ratio, bar_height))

# Shake effect function
def shake_screen():
    for _ in range(3):
        screen.blit(background_image, (random.randint(-3, 3), random.randint(-3, 3)))
        pygame.display.flip()
        pygame.time.delay(10)

# Reset game state function
def reset_game():
    global player_health, player_speed, score, timer, bullets, enemies, power_ups, player_speed_boost
    player_health = max_health
    player.x = width // 2 - player_width // 2
    bullets.clear()
    enemies.clear()
    power_ups.clear()
    player_speed_boost = False
    player_speed = 7
    score = 0
    timer = 0

# Leaderboard setup
high_scores = [0, 0, 0]  # Top 3 high scores

def update_leaderboard(new_score):
    high_scores.append(new_score)
    high_scores.sort(reverse=True)
    del high_scores[3:]

# Adjust leaderboard font size and position
leaderboard_font = pygame.font.Font(None, 24)  # Smaller font size

def draw_leaderboard():
    leaderboard_text = leaderboard_font.render("Leaderboard:", True, white)
    screen.blit(leaderboard_text, (width - 110, 60))  # Position under the pause button
    for i, score in enumerate(high_scores):
        score_text = leaderboard_font.render(f"{i + 1}. {score}", True, white)
        screen.blit(score_text, (width - 110, 90 + i * 20))

# Add a pause button in the top-right corner
pause_button = pygame.Rect(width - 110, 10, 100, 40)
paused = False

def draw_pause_button():
    pygame.draw.rect(screen, (255, 255, 0), pause_button)
    pause_text = font.render("Pause", True, black)
    screen.blit(pause_text, (pause_button.x + 10, pause_button.y + 5))

# Add a resume button when the game is paused
resume_button = pygame.Rect(width // 2 - 100, height // 2 - 25, 200, 50)

def draw_resume_button():
    pygame.draw.rect(screen, (0, 255, 0), resume_button)
    resume_text = font.render("Resume", True, black)
    screen.blit(resume_text, (resume_button.x + 50, resume_button.y + 10))

# Add game states for detailed game flow
START_SCREEN = 0
STORY_SCREEN = 1
GAMEPLAY_SCREEN = 2
GAME_OVER_SCREEN = 3

game_state = START_SCREEN

# Initialize story variables
story_texts = [
    "In the year 3050, Earth has been invaded by alien forces...",
    "You, the last surviving pilot of the Galactic Federation.",
    "Must protect the last remaining base in space.",
    "Collect power-ups and survive as long as you can!",
    "Good luck, pilot!"
]
story_index = 0
story_timer = 0
story_display_duration = 200  # Display each story text for 3 seconds

# Center and fit story texts to the screen width
story_font = pygame.font.Font(None, 28)  # Adjust font size for better fit

# Restore story text to display in parts
story_texts = [
    "In the year 3050, Earth has been invaded by alien forces...",
    "You, the last surviving pilot of the Galactic Federation.",
    "Must protect the last remaining base in space.",
    "Collect power-ups and survive as long as you can!",
    "Good luck, pilot!"
]

# Update draw_story_screen to display story in parts
def draw_story_screen():
    global story_index, story_timer
    if story_index < len(story_texts):
        story_text = story_font.render(story_texts[story_index], True, white)
        text_rect = story_text.get_rect(center=(width // 2, height // 2))
        screen.blit(story_text, text_rect.topleft)
    else:
        pygame.draw.rect(screen, (0, 255, 0), continue_button)
        continue_text = font.render("Continue", True, black)
        screen.blit(continue_text, (continue_button.x + 50, continue_button.y + 10))

# Buttons for start and continue
start_button = pygame.Rect(width // 2 - 100, height // 2 - 50, 200, 50)
continue_button = pygame.Rect(width // 2 - 100, height // 2 + 50, 200, 50)
restart_button = pygame.Rect(width // 2 - 100, height // 2 + 100, 200, 50)

# Draw start screen
def draw_start_screen():
    title_text = font.render("Space Shooter", True, white)
    title_rect = title_text.get_rect(center=(width // 2, height // 2 - 100))
    screen.blit(title_text, title_rect.topleft)
    pygame.draw.rect(screen, (0, 255, 0), start_button)
    start_text = font.render("Play", True, black)
    screen.blit(start_text, (start_button.x + 70, start_button.y + 10))

# Draw game over screen
def draw_game_over_screen():
    game_over_text = font.render("Game Over", True, white)
    game_over_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 100))
    screen.blit(game_over_text, game_over_rect.topleft)
    pygame.draw.rect(screen, (0, 255, 0), restart_button)
    restart_text = font.render("Restart", True, black)
    screen.blit(restart_text, (restart_button.x + 50, restart_button.y + 10))

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
        # Handle pause button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pause_button.collidepoint(event.pos):
                paused = not paused

    # Pause game logic
    if paused:
        pause_overlay = pygame.Surface((width, height))
        pause_overlay.set_alpha(128)  # Semi-transparent overlay
        pause_overlay.fill((0, 0, 0))
        screen.blit(pause_overlay, (0, 0))
        pause_message = font.render("Game Paused", True, white)
        screen.blit(pause_message, (width // 2 - 100, height // 2 - 80))

        # Draw resume button
        draw_resume_button()

        # Handle resume button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if resume_button.collidepoint(event.pos):
                paused = False

        pygame.display.flip()
        continue

    # Update game loop to handle detailed game flow
    if game_state == START_SCREEN:
        draw_start_screen()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_button.collidepoint(event.pos):
                game_state = STORY_SCREEN

    elif game_state == STORY_SCREEN:
        draw_story_screen()
        if story_index < len(story_texts):
            story_timer += 1
            if story_timer > story_display_duration:
                story_index += 1
                story_timer = 0
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if continue_button.collidepoint(event.pos):
                    game_state = GAMEPLAY_SCREEN

    elif game_state == GAMEPLAY_SCREEN:
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

        # Update player collision to use a bounding box
        player_collision_box = pygame.Rect(player.x + 10, player.y + 5, player_width - 20, player_height - 10)

        # Check for collisions
        for enemy, enemy_type in enemies[:]:
            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    enemies.remove((enemy, enemy_type))
                    bullets.remove(bullet)
                    score += 10
                    destroy_sound.play()
                    explosions.append(Explosion(enemy.x, enemy.y, 15))  # Explosion lasts for 15 frames
                    break
            if player_collision_box.colliderect(enemy):
                if not shield_active:
                    enemies.remove((enemy, enemy_type))
                    player_health -= 20
                    damage_sound.play()
                    shake_screen()
                    if player_health <= 0:
                        update_leaderboard(score)
                        game_state = GAME_OVER_SCREEN
                        break

        # Update player collision box position
        player_collision_box.x = player.x + 10
        player_collision_box.y = player.y + 5

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

        # Draw power-ups with different colors
        for power_up in power_ups:
            power_up_type = random.choice(['speed', 'shield', 'double_shot'])
            pygame.draw.rect(screen, power_up_colors[power_up_type], power_up)

        # Update explosions
        for explosion in explosions[:]:
            screen.blit(explosion_image, (explosion.rect.x, explosion.rect.y))
            explosion.timer -= 1
            if explosion.timer <= 0:
                explosions.remove(explosion)

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

        # Draw leaderboard
        draw_leaderboard()

        # Draw pause button in the game loop
        draw_pause_button()

    elif game_state == GAME_OVER_SCREEN:
        draw_game_over_screen()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if restart_button.collidepoint(event.pos):
                reset_game()
                game_state = START_SCREEN

    # Update display
    pygame.display.flip()