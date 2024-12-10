# Import necessary libraries for game development, random generation, and mathematical operations
import pygame
import random
import math

# Initialize Pygame modules
pygame.init()

# Set up the game window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Racing Game")

# Define color constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class Sound:
    # Manages game sound effects
    def __init__(self):
        # Initialize Pygame mixer and load sound files
        pygame.mixer.init()
        self.crash_sound = pygame.mixer.Sound('crash.wav')
        self.engine_sound = pygame.mixer.Sound('engine.wav')
        self.score_sound = pygame.mixer.Sound('score.wav')
        
    # Methods to play specific sound effects
    def play_crash(self):
        self.crash_sound.play()
        
    def play_engine(self):
        self.engine_sound.play()
        
    def play_score(self):
        self.score_sound.play()

class CarSelection:
    # Manages car selection before the game starts
    def __init__(self):
        # List of available cars with their properties
        self.cars = [
            {'image': 'Black_viper.png', 'name': 'Black Viper', 'speed': 6},
            {'image': 'car.png', 'name': 'Red Car', 'speed': 5},
            {'image': 'Audi.png', 'name': 'Audi', 'speed': 7}
        ]
        self.selected_index = 0
        
    # Cycle through cars in forward direction
    def next_car(self):
        self.selected_index = (self.selected_index + 1) % len(self.cars)
        
    # Cycle through cars in backward direction
    def previous_car(self):
        self.selected_index = (self.selected_index - 1) % len(self.cars)
        
    # Return the currently selected car
    def get_selected_car(self):
        return self.cars[self.selected_index]

