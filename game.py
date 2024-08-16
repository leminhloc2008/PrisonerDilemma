import pygame
import sys
import time
import random
import os
import importlib

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 2
GRID_MARGIN_TOP = 100
PLAYER_MARGIN = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)  # Color for the YCC logo

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Prisoner's Dilemma Game")

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
logo_font = pygame.font.Font(None, 72)  # Larger font for the logo

# Load and scale player assets
def load_and_scale(image_path, scale=0.25):
    img = pygame.image.load(image_path)
    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))

player_idle = load_and_scale('player_idle.png')
player_cooperate = load_and_scale('player_cooperate.png')
player_deflect = load_and_scale('player_deflect.png')

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.choices = []
        self.state = 'idle'
        self.strategy = self.load_strategy(f"{name}.py")

    def load_strategy(self, strategy_file):
        if not os.path.exists(strategy_file):
            print(f"Strategy file {strategy_file} not found. Using default strategy.")
            return lambda own_choices, opponent_choices: random.choice([True, False])

        spec = importlib.util.spec_from_file_location("strategy", strategy_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.make_choice

    def make_choice(self, opponent_choices):
        choice = self.strategy(self.choices, opponent_choices)
        self.state = 'cooperate' if choice else 'deflect'
        return choice


def draw_grid(choices1, choices2, player1, player2):
    for i in range(GRID_WIDTH):
        for j in range(GRID_HEIGHT):
            color = WHITE
            if i < len(choices1) and j == 0:
                color = GREEN if choices1[i] else RED
            elif i < len(choices2) and j == 1:
                color = GREEN if choices2[i] else RED

            pygame.draw.rect(screen, color,
                             (i * CELL_SIZE + (WIDTH - GRID_WIDTH * CELL_SIZE) // 2,
                              j * CELL_SIZE + GRID_MARGIN_TOP,
                              CELL_SIZE - 1, CELL_SIZE - 1))

    # Draw player names next to the grid
    name1 = small_font.render(player1.name, True, BLACK)
    name2 = small_font.render(player2.name, True, BLACK)
    screen.blit(name1, ((WIDTH - GRID_WIDTH * CELL_SIZE) // 2 - name1.get_width() - 10, GRID_MARGIN_TOP))
    screen.blit(name2, ((WIDTH - GRID_WIDTH * CELL_SIZE) // 2 - name2.get_width() - 10, GRID_MARGIN_TOP + CELL_SIZE))


def draw_players(player1, player2):
    # Player 1
    text = font.render(f"{player1.name}: {player1.score}", True, BLACK)
    text_rect = text.get_rect(center=(PLAYER_MARGIN + 50, HEIGHT - 30))
    screen.blit(text, text_rect)

    player_image = player_idle if player1.state == 'idle' else player_cooperate if player1.state == 'cooperate' else player_deflect
    player_rect = player_image.get_rect(center=(PLAYER_MARGIN + 50, HEIGHT - 250))  # Moved much higher
    screen.blit(player_image, player_rect)

    # Player 2
    text = font.render(f"{player2.name}: {player2.score}", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH - PLAYER_MARGIN - 50, HEIGHT - 30))
    screen.blit(text, text_rect)

    player_image = player_idle if player2.state == 'idle' else player_cooperate if player2.state == 'cooperate' else player_deflect
    player_rect = player_image.get_rect(center=(WIDTH - PLAYER_MARGIN - 50, HEIGHT - 250))  # Moved much higher
    screen.blit(player_image, player_rect)

def display_ranking(players, duration=5):
    start_time = time.time()
    while time.time() - start_time < duration:
        screen.fill(WHITE)
        players.sort(key=lambda x: x.score, reverse=True)
        for i, player in enumerate(players):
            text = font.render(f"{i + 1}. {player.name}: {player.score}", True, BLACK)
            screen.blit(text, (WIDTH // 4, 100 + i * 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def draw_logo():
    logo_text = logo_font.render("YCC", True, ORANGE)
    logo_rect = logo_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(logo_text, logo_rect)

def game_loop(players):
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player1, player2 = players[i], players[j]

            for _ in range(30):  # 30 rounds
                screen.fill(WHITE)

                choice1 = player1.make_choice(player2.choices)
                choice2 = player2.make_choice(player1.choices)

                player1.choices.append(choice1)
                player2.choices.append(choice2)

                if choice1 and choice2:  # Both cooperate
                    player1.score += 3
                    player2.score += 3
                elif choice1 and not choice2:  # Player 1 cooperates, Player 2 betrays
                    player2.score += 5
                elif not choice1 and choice2:  # Player 1 betrays, Player 2 cooperates
                    player1.score += 5
                else:  # Both betray
                    player1.score += 1
                    player2.score += 1

                draw_grid(player1.choices, player2.choices, player1, player2)
                draw_players(player1, player2)
                draw_logo()  # Add this line to draw the logo

                pygame.display.flip()
                time.sleep(0.5)  # Add a delay to make the game more observable

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

            player1.choices = []
            player2.choices = []
            player1.state = 'idle'
            player2.state = 'idle'

            # Display ranking after each match
            display_ranking(players)

    # Display final ranking
    display_ranking(players, duration=10)  # Display final ranking for 10 seconds


def main():
    num_players = int(input("Enter the number of players: "))
    players = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        players.append(Player(name))
    game_loop(players)

if __name__ == "__main__":
    main()