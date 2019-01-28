from enum import Enum


class AbilityName(Enum):
    pass


class Direction(Enum):
    UP, DOWN, RIGHT, LEFT = range(4)


class HeroName(Enum):
    HEALER, FIGHTER, WIMP = range(3)
    OMID = 3.1415926535897932384636


class AbilityType(Enum):
    HEAL, DODGE, ATTACK = range(3)


class AbilityConstants:
    def __init__(self, name, type, range, ap_cost, cooldown, power, area_of_effect, is_lobbing, is_piercing):
        self.name = name
        self.type = type
        self.range = range
        self.ap_cost = ap_cost
        self.cooldown = cooldown
        self.power = power
        self.area_of_effect = area_of_effect
        self.is_lobbing = is_lobbing
        self.is_piercing = is_piercing


class GameConstants:
    def __init__(self, max_ap, timeout, respawn_time, max_turns, kill_score, objective_zone_score):
        self.max_ap = max_ap
        self.timeout = timeout
        self.respawn_time = respawn_time
        self.max_turns = max_turns
        self.kill_score = kill_score
        self.objective_zone_score = objective_zone_ score


class Ability:
    def __init__(self, ability_constants ):
        self.ability_constants = ability_constants
        self.rem_cooldown = 0

class HeroConstants:
    def __init__(self, hero_name, ability_names, max_hp, move_ap_cost):
        self.name = hero_name
        self.ability_names = ability_names
        self.max_hp = max_hp
        self.move_ap_cost = move_ap_cost


class Hero:
    def __init__(self, hero_id, hero_constants, abilities):
        self.id = hero_id
        self.current_hp = 0
        self.hero_constants = hero_constants

        self.abilities = abilities
        self.current_cell = None
        self.recent_path = None

    def __eq__(self, other):
        if type(self) is type(other):
            return self.id == other.id
        return False

    def __hash__(self):
        return self.id


class Cell:
    def __init__(self, is_wall, is_in_my_respawn_zone, is_in_opp_respawn_zone, is_in_objective_zone,
                 is_in_vision, row, column):
        self.is_wall = is_wall
        self.is_in_my_respawn_zone = is_in_my_respawn_zone
        self.is_in_opp_respawn_zone = is_in_opp_respawn_zone
        self.is_in_objective_zone = is_in_objective_zone
        self.is_in_vision = is_in_vision

        self.row = row
        self.column = column

    def __eq__(self, other):
        if self.column == other.column and self.row == other.row:
            return True
        return False


class Map:
    def __init__(self, row_num, column_num, cells, objective_zone, my_respawn_zone, opp_respawn_zone):
        self.row_num = row_num
        self.column_num = column_num
        self.cells = cells
        self.objective_zone = objective_zone
        self.my_respawn_zone = my_respawn_zone
        self.opp_respawn_zone = opp_respawn_zone

    def is_in_map(self, row, column):
        if (0 <= row < self.row_num and 0 <= column < self.column_num):
            return True
        return False

    def get_cell(self, row, column):
        if 0 <= row < self.row_num and 0 <= column < self.column_num:
            return self.cells[row][column]
        else:
            return None