class Car(pygame.sprite.Sprite):
    # Represents the player's car with movement and collision mechanics
    def __init__(self, car_data):
        super().__init__()
        # Load and scale car image
        self.original_image = pygame.image.load(car_data['image'])
        self.original_image = pygame.transform.scale(self.original_image, (70, 70))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        
        # Initial car position
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.position = WINDOW_WIDTH // 2
        
        # Car properties
        self.lives = 3
        self.spinning = False  # Collision spin effect
        self.spin_angle = 0
        self.invulnerable = False  # Temporary invincibility after hit
        self.invulnerable_timer = 0
        self.speed = car_data['speed']
        
    def update(self):
        # Handle car spinning after collision
        if self.spinning:
            # Rotate car during spin
            self.spin_angle += 10
            if self.spin_angle >= 360:
                # Reset spin and enable invulnerability
                self.spin_angle = 0
                self.spinning = False
                self.invulnerable = True
                self.invulnerable_timer = 60 
            self.image = pygame.transform.rotate(self.original_image, self.spin_angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            # Normal car movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > 100:
                self.position -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH - 100:
                self.position += self.speed
            self.rect.centerx = self.position
            self.image = self.original_image

        # Manage invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

    def hit(self):
        # Handle car being hit by an obstacle
        if not self.invulnerable and not self.spinning:
            self.lives -= 1
            self.spinning = True
            self.spin_angle = 0
            return True
        return False

class Obstacle(pygame.sprite.Sprite):
    # Represents obstacles that the car must avoid
    def __init__(self):
        super().__init__()
        # Load and scale a random obstacle image
        obstacle_images = ['Police.png', 'taxi.png', 'Ambulance.png']
        self.image = pygame.image.load(random.choice(obstacle_images))
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.rect = self.image.get_rect()
        
        # Random initial position and speed
        self.rect.x = random.randint(100, WINDOW_WIDTH - 100 - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(3, 7)

    def update(self):
        # Move the obstacle down the screen
        self.rect.y += self.speed
        # Remove the obstacle if it goes off-screen
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    # Represents power-ups that provide benefits to the player
    def __init__(self):
        super().__init__()
        # Define power-up types and their effects
        self.types = {
            'shield': {'image': 'shield.png', 'effect': 'invulnerability'},
            'speed': {'image': 'speed.png', 'effect': 'boost'},
            'life': {'image': 'heart.png', 'effect': 'extra_life'}
        }
        # Randomly select a power-up type
        self.type = random.choice(list(self.types.keys()))
        # Load and scale the power-up image
        self.image = pygame.image.load(self.types[self.type]['image'])
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        
        # Random initial position
        self.rect.x = random.randint(100, WINDOW_WIDTH - 100 - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = 3
        
    def update(self):
        # Move the power-up down the screen
        self.rect.y += self.speed
        # Remove the power-up if it goes off-screen
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Game:
    # Manages the overall game state and logic
    def __init__(self):
        self.sound = Sound()
        self.car_selection = CarSelection()
        self.state = 'menu'  # Initial game state
        self.paused = False
        self.power_ups = pygame.sprite.Group()
        self.initialize_game()
        
    def initialize_game(self):
        # Set up the game with the selected car and initial conditions
        selected_car = self.car_selection.get_selected_car()
        self.car = Car(selected_car)
        self.obstacles = pygame.sprite.Group()
        self.road_lines = []
        self.score = 0
        self.game_over = False
        
        # Create initial road lines for visual effect
        for i in range(10):
            y = i * 100
            self.road_lines.append({'x': WINDOW_WIDTH // 2, 'y': y})

    def create_obstacle(self):
        # Randomly create obstacles with a limit on the number
        if random.random() < 0.02 and len(self.obstacles) < 5:
            self.obstacles.add(Obstacle())

    def create_power_up(self):
        # Randomly create power-ups
        if random.random() < 0.01:
            self.power_ups.add(PowerUp())
            
    def toggle_pause(self):
        # Toggle the paused state of the game
        self.paused = not self.paused

    def update_road_lines(self):
        # Move road lines to create a scrolling effect
        for line in self.road_lines:
            line['y'] += 5
            if line['y'] > WINDOW_HEIGHT:
                line['y'] = -30

    def apply_power_up(self, power_up_type):
        # Apply the effect of a collected power-up
        if power_up_type == 'shield':
            self.car.invulnerable = True
            self.car.invulnerable_timer = 300
            self.sound.play_score()
        elif power_up_type == 'speed':
            self.car.speed += 2
            self.sound.play_score()
        elif power_up_type == 'life':
            self.car.lives += 1
            self.sound.play_score()

    def update(self):
        # Update game elements if the game is in the playing state
        if self.state == 'playing' and not self.game_over:
            self.car.update()
            self.obstacles.update()
            self.power_ups.update()
            self.update_road_lines()
            self.create_obstacle()
            self.create_power_up()

            # Check for power-up collisions
            power_up_hits = pygame.sprite.spritecollide(self.car, self.power_ups, True)
            for power_up in power_up_hits:
                self.apply_power_up(power_up.type)

            # Check for obstacle collisions
            if not self.car.spinning:
                for obstacle in self.obstacles:
                    if pygame.sprite.collide_rect(self.car, obstacle):
                        if self.car.hit():
                            self.sound.play_crash()
                            obstacle.kill()
                            if self.car.lives <= 0:
                                self.game_over = True
                                self.state = 'game_over'

            # Increment score over time
            self.score += 1 // 60

    def draw_menu(self):
        # Draw the main menu screen
        screen.fill(BLACK)
        font = pygame.font.Font(None, 48)
        
        title = font.render("Racing Game", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        car_data = self.car_selection.get_selected_car()
        car_name = font.render(car_data['name'], True, WHITE)
        screen.blit(car_name, (WINDOW_WIDTH//2 - car_name.get_width()//2, 200))
        
        instructions = font.render("<- -> to select car, SPACE to start", True, WHITE)
        screen.blit(instructions, (WINDOW_WIDTH//2 - instructions.get_width()//2, 300))
        
        pygame.display.flip()
        
    def draw_pause(self):
        # Draw the pause screen
        screen.fill(BLACK)
        font = pygame.font.Font(None, 48)
        pause_text = font.render("Game Paused", True, WHITE)
        instructions_text = font.render("Press P to resume", True, WHITE)
        screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        screen.blit(instructions_text, (WINDOW_WIDTH // 2 - instructions_text.get_width() // 2, WINDOW_HEIGHT // 2 + 10))
        pygame.display.flip()

    def draw(self):
        # Draw the game screen
        screen.fill(BLACK)
        
        # Draw the road
        pygame.draw.rect(screen, WHITE, (100, 0, WINDOW_WIDTH-200, WINDOW_HEIGHT))
        pygame.draw.rect(screen, BLACK, (120, 0, WINDOW_WIDTH-240, WINDOW_HEIGHT))
        
        # Draw road lines
        for line in self.road_lines:
            pygame.draw.rect(screen, WHITE, 
                           (line['x'] - 5, line['y'], 10, 30))

        # Draw obstacles and power-ups
        self.obstacles.draw(screen)
        self.power_ups.draw(screen)
        
        # Draw the car, flashing if invulnerable
        if not self.car.invulnerable or pygame.time.get_ticks() % 200 < 100:
            screen.blit(self.car.image, self.car.rect)

        # Draw the score and lives
        font = pygame.font.Font(None, 36)

        for i in range(self.car.lives):
            life_image = pygame.transform.scale(self.car.original_image, (25, 40))
            screen.blit(life_image, (10 + i * 30, 10))
        
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH - 150, 10))

        # Draw game over message if applicable
        if self.game_over:
            game_over_text = font.render('Game Over! Press R to restart', True, RED)
            screen.blit(game_over_text, 
                       (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 
                        WINDOW_HEIGHT//2))

        pygame.display.flip()

# Initialize the game
game = Game()
clock = pygame.time.Clock()
running = True

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game.state == 'menu':
                if event.key == pygame.K_LEFT:
                    game.car_selection.previous_car()
                elif event.key == pygame.K_RIGHT:
                    game.car_selection.next_car()
                elif event.key == pygame.K_SPACE:
                    game.state = 'playing'
                    game.sound.play_engine()
            elif game.state == 'playing':
                if event.key == pygame.K_p:
                    game.toggle_pause()
            elif game.state == 'game_over':
                if event.key == pygame.K_r:
                    game.state = 'menu'
                    game.initialize_game()

    # Update and draw the game based on the current state
    if game.state == 'menu':
        game.draw_menu()
    elif game.state == 'playing' and not game.paused:
        game.update()
        game.draw()
    elif game.paused:
        game.draw_pause()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()