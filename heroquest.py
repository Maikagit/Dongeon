import pygame
import random

# Tile constants
WALL = '#'
FLOOR = '.'
START = 'S'
TRAP = 'T'
MONSTER = 'M'
TREASURE = 'X'

TILE_SIZE = 48
WIDTH = 12
HEIGHT = 12
SCREEN_WIDTH = WIDTH * TILE_SIZE
SCREEN_HEIGHT = HEIGHT * TILE_SIZE + 100

# Colors for drawing
COLORS = {
    WALL: (100, 100, 100),
    FLOOR: (200, 200, 200),
    START: (150, 255, 150),
    TRAP: (255, 100, 100),
    MONSTER: (50, 50, 50),
    TREASURE: (255, 255, 100),
    'hero': (50, 50, 255)
}

# Helper functions for procedural board generation
def dig_room(board, x, y, w, h):
    for j in range(y, y + h):
        for i in range(x, x + w):
            if 0 <= i < WIDTH and 0 <= j < HEIGHT:
                board[j][i] = FLOOR


def surround_with_corridor(board, x, y, w, h):
    for i in range(x - 1, x + w + 1):
        if 0 <= i < WIDTH:
            if y - 1 >= 0:
                board[y - 1][i] = FLOOR
            if y + h < HEIGHT:
                board[y + h][i] = FLOOR
    for j in range(y - 1, y + h + 1):
        if 0 <= j < HEIGHT:
            if x - 1 >= 0:
                board[j][x - 1] = FLOOR
            if x + w < WIDTH:
                board[j][x + w] = FLOOR


def connect_points(board, ax, ay, bx, by):
    x, y = ax, ay
    while (x, y) != (bx, by):
        if random.choice([True, False]):
            if x != bx:
                x += 1 if bx > x else -1
        if y != by:
            y += 1 if by > y else -1
        if x != bx and y != by and random.choice([True, False]):
            x += 1 if bx > x else -1
        board[y][x] = FLOOR


def generate_board():
    board = [[WALL for _ in range(WIDTH)] for _ in range(HEIGHT)]

    base_positions = [(2, 2), (7, 2), (2, 7), (7, 7)]
    rooms = []
    for x, y in base_positions:
        rx = x + random.randint(0, 1)
        ry = y + random.randint(0, 1)
        dig_room(board, rx, ry, 3, 3)
        surround_with_corridor(board, rx, ry, 3, 3)
        rooms.append((rx, ry, 3, 3))

    def center(room):
        x, y, w, h = room
        return x + w // 2, y + h // 2

    for a, b in zip(rooms, rooms[1:]):
        ax, ay = center(a)
        bx, by = center(b)
        connect_points(board, ax, ay, bx, by)

    for x in range(WIDTH):
        board[0][x] = FLOOR
        board[HEIGHT - 1][x] = FLOOR
    for y in range(HEIGHT):
        board[y][0] = FLOOR
        board[y][WIDTH - 1] = FLOOR

    sx, sy = center(rooms[0])
    tx, ty = center(rooms[-1])
    board[sy][sx] = START
    board[ty][tx] = TREASURE

    free = [(x, y) for y in range(HEIGHT) for x in range(WIDTH) if board[y][x] == FLOOR]
    mx, my = random.choice(free)
    board[my][mx] = MONSTER
    free.remove((mx, my))
    tx2, ty2 = random.choice(free)
    board[ty2][tx2] = TRAP

    return board

# Board layout with corridors, a monster room and a treasure room
BOARD_TEMPLATE = [
    "############",
    "#S..####..T#",
    "#..#....#..#",
    "#..#....#..#",
    "####....####",
    "#..........#",
    "#..####..M.#",
    "#..#..#....#",
    "#..#..#....#",
    "#X.#..#..T.#",
    "#..........#",
    "############"
]

class Dice:
    """Six sided dice with 3 sword faces and 3 shield faces"""
    @staticmethod
    def roll():
        return 'sword' if random.randint(0, 5) < 3 else 'shield'

    @staticmethod
    def roll_many(n):
        return [Dice.roll() for _ in range(n)]

