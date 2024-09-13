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
NUM_MONSTERS = 10
MAX_DUNGEON_LEVELS = 20

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
shield_image = pygame.image.load("images/shield.png").convert_alpha()
boots_image = pygame.image.load("images/boots.png").convert_alpha()
helmet_image = pygame.image.load("images/helmet.png").convert_alpha()

# Czcionki
font = pygame.font.SysFont("Arial", 16)


class ItemCategories(str, Enum):
    """Enum dla kategorii przedmiotów"""

    SWORD = "sword"
    SHIELD = "shield"
    BOOTS = "boots"
    HELMET = "helmet"
    POTION = "potion"


item_images = {
    "potion": potion_image,
    "sword": sword_image,
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
        self.category = category  # 'sword', 'shield', 'boots', 'helmet', 'potion'
        self.image = image
        self.attack = attack
        self.defense = defense
        self.healing = healing

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

    def __init__(self, x, y, image, name, hp, attack, exp_value):
        super().__init__(x, y, image, name, hp, attack)
        self.exp_value = exp_value


class Game:
    def __init__(self):
        self.level = 1
        self.running = True
        self.clock = pygame.time.Clock()
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
        self.monsters = []
        for _ in range(NUM_MONSTERS):
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
        if self.level % 10 == 0:
            # Smok na co 10 poziomie
            monster = Monster(x, y, dragon_image, "Smok", 200, 25, 1000)
        else:
            monster_type = random.choice(["Goblin", "Troll"])
            if monster_type == "Goblin":
                monster = Monster(x, y, goblin_image, "Goblin", 30, 5, 25)
            else:
                monster = Monster(x, y, troll_image, "Troll", 50, 15, 100)
        return monster

    def get_random_floor_position(self):
        while True:
            x = random.randint(1, MAP_WIDTH - 2)
            y = random.randint(1, MAP_HEIGHT - 2)
            if self.map[y][x] == FLOOR_CHAR:
                return x, y

    def generate_random_item(self, exp_value: int = 0) -> Item:
        """Generuje losowy przedmiot na podstawie wartości doświadczenia potwora"""
        # 20% szans na miksturę
        if random.random() < 0.2:
            category = "potion"
            name = "Mikstura Leczenia"
            healing = 25  # Mikstura leczy 25 HP
            image = potion_image
            return Item(name, category, image, healing=healing)
        else:
            categories = ["sword", "shield", "boots", "helmet"]
            category = random.choice(categories)

            max_primary_bonus = min(random.randint(5, 30) + exp_value // 100, 100)
            max_secondary_bonus = max_primary_bonus // 2

            attack = (
                random.randint(1, max_primary_bonus) if category == "sword" else random.randint(0, max_secondary_bonus)
            )
            defense = (
                random.randint(1, max_primary_bonus) if category != "sword" else random.randint(0, max_secondary_bonus)
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

        # Wyświetl informacje
        info_text = (
            f"Poziom: {self.level}  HP: {self.player.hp}/{self.player.max_hp}  "
            f"Atk: {self.player.total_attack()}  Def: {self.player.total_defense()}  "
            f"Exp: {self.player.exp}  Gracz Poziom: {self.player.level}"
        )
        info_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(info_surface, (10, MAP_HEIGHT * TILE_SIZE + 5))

    def handle_input(self):
        dx, dy = 0, 0
        self.player_moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_e:
                    self.open_inventory()
                elif event.key == pygame.K_RETURN:
                    self.attack()
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
        inventory_open = True
        cursor = 0
        while inventory_open:
            screen.fill((0, 0, 0))
            # Wyświetl tytuł
            title_surface = font.render("Ekwipunek:", True, (255, 255, 255))
            screen.blit(title_surface, (10, 10))
            # Wyświetl przedmioty
            for idx, item in enumerate(self.player.inventory):
                y_pos = 40 + idx * 30
                marker = ">" if idx == cursor else " "
                equip_status = ""
                if item.category != "potion":
                    if item in self.player.equipped.values():
                        equip_status = " [Założony]"
                item_text = f"{marker} {idx + 1}. {item}{equip_status}"
                item_surface = font.render(item_text, True, (255, 255, 255))
                screen.blit(item_surface, (10, y_pos))
            # Wyświetl instrukcje
            instructions = "U - użyj/załóż, D - wyrzuć, Esc - powrót"
            instructions_surface = font.render(instructions, True, (255, 255, 255))
            screen.blit(instructions_surface, (10, SCREEN_HEIGHT - 40))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    inventory_open = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and cursor > 0:
                        cursor -= 1
                    elif event.key == pygame.K_DOWN and cursor < len(self.player.inventory) - 1:
                        cursor += 1
                    elif event.key == pygame.K_u:
                        if len(self.player.inventory) > 0:
                            item = self.player.inventory[cursor]
                            category = item.category
                            if category == "potion":
                                # Użyj mikstury
                                self.player.hp += item.healing
                                if self.player.hp > self.player.max_hp:
                                    self.player.hp = self.player.max_hp
                                # Usuń miksturę z ekwipunku
                                del self.player.inventory[cursor]
                                if cursor >= len(self.player.inventory):
                                    cursor = len(self.player.inventory) - 1
                            else:
                                if category in self.player.equipped and self.player.equipped[category] == item:
                                    # Zdejmij przedmiot
                                    del self.player.equipped[category]
                                else:
                                    # Załóż przedmiot, zdejmując ewentualnie poprzedni
                                    self.player.equipped[category] = item
                    elif event.key == pygame.K_d:
                        if len(self.player.inventory) > 0:
                            # Wyrzuć przedmiot
                            del self.player.inventory[cursor]
                            if cursor >= len(self.player.inventory):
                                cursor = len(self.player.inventory) - 1
                    elif event.key == pygame.K_ESCAPE:
                        inventory_open = False

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
            screen.fill((0, 0, 0))
            text_surface = font.render("Koniec gry! Naciśnij Enter, aby wyjść.", True, (255, 255, 255))
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
            screen.fill((0, 0, 0))
            text_surface = font.render("Gratulacje! Wygrałeś! Naciśnij Enter, aby wyjść.", True, (255, 255, 255))
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
        dx, dy = game.handle_input()
        game.move_player(dx, dy)
        game.update()
        game.draw()
        pygame.display.flip()
        game.clock.tick(1)

    pygame.quit()


if __name__ == "__main__":
    main()
