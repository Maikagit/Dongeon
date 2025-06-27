import random
import time
from flask import Flask, request, redirect, url_for, render_template_string

# Tile constants
WALL = '#'
FLOOR = '.'
START = 'S'
TRAP = 'T'
MONSTER = 'M'
TREASURE = 'X'

WIDTH = 12
HEIGHT = 12

# Board generation helpers (copied from heroquest)
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
    room_w, room_h = 4, 5  # larger rectangular rooms
    rooms = []
    for x, y in base_positions:
        rx = x + random.randint(0, 1)
        ry = y + random.randint(0, 1)
        dig_room(board, rx, ry, room_w, room_h)
        surround_with_corridor(board, rx, ry, room_w, room_h)
        rooms.append((rx, ry, room_w, room_h))

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

class Dice:
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
        self.board = generate_board()
        self.hero = self._find_start()
        self.message = "Press ROLL to move"
        self.move_points = 0
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

    def roll_move(self):
        if self.move_points == 0:
            self.move_points = random.randint(1, 6)
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

    def handle_combat(self, monster):
        self.message = "A monster appears!"
        self.log(f"Encountered monster at ({monster.x}, {monster.y})")
        while monster.alive() and self.hero.alive():
            time.sleep(0.3)
            attack_rolls = Dice.roll_many(self.hero.attack)
            defense_rolls = Dice.roll_many(monster.defense)
            self.log(f"Hero attacks: {attack_rolls} vs {defense_rolls}")
            damage = attack_rolls.count('sword') - defense_rolls.count('shield')
            if damage > 0:
                monster.hp -= damage
                self.log(f"Monster takes {damage} damage (HP={monster.hp})")
            else:
                self.log("Monster blocks the attack")
            if not monster.alive():
                self.message = "Monster defeated!"
                self.log("Monster defeated!")
                break
            time.sleep(0.3)
            attack_rolls = Dice.roll_many(monster.attack)
            defense_rolls = Dice.roll_many(self.hero.defense)
            self.log(f"Monster attacks: {attack_rolls} vs {defense_rolls}")
            damage = attack_rolls.count('sword') - defense_rolls.count('shield')
            if damage > 0:
                self.hero.hp -= damage
                self.log(f"Hero takes {damage} damage (HP={self.hero.hp})")
            else:
                self.log("Hero blocks the attack")
            if not self.hero.alive():
                self.message = "The monster killed you!"
                self.log("Hero defeated!")

    def board_with_hero(self):
        board = [row[:] for row in self.board]
        board[self.hero.y][self.hero.x] = '@'
        return board

a = Flask(__name__)
GAME = Game()

TEMPLATE = """
<!doctype html>
<title>Mini Hero Quest</title>
<h1>Mini Hero Quest (Web)</h1>
<pre>{{board}}</pre>
<p>{{message}}</p>
<p>HP: {{hp}} Move: {{move_points}}</p>
<form method="post" action="/roll"><button type="submit">Roll</button></form>
<form method="post" action="/move">
<button name="dir" value="up">Up</button>
<button name="dir" value="down">Down</button>
<button name="dir" value="left">Left</button>
<button name="dir" value="right">Right</button>
</form>
<form method="post" action="/reset"><button type="submit">Reset</button></form>
"""

@a.route("/", methods=["GET"])
def index():
    board = "\n".join("".join(row) for row in GAME.board_with_hero())
    return render_template_string(TEMPLATE, board=board, message=GAME.message, hp=GAME.hero.hp, move_points=GAME.move_points)

@a.route("/roll", methods=["POST"])
def roll():
    GAME.roll_move()
    return redirect(url_for('index'))

@a.route("/move", methods=["POST"])
def move():
    d = request.form.get('dir')
    moves = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
    if d in moves:
        dx, dy = moves[d]
        GAME.handle_movement(dx, dy)
    return redirect(url_for('index'))

@a.route("/reset", methods=["POST"])
def reset():
    global GAME
    GAME = Game()
    return redirect(url_for('index'))

if __name__ == "__main__":
    a.run(host="0.0.0.0", port=8000)