class Entity:
    def __init__(self, x, y, attack=2, defense=2, hp=3):
        self.x = x
        self.y = y
        self.attack = attack
        self.defense = defense
        self.hp = hp

    def alive(self):
        return self.hp > 0

class Hero(Entity):
    pass

class Monster(Entity):
    pass

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mini Hero Quest")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        self.board = generate_board()
        self.hero = self._find_start()
        self.message = "Press SPACE to roll move"
        self.move_points = 0
        self.running = True
        self.log_file = open("combat.log", "w")

    def log(self, text):
        print(text)
        self.log_file.write(text + "\n")
        self.log_file.flush()

    def _find_start(self):
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                if tile == START:
                    self.board[y][x] = FLOOR
                    return Hero(x, y)
        raise ValueError("Start position not found")

    def draw_board(self):
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                color = COLORS.get(tile, (0,0,0))
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0,0,0), rect, 1)
        # Draw hero
        rect = pygame.Rect(self.hero.x*TILE_SIZE, self.hero.y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, COLORS['hero'], rect)

    def draw_ui(self):
        msg_surf = self.font.render(self.message, True, (255,255,255))
        self.screen.blit(msg_surf, (10, SCREEN_HEIGHT-90))
        stats = f"HP: {self.hero.hp}  Move: {self.move_points}"
        stats_surf = self.font.render(stats, True, (255,255,255))
        self.screen.blit(stats_surf, (10, SCREEN_HEIGHT-60))

    def roll_move(self):
        self.move_points = random.randint(1,6)
        self.message = f"Move {self.move_points} steps"

    def handle_movement(self, dx, dy):
        if self.move_points <= 0:
            return
        nx = self.hero.x + dx
        ny = self.hero.y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            tile = self.board[ny][nx]
            if tile != WALL:
                self.hero.x = nx
                self.hero.y = ny
                self.move_points -= 1
                if tile == TRAP:
                    self.hero.hp -= 1
                    self.message = "You stepped on a trap!"
                    self.board[ny][nx] = FLOOR
                elif tile == MONSTER:
                    self.handle_combat(Monster(nx, ny))
                    if self.hero.alive():
                        self.board[ny][nx] = FLOOR
                elif tile == TREASURE:
                    self.message = "You found the treasure!"
                    self.board[ny][nx] = FLOOR
                if self.hero.hp <= 0:
                    self.message = "You died!"
                    self.running = False

    def handle_combat(self, monster):
        self.message = "A monster appears!"
        self.log(f"Encountered monster at ({monster.x}, {monster.y})")
        while monster.alive() and self.hero.alive():
            pygame.time.delay(300)
            attack_rolls = Dice.roll_many(self.hero.attack)
            defense_rolls = Dice.roll_many(monster.defense)
            self.log(f"Hero attacks: {attack_rolls} vs {defense_rolls}")
            if attack_rolls.count('sword') > defense_rolls.count('shield'):
                monster.hp -= 1
                self.log(f"Monster takes 1 damage (HP={monster.hp})")
            else:
                self.log("Monster blocks the attack")
            if not monster.alive():
                self.message = "Monster defeated!"
                self.log("Monster defeated!")
                break
            pygame.time.delay(300)
            attack_rolls = Dice.roll_many(monster.attack)
            defense_rolls = Dice.roll_many(self.hero.defense)
            self.log(f"Monster attacks: {attack_rolls} vs {defense_rolls}")
            if attack_rolls.count('sword') > defense_rolls.count('shield'):
                self.hero.hp -= 1
                self.log(f"Hero takes 1 damage (HP={self.hero.hp})")
            else:
                self.log("Hero blocks the attack")
            if not self.hero.alive():
                self.message = "The monster killed you!"
                self.log("Hero defeated!")

    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.move_points == 0:
                        self.roll_move()
                    elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        if event.key == pygame.K_UP:
                            self.handle_movement(0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.handle_movement(0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.handle_movement(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.handle_movement(1, 0)
            self.screen.fill((0,0,0))
            self.draw_board()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()
        self.log_file.close()

if __name__ == "__main__":
    Game().game_loop()
