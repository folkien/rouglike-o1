import random
from enum import Enum

import pygame

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
SCREEN_WIDTH = 640  # Szerokość okna gry
SCREEN_HEIGHT = 480  # Wysokość okna gry
TILE_SIZE = 32  # Rozmiar kafelka (32x32 px)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Pygame")

# Definicje znaków
PLAYER_CHAR = "@"
WALL_CHAR = "#"
FLOOR_CHAR = "."
CHEST_CHAR = "C"
GOBLIN_CHAR = "g"
TROLL_CHAR = "T"
DRAGON_CHAR = "D"
STAIRS_DOWN_CHAR = ">"

# Konfiguracja gry
MAP_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_HEIGHT = SCREEN_HEIGHT // TILE_SIZE - 2  # Odejmiemy 2 linie na interfejs
NUM_CHESTS = 5
NUM_MONSTERS = 6
MAX_DUNGEON_LEVELS = 30

# Kolory
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (0, 0, 255)
COLOR_PURPLE = (128, 0, 128)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLACK = (0, 0, 0)

# Ładowanie obrazów
player_image = pygame.image.load("images/player.png").convert_alpha()
wall_image = pygame.image.load("images/wall.png").convert_alpha()
floor_image = pygame.image.load("images/floor.png").convert_alpha()
chest_image = pygame.image.load("images/chest.png").convert_alpha()
goblin_image = pygame.image.load("images/goblin.png").convert_alpha()
troll_image = pygame.image.load("images/troll.png").convert_alpha()
dragon_image = pygame.image.load("images/dragon.png").convert_alpha()
stairs_down_image = pygame.image.load("images/stairs_down.png").convert_alpha()
potion_image = pygame.image.load("images/potion.png").convert_alpha()
sword_image = pygame.image.load("images/sword.png").convert_alpha()
spear_image = pygame.image.load("images/spear.png").convert_alpha()
axe_image = pygame.image.load("images/axe.png").convert_alpha()
shield_image = pygame.image.load("images/shield.png").convert_alpha()
boots_image = pygame.image.load("images/boots.png").convert_alpha()
helmet_image = pygame.image.load("images/helmet.png").convert_alpha()

# Czcionki
font = pygame.font.SysFont("Arial", 16)
bold_font = pygame.font.SysFont("Arial", 16, bold=True)


class ItemCategories(str, Enum):
    """Enum dla kategorii przedmiotów"""

    SWORD = "sword"
    SPEAR = "spear"
    AXE = "axe"
    SHIELD = "shield"
    BOOTS = "boots"
    HELMET = "helmet"
    POTION = "potion"


item_images = {
    "potion": potion_image,
    "sword": sword_image,
    "spear": spear_image,
    "axe": axe_image,
    "shield": shield_image,
    "boots": boots_image,
    "helmet": helmet_image,
}


class Entity:
    """Klasa bazowa dla gracza i potworów"""

    def __init__(self, x, y, image, name, hp, attack, defense=0):
        self.x = x
        self.y = y
        self.image = image
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense

    def draw(self, surface):
        surface.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))


class Item:
    """Klasa reprezentująca przedmioty w grze"""

    def __init__(self, name, category, image, attack=0, defense=0, healing=0):
        self.name = name
        self.category = category  # 'sword', 'spear', 'axe', 'shield', 'boots', 'helmet', 'potion'
        self.image = image
        self.attack = attack
        self.defense = defense
        self.healing = healing

    @property
    def total(self) -> int:
        """Total stat value"""
        return self.attack + self.defense + self.healing

    def __str__(self):
        if self.category == "potion":
            return f"{self.name} (Leczy {self.healing} HP)"
        else:
            return f"{self.name} ({self.category}) [Atk: {self.attack}, Def: {self.defense}]"


class Player(Entity):
    """Klasa reprezentująca postać gracza"""

    def __init__(self, x, y):
        attack = random.randint(0, 5)
        defense = random.randint(0, 5)
        super().__init__(x, y, player_image, "Rycerz", 100, attack, defense)
        self.max_hp = 100  # Maksymalne punkty życia
        self.inventory = []
        self.equipped = {}  # {'sword': item, 'shield': item, ...}
        self.exp = 0
        self.level = 1

    def total_attack(self) -> int:
        """Zwraca całkowitą wartość ataku, łącznie z wyposażonymi przedmiotami"""
        return self.attack + sum(item.attack for item in self.equipped.values())

    def total_defense(self) -> int:
        """Zwraca całkowitą wartość obrony, łącznie z wyposażonymi przedmiotami"""
        return self.defense + sum(item.defense for item in self.equipped.values())

    def check_level_up(self) -> bool:
        """Sprawdza, czy gracz zdobył wystarczająco doświadczenia do awansu"""
        required_exp = self.level * 1000
        if self.exp >= required_exp:
            self.level += 1
            self.attack += 1
            self.defense += 1
            return True
        return False