class World:
    _DEBUGGING_MODE = False
    _LOG_FILELPOINTER = None

    def __init__(self, map, game_constants, ability_constants, hero_constants, my_heroes, opp_heroes,
                 my_dead_heroes, ap, score):
        self.map = map
        self.game_constants = game_constants
        self.ability_constants = ability_constants
        self.hero_constants = hero_constants
        self.my_heroes = my_heroes
        self.opp_heroes = opp_heroes
        self.my_dead_heroes = my_dead_heroes
        self.ap = ap
        self.score = score
        self.heroes = None

    def _handle_init_message(self, msg):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write(str(msg))
            World._LOG_FILE_POINTER.write('\n')
        self.game_constant_init(msg)
        self.map_init(msg)
        self.hero_init(msg)
        self.ability_constants_init(msg)

    def ability_constants_init(self, msg):
        ability_list = msg["abilities"]
        abilities = []
        for dic in ability_list:
            ability_constant = AbilityConstants(dic["name"], self.get_type(dic["type"]), dic["range"], dic["APCost"]
                                                , dic["cooldown"], dic["power"], dic["areaOfEffect"], dic["isLobbing"]
                                                , dic["isPiercing"])  # todo : what is real format
            abilities.__add__(ability_constant)
        self.ability_constants = abilities

    def hero_init(self, msg):
        heroes_list = msg["heroes"]
        heroes = []
        for step, h in enumerate(heroes_list):
            names = []
            for name in h["abilityNames"]:
                names.__add__(name)
            constant = HeroConstants(h["name"], names, h["maxHP"], h["moveAPCost"])
            heroes.__add__(Hero(step, constant, None))
        self.heroes = heroes

    def map_init(self, msg):
        temp_map = msg["map"]
        row_num = temp_map["rowNum"]
        col_num = temp_map["columnNum"]
        cells_map = temp_map["cells"]
        cells = [[0 for _ in range(row_num)] for _ in range(col_num)]
        objective_zone = []
        my_respawn_zone = []
        opp_respawn_zone = []
        for row in range(int(row_num)):
            for col in range(int(col_num)):
                temp_cell = cells_map[row][col]
                c = cells[row][col] = Cell(temp_cell["isWall"], temp_cell["isInMyRespawnZone"],
                                           temp_cell["isInOppRespawnZone"],
                                           temp_cell["isInObjectZone"], False, row, col)
                if c.is_objective_zone:
                    objective_zone.__add__(c)
                if c.is_in_my_respawn_zone:
                    my_respawn_zone.__add__(c)
                if c.is_in_opp_respawn_zone:
                    opp_respawn_zone.__add__(c)
        self.map = Map(row_num, col_num, cells, objective_zone, my_respawn_zone, opp_respawn_zone)

    def game_constant_init(self, msg):
        temp_map = msg["gameConstants"]
        self.game_constants = GameConstants(temp_map["maxAP"], temp_map["timeout"],
                                            temp_map["respawnTime"], temp_map["maxTurn"])

    def get_ability_constants(self, ability_name):
        for a in self.ability_constants:
            if a.name == ability_name:
                return a

    def get_hero_constants(self, hero_name):
        for h in self.hero_constants:
            if hero_name == h.name:
                return h

    def get_hero(self, id):
        for hero in self.my_heroes:
            if hero.id == id:
                return hero
        return None

    def get_my_hero(self, cell):
        for hero in self.my_heroes:
            if hero.current_cell == cell:
                return hero
        return None

    def get_my_hero(self, row, column):
        if not self.map.is_in_map(row, column):
            return None
        for hero in self.my_heroes:
            if hero.current_cell.row == row and hero.current_cell.column == column:
                return hero
        return None

        ability_list = msg["abilities"]
        abilities = []
        for dic in ability_list:
            ability_constant = AbilityConstants(dic["name"], self.get_type(dic["type"]), dic["range"], dic["APCost"]
                                                , dic["cooldown"], dic["power"], dic["areaOfEffect"], dic["isLobbing"]
                                                , dic["isPiercing"])#todo : what is real format
            abilities.__add__(ability_constant)
        self.ability_constants = abilities
    def get_opp_hero(self, cell):
        for hero in self.opp_heroes:
            if hero.current_cell == cell:
                return hero
        return None

    def get_opp_hero(self, row, column):
        if not self.map.is_in_map(row, column):
            return None
        for hero in self.opp_heroes:
            if hero.current_cell.row == row and hero.current_cell.column == column:
                return hero
        return None

    def get_impact_cell(self, ability, start_cell, target_cell):
        if ability.is_lobbing:
            return target_cell
        return self.get_ray_cells(start_cell, target_cell)[-1]  # return the last cell of ray cells

    def get_impact_cells(self, ability_name, start_cell, target_cell):
        ability_constant = self.get_ability_constants(ability_name)
        if ability_constant.is_lobbing:
            return target_cell
        if start_cell.is_wall or start_cell == target_cell:
            return start_cell
        last_cell = None
        rey_cells = self.get_ray_cells(start_cell, start_cell)
        impact_cells = []

        for cell in rey_cells:
            if self.manhattan_distance(cell, start_cell):
                continue
            last_cell = cell
            if self.is_affected(ability_constant, cell):
                impact_cells.__add__(cell)
                if not ability_constant.is_piercing:
                    break
        if not last_cell in impact_cells:
            impact_cells.__add__(last_cell)
        return impact_cells

    def is_affected(self, ability_constant, cell):
        return (self.get_opp_hero(cell) != None and not ability_constant.type == AbilityType.HEAL) or (
                self.get_my_hero(cell) != None and ability_constant.type == AbilityType.HEAL)

    def manhattan_distance(self, start_cell, end_cell):
        import math
        return int(math.fabs(start_cell.row - end_cell.row) + math.fabs(start_cell.column - end_cell.column))

    # todo : with row and colm
    def slope_equation(self, x1, y1, x2, y2, x3, y3):
        return y3 * (x1 - x2) - x3 * (y1 - y2) - (x1 * y2 - y1 * x2)

    def move_hero(self, hero_id, directions):
        pass

    def move_hero(self, hero, directions):
        # self.move_hero(self, hero.id, directions) #todo : different prototype need
        pass

    def calculate_neighbour(self, start, target, current, former):
        if start.row == target.row:
            if start.row != current.row:
                return None
            if start.column > target.column:
                return self.map.get_cell(current.row, current.column - 1)
            else:
                return self.map.get_cell(current.row, current.column + 1)
        if start.column == target.column:
            if start.column != current.column:
                return None
            if start.row > target.row:
                return self.map.get_cell(current.row - 1, current.column)
            else:
                return self.map.get_cell(current.row + 1, current.column)
        options = []
        for delta_row in range(-1, 2):
            for delta_col in range(-1, 2):
                if not self.is_accessible(current.row + delta_row, current.column + delta_col):
                    continue
                possible_next_cell = self.map.get_cell(current.row + delta_row, current.column + delta_col)
                if former == possible_next_cell:
                    continue
                if current == possible_next_cell:
                    continue
                x1 = start.row
                x2 = target.row
                y1 = start.column
                y2 = target.column
                if possible_next_cell.row != current.row and possible_next_cell.column != current.column:
                    x3 = (possible_next_cell.row + current.row) / 2
                    y3 = (possible_next_cell.column + current.column) / 2

                    if self.slope_equation(x1, y1, x2, y2, x3, y3) == 0:
                        if current is not former:
                            return possible_next_cell
                        options += [possible_next_cell]

                x3 = (current.row + possible_next_cell.row) / 2 + (possible_next_cell.column - current.column) / 2
                y3 = (possible_next_cell.column + current.column) / 2 + (possible_next_cell.row - current.row) / 2

                x4 = (current.row + possible_next_cell.row) / 2 - (possible_next_cell.column - current.column) / 2
                y4 = (possible_next_cell.column + current.column) / 2 - (possible_next_cell.row - current.row) / 2

                if self.slope_equation(x1, y1, x2, y2, x3, y3) * self.slope_equation(x1, y1, x2, y2, x4, y4) < 0:
                    if current is not former:
                        return possible_next_cell
                    options += [possible_next_cell]
        for option in options:
            if (start.row <= option.row <= target.row) or (start.row >= option.row >= target.row):
                if (start.column <= option.column <= target.column) or (start.column >= option.column >= target.column):
                    return option

    def get_ray_cells(self, start_cell, end_cell):
        if not self.is_accessible(start_cell.row, start_cell.column):
            return []
        if start_cell == end_cell:
            return [start_cell]
        res = [start_cell]
        former = start_cell
        while res[-1] != end_cell:
            current = res[-1]
            neighbour = self.calculate_neighbour(start_cell, end_cell, current, former)
            if neighbour is None:
                break
            if neighbour.is_wall:
                break
            if neighbour.row != current.row and neighbour.column != current.column:
                if self.map.get_cell(current.row, neighbour.column).is_wall or self.map.get_cell(neighbour.row,
                                                                                                 current.column).is_wall:
                    break
            res += [neighbour]
            former = current
        return res

    def is_in_vision(self, start_cell, end_cell):
        if start_cell == end_cell:
            return True
        if end_cell == self.get_ray_cells(start_cell, end_cell)[-1]:
            return True
        return False

    def is_accessible(self, row, column):
        if 0 <= row < self.map.row_num and 0 <= column < self.map.column_num:
            return not self.map.get_cell(row, column).is_wall
        return False

    def get_next_cell(self, cell, direction):
        if self.is_accessible(cell.row - 1, cell.column) and direction == Direction.UP:
            return self.map.get_cell(cell.row - 1, cell.column)
        if self.is_accessible(cell.row, cell.column - 1) and direction == Direction.LEFT:
            return self.map.get_cell(cell.row, cell.column - 1)
        if self.is_accessible(cell.row + 1, cell.column) and direction == Direction.DOWN:
            return self.map.get_cell(cell.row + 1, cell.column)
        if self.is_accessible(cell.row, cell.column + 1) and direction == Direction.RIGHT:
            return self.map.get_cell(cell.row, cell.column + 1)
        return None

    def get_path_move_directions(self, start_cell, end_cell):
        pass

    def bfs(self):
        pass

    def get_cells_in_aoe(self, cell, area_of_effect):
        cells = []
        for row in range(cell.row - area_of_effect, cell.row + area_of_effect + 1):
            for col in range(cell.column - area_of_effect, cell.column + area_of_effect + 1):
                if not self.map.is_in_map(row, col):
                    continue
                if self.manhattan_distance(cell, self.map.get_cell(row, col)) <= area_of_effect:
                    cells += self.map.get_cell(row, col)
        return cells

    def get_ability_targets(self, ability_name, start_cell, end_cell):
        cells = []
        ability_constant = self.get_ability_constants(ability_name)
        cells = self.get_impact_cells(ability_name, start_cell, end_cell)
        affected_cells = set()
        for cell in cells:
            affected_cells.update(self.get_cells_in_aoe(cell, ability_constant.area_of.effect))
        if ability_constant.type == AbilityType.HEAL:
            return self.get_my_heroes_in_cells(cells)
        return self.get_opp_heroes_in_cells(cells)

    def get_my_heroes_in_cells(self, cells):
        heroes = []
        for cell in cells:
            hero = self.get_my_hero(cell)
            if hero:
                heroes.__add__(hero)
        return heroes

    def get_opp_heroes_in_cells(self, cells):
        heroes = []
        for cell in cells:
            hero = self.get_opp_hero(cell)
            if hero:
                heroes.__add__(hero)
        return heroes


#     void castAbility(int id, Ability ability, Cell targetCell);
#     void moveHero(int id, Direction[] move_directions);
#     void pickHero(HeroName heroName)
class Event:
    EVENT = "event"

    def __init__(self, type, args):
        self.type = type
        self.args = args

    def add_arg(self, arg):
        self.args.append(arg)


class ServerConstants:
    KEY_ARGS = "args"
    KEY_NAME = "name"
    KEY_TYPE = "type"

    CONFIG_KEY_IP = "ip"
    CONFIG_KEY_PORT = "port"
    CONFIG_KEY_TOKEN = "token"

    MESSAGE_TYPE_EVENT = "event"
    MESSAGE_TYPE_INIT = "init"
    MESSAGE_TYPE_SHUTDOWN = "shutdown"
    MESSAGE_TYPE_TURN = "turn"

    CHANGE_TYPE_ADD = "a"
    CHANGE_TYPE_DEL = "d"
    CHANGE_TYPE_MOV = "m"
    CHANGE_TYPE_ALT = "c"
