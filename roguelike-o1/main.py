import curses
import random

# Definicje znaków
PLAYER_CHAR = '@'
WALL_CHAR = '#'
FLOOR_CHAR = '.'
CHEST_CHAR = 'C'
GOBLIN_CHAR = 'g'
TROLL_CHAR = 'T'
DRAGON_CHAR = 'D'
STAIRS_DOWN_CHAR = '>'

# Konfiguracja gry
MAP_WIDTH = 40
MAP_HEIGHT = 20
NUM_CHESTS = 5
NUM_MONSTERS = 10
MAX_DUNGEON_LEVELS = 20

class Entity:
    def __init__(self, x, y, char, name, hp, attack, defense=0):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense

class Item:
    def __init__(self, name, category, attack=0, defense=0):
        self.name = name
        self.category = category  # 'sword', 'shield', 'boots', 'helmet'
        self.attack = attack
        self.defense = defense

    def __str__(self):
        return f"{self.name} ({self.category}) [Atk: {self.attack}, Def: {self.defense}]"

class Player(Entity):
    def __init__(self, x, y):
        attack = random.randint(0, 5)
        defense = random.randint(0, 5)
        super().__init__(x, y, PLAYER_CHAR, 'Rycerz', 100, attack, defense)
        self.inventory = []
        self.equipped = {}  # {'sword': item, 'shield': item, ...}
        self.exp = 0
        self.level = 1

    def total_attack(self):
        base_attack = self.attack
        for item in self.equipped.values():
            base_attack += item.attack
        return base_attack

    def total_defense(self):
        base_defense = self.defense
        for item in self.equipped.values():
            base_defense += item.defense
        return base_defense

    def check_level_up(self):
        required_exp = self.level * 1000
        if self.exp >= required_exp:
            self.level += 1
            self.attack += 1
            self.defense += 1
            return True
        return False