class Monster(Entity):
    """Klasa reprezentująca potwora w grze"""

    def __init__(self, x, y, image, name, hp, attack, defense, exp_value):
        super().__init__(x, y, image, name, hp, attack, defense)
        self.exp_value = exp_value


class Game:
    def __init__(self):
        self.level = 1
        self.running = True
        self.generate_level()

    def generate_level(self):
        self.map = [[FLOOR_CHAR for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        # Dodaj ściany na brzegach
        for x in range(MAP_WIDTH):
            self.map[0][x] = WALL_CHAR
            self.map[MAP_HEIGHT - 1][x] = WALL_CHAR
        for y in range(MAP_HEIGHT):
            self.map[y][0] = WALL_CHAR
            self.map[y][MAP_WIDTH - 1] = WALL_CHAR

        # Umieść losowo skrzynie
        self.chests = []
        for _ in range(NUM_CHESTS):
            x, y = self.get_random_floor_position()
            self.chests.append((x, y))

        # Umieść losowo potwory
        monsters_amount = min(NUM_MONSTERS + self.level, 30)
        self.monsters = []
        for _ in range(monsters_amount):
            x, y = self.get_random_floor_position()
            monster = self.create_monster(x, y)
            self.monsters.append(monster)

        # Umieść gracza
        if hasattr(self, "player"):
            # Zachowaj ekwipunek i statystyki
            self.player.x, self.player.y = self.get_random_floor_position()
        else:
            x, y = self.get_random_floor_position()
            self.player = Player(x, y)

        # Umieść schody w dół
        x, y = self.get_random_floor_position()
        self.stairs_down = (x, y)

    def create_monster(self, x, y):
        """Create monster based on dungeon level"""

        # Goblin: Level 0: 80%, Level 5 and above: 30%
        goblin_probability = 0.8
        if self.level >= 5:
            goblin_probability = 0.3

        # Troll: Level 3 and above: 30%
        troll_probability = 0.05
        if self.level >= 3:
            troll_probability = 0.30

        # Dragon: Level is multiple of 10, Always dragons
        dragon_probability = self.level / 100
        if self.level != 0 and self.level % 10 == 0:
            dragon_probability = 0.80

        monster_type = random.choices(
            population=["Goblin", "Troll", "Smok"],
            weights=[goblin_probability, troll_probability, dragon_probability],
        )[0]

        if monster_type == "Goblin":
            monster = Monster(x, y, goblin_image, "Goblin", hp=30, attack=8, defense=3, exp_value=50)
        elif monster_type == "Troll":
            monster = Monster(x, y, troll_image, "Troll", hp=100, attack=15, defense=40, exp_value=250)
        elif monster_type == "Smok":
            monster = Monster(x, y, dragon_image, "Smok", hp=400, attack=55, defense=25, exp_value=1200)

        return monster

    def get_random_floor_position(self):
        while True:
            x = random.randint(1, MAP_WIDTH - 2)
            y = random.randint(1, MAP_HEIGHT - 2)
            if self.map[y][x] == FLOOR_CHAR:
                return x, y

    def generate_random_item(self, dungeon_level: int, exp_value: int = 0) -> Item:
        """Generuje losowy przedmiot na podstawie wartości doświadczenia potwora"""
        # 20% szans na miksturę
        if random.random() < 0.2:
            category = "potion"
            name = "Mikstura Leczenia"
            healing = 25  # Mikstura leczy 25 HP
            image = item_images[category]
            return Item(name, category, image, healing=healing)
        else:
            categories = ["sword", "spear", "axe", "shield", "boots", "helmet"]
            category = random.choice(categories)

            max_primary_bonus = min(random.randint(5, 30) + dungeon_level + exp_value // 100, 100)
            max_secondary_bonus = max_primary_bonus // 2

            attack = (
                random.randint(1, max_primary_bonus)
                if category in ["sword", "spear", "axe"]
                else random.randint(0, max_secondary_bonus)
            )
            defense = (
                random.randint(1, max_primary_bonus)
                if category not in ["sword", "spear", "axe"]
                else random.randint(0, max_secondary_bonus)
            )
            name = f"{category.capitalize()} +{attack + defense}"
            image = item_images[category]
            return Item(name, category, image, attack, defense)

    def draw(self):
        # Rysuj mapę
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = self.map[y][x]
                pos = (x * TILE_SIZE, y * TILE_SIZE)
                if tile == FLOOR_CHAR:
                    screen.blit(floor_image, pos)
                elif tile == WALL_CHAR:
                    screen.blit(wall_image, pos)

        # Narysuj skrzynie
        for x, y in self.chests:
            screen.blit(chest_image, (x * TILE_SIZE, y * TILE_SIZE))

        # Narysuj schody w dół
        x, y = self.stairs_down
        screen.blit(stairs_down_image, (x * TILE_SIZE, y * TILE_SIZE))

        # Narysuj potwory
        for monster in self.monsters:
            monster.draw(screen)

        # Narysuj gracza
        self.player.draw(screen)

        # Wyświetl pasek życia
        self.draw_health_bar()

        # Wyświetl informacje
        self.draw_stats()

        pygame.display.flip()

    def draw_health_bar(self):
        bar_width = 200
        bar_height = 20
        x = 10
        y = MAP_HEIGHT * TILE_SIZE + 5

        # Tło paska
        pygame.draw.rect(screen, COLOR_RED, (x, y, bar_width, bar_height))
        # Wypełnienie paska
        hp_ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(screen, COLOR_GREEN, (x, y, bar_width * hp_ratio, bar_height))
        # Obramowanie
        pygame.draw.rect(screen, COLOR_WHITE, (x, y, bar_width, bar_height), 2)

    def draw_stats(self):
        y_offset = MAP_HEIGHT * TILE_SIZE + 30
        # Atak
        atk_text = bold_font.render(f"Atk: {self.player.total_attack()}", True, COLOR_BLUE)
        screen.blit(atk_text, (10, y_offset))
        # Obrona
        def_text = bold_font.render(f"Def: {self.player.total_defense()}", True, COLOR_PURPLE)
        screen.blit(def_text, (100, y_offset))
        # Poziom gracza
        level_text = bold_font.render(f"Lvl: {self.player.level}", True, COLOR_WHITE)
        screen.blit(level_text, (200, y_offset))
        # Doświadczenie
        exp_text = bold_font.render(f"Exp: {self.player.exp}", True, COLOR_WHITE)
        screen.blit(exp_text, (350, y_offset))
        # Poziom lochu
        dungeon_level_text = bold_font.render(f"Stage: {self.level}", True, COLOR_WHITE)
        screen.blit(dungeon_level_text, (500, y_offset))

    def handle_input(self):
        dx, dy = 0, 0
        self.player_moved = False
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting_for_input = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        dy = -1
                        waiting_for_input = False
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                        waiting_for_input = False
                    elif event.key == pygame.K_LEFT:
                        dx = -1
                        waiting_for_input = False
                    elif event.key == pygame.K_RIGHT:
                        dx = 1
                        waiting_for_input = False
                    elif event.key == pygame.K_e:
                        self.open_inventory()
                        self.draw()  # Odśwież ekran po wyjściu z ekwipunku
                    elif event.key == pygame.K_RETURN:
                        self.attack()
                        waiting_for_input = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        waiting_for_input = False
            # Rysuj ekran podczas oczekiwania na wejście
            self.draw()
        if dx != 0 or dy != 0:
            self.player_moved = True
        return dx, dy

    def move_player(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        if self.map[new_y][new_x] != WALL_CHAR and not self.is_occupied(new_x, new_y):
            self.player.x = new_x
            self.player.y = new_y

    def attack(self):
        for monster in self.monsters:
            if abs(monster.x - self.player.x) <= 1 and abs(monster.y - self.player.y) <= 1:
                # Monster defense, if critical hit, ignore defense
                defence = monster.defense
                if random.random() < 0.1:
                    defence = 0

                # Damage calculation
                damage = max(1, self.player.total_attack() - defence)
                monster.hp -= damage

                #  Check : Monster is dead
                if monster.hp <= 0:
                    self.player.exp += monster.exp_value
                    # Sprawdź poziomowanie
                    if self.player.check_level_up():
                        pass  # Możesz dodać informację o awansie
                    # Drop przedmiot z 30% szansą
                    if random.random() < 0.3:
                        item = self.generate_random_item(dungeon_level=self.level, exp_value=monster.exp_value)
                        self.player.inventory.append(item)
                    self.monsters.remove(monster)
                break

    def open_inventory(self):
        inventory_open = True
        cursor = 0
        while inventory_open:
            screen.fill(COLOR_BLACK)
            # Wyświetl tytuł
            title_surface = font.render("Ekwipunek:", True, COLOR_WHITE)
            screen.blit(title_surface, (10, 10))
            # Wyświetl przedmioty
            inventory_sorted = sorted(self.player.inventory, key=lambda x: x.total, reverse=True)

            for idx, item in enumerate(inventory_sorted):
                y_pos = 40 + idx * 30
                marker = ">" if idx == cursor else " "
                equip_status = ""
                if item.category != "potion":
                    if item in self.player.equipped.values():
                        equip_status = " [Założony]"
                item_text = f"{marker} {idx + 1}. {item}{equip_status}"
                item_surface = font.render(item_text, True, COLOR_WHITE)
                screen.blit(item_surface, (10, y_pos))

            # Wyświetl instrukcje
            instructions = "U - użyj/załóż, D - wyrzuć, Esc - powrót"
            instructions_surface = font.render(instructions, True, COLOR_WHITE)
            screen.blit(instructions_surface, (10, SCREEN_HEIGHT - 40))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    inventory_open = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and cursor > 0:
                        cursor -= 1
                    elif event.key == pygame.K_DOWN and cursor < len(inventory_sorted) - 1:
                        cursor += 1
                    elif event.key == pygame.K_u:
                        if len(inventory_sorted) > 0:
                            item = inventory_sorted[cursor]
                            category = item.category
                            if category == "potion":
                                # Użyj mikstury
                                self.player.hp += item.healing
                                if self.player.hp > self.player.max_hp:
                                    self.player.hp = self.player.max_hp
                                # Usuń miksturę z ekwipunku
                                self.player.inventory.remove(item)
                                inventory_sorted.remove(item)
                                if cursor >= len(inventory_sorted):
                                    cursor = len(inventory_sorted) - 1
                            else:
                                if category in self.player.equipped and self.player.equipped[category] == item:
                                    # Zdejmij przedmiot
                                    del self.player.equipped[category]
                                else:
                                    # Załóż przedmiot, zdejmując ewentualnie poprzedni
                                    self.player.equipped[category] = item
                    elif event.key == pygame.K_d:
                        if len(inventory_sorted) > 0:
                            # Wyrzuć przedmiot
                            item = inventory_sorted[cursor]
                            self.player.inventory.remove(item)
                            inventory_sorted.remove(item)
                            if cursor >= len(inventory_sorted):
                                cursor = len(inventory_sorted) - 1
                    elif event.key == pygame.K_ESCAPE:
                        inventory_open = False

    def update(self):
        # Sprawdź, czy gracz najechał na skrzynię
        for chest in self.chests:
            if self.player.x == chest[0] and self.player.y == chest[1]:
                item = self.generate_random_item(dungeon_level=self.level)
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
                    defence = self.player.total_defense()
                    # Critical hit, ignore defense
                    if random.random() < 0.1:
                        defence = 0

                    damage = max(1, monster.attack - defence)

                    # Player : Get damage
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
        if monster.name == "Goblin":
            move_choice = random.choice([0, 1, 2])
        elif monster.name == "Troll":
            move_choice = random.choice([0, 1])
        elif monster.name == "Smok":
            move_choice = 1

        for _ in range(move_choice):
            new_x = monster.x + target_dx
            new_y = monster.y + target_dy
            if (
                0 <= new_x < MAP_WIDTH
                and 0 <= new_y < MAP_HEIGHT
                and self.map[new_y][new_x] != WALL_CHAR
                and not self.is_occupied(new_x, new_y)
            ):
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
        game_over_screen = True
        while game_over_screen:
            screen.fill(COLOR_BLACK)
            text_surface = font.render("Koniec gry! Naciśnij Enter, aby wyjść.", True, COLOR_WHITE)
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    game_over_screen = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.running = False
                        game_over_screen = False

    def game_win(self):
        game_win_screen = True
        while game_win_screen:
            screen.fill(COLOR_BLACK)
            text_surface = font.render("Gratulacje! Wygrałeś! Naciśnij Enter, aby wyjść.", True, COLOR_WHITE)
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    game_win_screen = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.running = False
                        game_win_screen = False


def main():
    game = Game()

    while game.running:
        game.draw()
        dx, dy = game.handle_input()
        game.move_player(dx, dy)
        game.update()

    pygame.quit()


if __name__ == "__main__":
    main()