class Monster(Entity):
    def __init__(self, x, y, char, name, hp, attack, exp_value):
        super().__init__(x, y, char, name, hp, attack)
        self.exp_value = exp_value

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.level = 1
        self.generate_level()

    def generate_level(self):
        self.map = [[FLOOR_CHAR for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        # Dodaj ściany na brzegach
        for x in range(MAP_WIDTH):
            self.map[0][x] = WALL_CHAR
            self.map[MAP_HEIGHT-1][x] = WALL_CHAR
        for y in range(MAP_HEIGHT):
            self.map[y][0] = WALL_CHAR
            self.map[y][MAP_WIDTH-1] = WALL_CHAR

        # Umieść losowo skrzynie
        self.chests = []
        for _ in range(NUM_CHESTS):
            x, y = self.get_random_floor_position()
            self.chests.append((x, y))

        # Umieść losowo potwory
        self.monsters = []
        for _ in range(NUM_MONSTERS):
            x, y = self.get_random_floor_position()
            monster = self.create_monster(x, y)
            self.monsters.append(monster)

        # Umieść gracza
        if hasattr(self, 'player'):
            # Zachowaj ekwipunek i statystyki
            self.player.x, self.player.y = self.get_random_floor_position()
        else:
            x, y = self.get_random_floor_position()
            self.player = Player(x, y)

        # Umieść schody w dół
        x, y = self.get_random_floor_position()
        self.stairs_down = (x, y)

    def create_monster(self, x, y):
        if self.level % 10 == 0:
            # Smok na co 10 poziomie
            monster = Monster(x, y, DRAGON_CHAR, 'Smok', 200, 25, 1000)
        else:
            monster_type = random.choice(['Goblin', 'Troll'])
            if monster_type == 'Goblin':
                monster = Monster(x, y, GOBLIN_CHAR, 'Goblin', 30, 5, 25)
            else:
                monster = Monster(x, y, TROLL_CHAR, 'Troll', 50, 15, 100)
        return monster

    def get_random_floor_position(self):
        while True:
            x = random.randint(1, MAP_WIDTH - 2)
            y = random.randint(1, MAP_HEIGHT - 2)
            if self.map[y][x] == FLOOR_CHAR:
                return x, y

    def generate_random_item(self, exp_value=0):
        categories = ['sword', 'shield', 'boots', 'helmet']
        category = random.choice(categories)
        # Lepsze potwory dają lepsze przedmioty
        max_bonus = min(5 + exp_value // 100, 15)
        attack = random.randint(1, max_bonus) if category == 'sword' else 0
        defense = random.randint(1, max_bonus) if category != 'sword' else 0
        name = f"{category.capitalize()} +{attack + defense}"
        return Item(name, category, attack, defense)

    def draw(self):
        self.stdscr.clear()
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                char = self.map[y][x]
                self.stdscr.addch(y, x, char)

        # Narysuj skrzynie
        for (x, y) in self.chests:
            self.stdscr.addch(y, x, CHEST_CHAR)

        # Narysuj potwory
        for monster in self.monsters:
            self.stdscr.addch(monster.y, monster.x, monster.char)

        # Narysuj schody w dół
        self.stdscr.addch(self.stairs_down[1], self.stairs_down[0], STAIRS_DOWN_CHAR)

        # Narysuj gracza
        self.stdscr.addch(self.player.y, self.player.x, self.player.char)

        # Wyświetl informacje
        self.stdscr.addstr(
            MAP_HEIGHT,
            0,
            f'Poziom: {self.level}  HP: {self.player.hp}  Atk: {self.player.total_attack()}  Def: {self.player.total_defense()}  Exp: {self.player.exp}  Gracz Poziom: {self.player.level}'
        )
        self.stdscr.refresh()

    def handle_input(self):
        key = self.stdscr.getch()
        dx, dy = 0, 0
        self.player_moved = False
        if key == curses.KEY_UP:
            dy = -1
        elif key == curses.KEY_DOWN:
            dy = 1
        elif key == curses.KEY_LEFT:
            dx = -1
        elif key == curses.KEY_RIGHT:
            dx = 1
        elif key == ord('e'):
            self.open_inventory()
        elif key == 10:  # Enter key
            self.attack()
        if dx != 0 or dy != 0:
            self.player_moved = True
        return dx, dy

    def move_player(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        if self.map[new_y][new_x] != WALL_CHAR:
            self.player.x = new_x
            self.player.y = new_y

    def attack(self):
        for monster in self.monsters:
            if abs(monster.x - self.player.x) <= 1 and abs(monster.y - self.player.y) <= 1:
                damage = self.player.total_attack()
                monster.hp -= damage
                if monster.hp <= 0:
                    self.player.exp += monster.exp_value
                    # Sprawdź poziomowanie
                    if self.player.check_level_up():
                        pass  # Możesz dodać informację o awansie
                    # Drop przedmiot z 30% szansą
                    if random.random() < 0.3:
                        item = self.generate_random_item(monster.exp_value)
                        self.player.inventory.append(item)
                    self.monsters.remove(monster)
                break

    def open_inventory(self):
        cursor = 0
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, 'Ekwipunek:')
            for idx, item in enumerate(self.player.inventory):
                marker = '>' if idx == cursor else ' '
                equip_status = ''
                for equipped_item in self.player.equipped.values():
                    if item == equipped_item:
                        equip_status = ' [Założony]'
                        break
                self.stdscr.addstr(idx + 1, 0, f'{marker} {idx + 1}. {item}{equip_status}')
            self.stdscr.addstr(len(self.player.inventory) + 2, 0, 'U - załóż/zdejmij, Esc - powrót')
            self.stdscr.refresh()
            key = self.stdscr.getch()
            if key == curses.KEY_UP and cursor > 0:
                cursor -= 1
            elif key == curses.KEY_DOWN and cursor < len(self.player.inventory) - 1:
                cursor += 1
            elif key == ord('u'):
                if len(self.player.inventory) > 0:
                    item = self.player.inventory[cursor]
                    category = item.category
                    if category in self.player.equipped and self.player.equipped[category] == item:
                        # Zdejmij przedmiot
                        del self.player.equipped[category]
                    else:
                        # Załóż przedmiot, zdejmując ewentualnie poprzedni
                        self.player.equipped[category] = item
            elif key == 27:  # ESC key
                break

    def update(self):
        # Sprawdź, czy gracz najechał na skrzynię
        for chest in self.chests:
            if self.player.x == chest[0] and self.player.y == chest[1]:
                item = self.generate_random_item()
                self.player.inventory.append(item)
                self.chests.remove(chest)
                break

        # Sprawdź, czy gracz najechał na schody w dół
        if self.player.x == self.stairs_down[0] and self.player.y == self.stairs_down[1]:
            if self.level < MAX_DUNGEON_LEVELS:
                self.level += 1
                self.generate_level()
            else:
                self.game_win()

        # Potwory poruszają się
        for monster in self.monsters:
            self.move_monster(monster)

        # Potwory atakują gracza
        for monster in self.monsters:
            if abs(monster.x - self.player.x) <= 1 and abs(monster.y - self.player.y) <= 1:
                if not self.player_moved:
                    damage = monster.attack - self.player.total_defense()
                    if damage < 0:
                        damage = 0
                    self.player.hp -= damage
                    if self.player.hp <= 0:
                        self.game_over()
                        break

    def move_monster(self, monster):
        # Oblicz odległość euklidesową
        dx = self.player.x - monster.x
        dy = self.player.y - monster.y
        dist_sq = dx * dx + dy * dy

        if dist_sq < 9:
            # Poruszaj się w kierunku gracza
            target_dx = 1 if dx > 0 else -1 if dx < 0 else 0
            target_dy = 1 if dy > 0 else -1 if dy < 0 else 0
        else:
            # Poruszaj się losowo
            target_dx = random.choice([-1, 0, 1])
            target_dy = random.choice([-1, 0, 1])

        move_choice = 0
        if monster.name == 'Goblin':
            move_choice = random.choice([0, 1, 2])
        elif monster.name == 'Troll':
            move_choice = random.choice([0, 1])
        elif monster.name == 'Smok':
            move_choice = 1

        for _ in range(move_choice):
            new_x = monster.x + target_dx
            new_y = monster.y + target_dy
            if self.map[new_y][new_x] != WALL_CHAR and not self.is_occupied(new_x, new_y):
                monster.x = new_x
                monster.y = new_y

    def is_occupied(self, x, y):
        if self.player.x == x and self.player.y == y:
            return True
        for other in self.monsters:
            if other.x == x and other.y == y:
                return True
        return False

    def game_over(self):
        self.stdscr.clear()
        self.stdscr.addstr(MAP_HEIGHT // 2, MAP_WIDTH // 2 - 5, 'Koniec gry!')
        self.stdscr.refresh()
        self.stdscr.getch()
        exit()

    def game_win(self):
        self.stdscr.clear()
        self.stdscr.addstr(MAP_HEIGHT // 2, MAP_WIDTH // 2 - 7, 'Gratulacje! Wygrałeś!')
        self.stdscr.refresh()
        self.stdscr.getch()
        exit()

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    game = Game(stdscr)

    while True:
        game.draw()
        dx, dy = game.handle_input()
        game.move_player(dx, dy)
        game.update()

curses.wrapper(main)
