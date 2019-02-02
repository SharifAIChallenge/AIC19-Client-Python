import copy
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
    def __init__(self, max_ap, timeout, respawn_time, max_turns, kill_score, objective_zone_score, max_score):
        self.max_ap = max_ap
        self.timeout = timeout
        self.respawn_time = respawn_time
        self.max_turns = max_turns
        self.kill_score = kill_score
        self.objective_zone_score = objective_zone_score


class Ability:
    def __init__(self, ability_constants):
        self.ability_constants = ability_constants


class HeroConstants:
    def __init__(self, hero_name, ability_names, max_hp, move_ap_cost):
        self.name = hero_name
        self.ability_names = ability_names
        self.max_hp = max_hp
        self.move_ap_cost = move_ap_cost


class Hero:
    def __init__(self, hero_id, hero_constant, abilities, respawnTime=None, recent_path=None, cooldowns=None):
        self.id = hero_id
        self.abilities = abilities
        self.constants = hero_constant
        self.current_cell = None
        self.recent_path = recent_path
        self.respawnTime = respawnTime
        self.recent_path = recent_path
        self.cooldowns = cooldowns
        self.current_hp = 0

    def __eq__(self, other):
        if type(self) is type(other):
            return self.id == other.id
        return False

    def __hash__(self):
        return self.id


class Cooldown:
    def __init__(self, name, remCooldown):
        self.name = name
        self.remCooldown


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

    def __hash__(self):
        return self.row * 32 + self.column


class Map:
    def __init__(self, row_num, column_num, cells, objective_zone, my_respawn_zone, opp_respawn_zone):
        self.row_num = row_num
        self.column_num = column_num
        self.cells = cells
        self.objective_zone = objective_zone
        self.my_respawn_zone = my_respawn_zone
        self.opp_respawn_zone = opp_respawn_zone

    def is_in_map(self, row, column):
        if 0 <= row < self.row_num and 0 <= column < self.column_num:
            return True
        return False

    def get_cell(self, row, column):
        if 0 <= row < self.row_num and 0 <= column < self.column_num:
            return self.cells[row][column]
        else:
            return None


class Phase(Enum):
    PICK, MOVE, ACTION = range(3)


class CastedAbility:
    def __init__(self, caster_id, targeted_ids, start_cell, end_cell, ability_name):
        self.caster_id = caster_id
        self.targeted_ids = targeted_ids
        self.start_cell = start_cell
        self.end_cell = end_cell
        self.ability_name = ability_name


class World:
    _DEBUGGING_MODE = False
    _LOG_FILELPOINTER = None

    def __init__(self, map=None, game_constants=None, ability_constants=None, hero_constants=None, my_heroes=None,
                 opp_heroes=None, dead_heroes=None, ap=None, score=None, world=None):
        self.map = map
        self.game_constants = game_constants
        self.ability_constants = ability_constants
        self.hero_constants = hero_constants
        self.my_heroes = my_heroes
        self.opp_heroes = opp_heroes
        self.dead_heroes = dead_heroes
        self.ap = ap
        self.heroes = None
        self.my_score = 0
        self.opp_score = 0
        self.current_phase = 'pick'
        self.current_turn = 0
        if world is not None:
            self.game_constants = world.game_constants
            self.hero_constants = world.hero_constants
            self.ability_constants = world.ability_constants
            self.map = world.map
        self.my_casted_ability = []
        self.opp_casted_ability = []

    def _handle_init_message(self, msg):
        if World._DEBUGGING_MODE:
            if World._LOG_FILE_POINTER is None:
                World._LOG_FILE_POINTER = open("client.log", 'w')
            World._LOG_FILE_POINTER.write(str(msg))
            World._LOG_FILE_POINTER.write('\n')
        msg = msg['args'][0]
        self.game_constant_init(msg['gameConstant'])
        self.map_init(msg["map"])
        self.hero_init(msg["heroes"])
        self.ability_constants_init(msg["abilities"])

    def _handle_pick_message(self, msg):
        msg = msg['args'][0]
        my_heroes = msg["myHeroes"]
        opp_heroes = msg["oppHeroes"]
        self.my_heroes = []
        self.opp_heroes = []
        for hero in my_heroes:
            for first_hero in self.heroes:
                if hero["name"] == first_hero.constants.name:
                    my_hero = copy.copy(first_hero)
                    my_hero.id = hero["id"]
                    self.my_heroes.append(my_hero)
        for hero in opp_heroes:
            for first_hero in self.heroes:
                if hero["name"] == first_hero.constants.name:
                    my_hero = copy.copy(first_hero)
                    my_hero.id = hero["id"]
                    self.opp_heroes.append(my_heroes)

    def _handle_turn_message(self, msg):
        msg = msg['args'][0]
        self.my_score = msg["myScore"]
        self.opp_score = msg["oppScore"]
        self.current_phase = self._get_phase(msg["currentPhase"])
        self.current_turn = msg["currentTurn"]
        self._update_map(msg["map"])
        my_heroes = msg["myHeroes"]
        opp_heroes = msg["oppHeroes"]
        self._update_heroes(my_heroes)
        self._update_heroes(opp_heroes)
        self._handle_casted_ability(msg["myCastedAbilities"], "my")
        self._handle_casted_ability(msg["oppCastedAbilities"], "opp")

    def _handle_casted_ability(self, casted_abilities, my_or_opp):
        casted_list = []
        for casted_ability in casted_abilities:
            targeted_list = []
            for target in casted_ability["targetHeroIds"]:
                targeted_list.append(target)
            casted_list.append(CastedAbility(casted_ability["casterId"], targeted_list,
                                             self.map.get_cell(casted_ability["startCell"]["row"],
                                                               casted_ability["startCell"]["column"]),
                                             self.map.get_cell(casted_ability["endCell"]["row"],
                                                               casted_ability["endCell"]["column"]),
                                             casted_ability["abilityName"]))
        if my_or_opp == "my":
            self.my_casted_ability = casted_list
        elif my_or_opp == "opp":
            self.opp_casted_ability = casted_list

    def _update_heroes(self, heroes_list):
        for new_hero in heroes_list:
            id = new_hero["id"]
            hero = self.get_hero(id)
            hero.current_hp = new_hero["currentHP"]
            cooldown_list = []
            cooldowns = new_hero["cooldowns"]
            for cooldown in cooldowns:
                cd = Cooldown(cooldown["name"], cooldown["remCooldown"])
                cooldown_list.append(cd)
            hero.cooldowns = cooldown_list
            hero.current_cell = self.map.get_cell(new_hero["currentCell"]["row"],
                                                  new_hero["currentCell"]["column"])
            recent_path = []
            for recent in new_hero["recentPath"]:
                recent_path.append(self.map.get_cell(recent["row"], recent["column"]))
            hero.recent_path = recent_path
            hero.respawn_time = new_hero["respawnTime"]

    def _update_map(self, cells_map):
        cells = [[0 for _ in range(self.map.row_num)] for _ in range(self.map.column_num)]
        objective_zone = []
        my_respawn_zone = []
        opp_respawn_zone = []
        for row in range(int(self.map.row_num)):
            for col in range(int(self.map.column_num)):
                temp_cell = cells_map[row][col]
                cells[row][col] = Cell(temp_cell["isWall"], temp_cell["isInMyRespawnZone"],
                                       temp_cell["isInOppRespawnZone"],
                                       temp_cell["isInObjectZone"], temp_cell["isInVision"], row, col)

    def ability_constants_init(self, ability_list):

        abilities = []
        for dic in ability_list:
            ability_constant = AbilityConstants(dic["name"], self.get_type(dic["type"]), dic["range"], dic["APCost"]
                                                , dic["cooldown"], dic["power"], dic["areaOfEffect"], dic["isLobbing"]
                                                , dic["isPiercing"])  # todo : what is real format
            abilities.append(ability_constant)
        self.ability_constants = abilities

    @staticmethod
    def _get_phase(param):
        if param == "pick":
            return Phase.PICK
        if param == "move":
            return Phase.MOVE
        else:
            return Phase.ACTION

    def hero_init(self, heroes_list):
        heroes = []
        constants = []
        for step, h in enumerate(heroes_list):
            names = []
            for name in h["abilityNames"]:
                names.append(name)
            constant = HeroConstants(h["name"], names, h["maxHP"], h["moveAPCost"])
            heroes.append(Hero(0, constant, None))
            constants.append(constant)
        self.heroes = heroes
        self.hero_constants = constants

    def map_init(self, map):
        row_num = map["rowNum"]
        col_num = map["columnNum"]
        cells_map = map["cells"]
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
                    objective_zone.append(c)
                if c.is_in_my_respawn_zone:
                    my_respawn_zone.append(c)
                if c.is_in_opp_respawn_zone:
                    opp_respawn_zone.append(c)
        self.map = Map(row_num, col_num, cells, objective_zone, my_respawn_zone, opp_respawn_zone)

    def game_constant_init(self, game_constants):
        self.game_constants = GameConstants(game_constants["maxAP"], game_constants["timeout"],
                                            game_constants["respawnTime"], game_constants["maxTurn"],
                                            game_constants["killScore"]
                                            , game_constants["objectiveZoneScore"], game_constants["maxScore"])

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
        for hero in self.opp_heroes:
            if hero.id == id:
                return hero
        return None

    def get_my_hero(self, cell=None, row=None, column=None):
        if cell is not None and row is None and column is None:
            for hero in self.my_heroes:
                if hero.current_cell == cell:
                    return hero
        elif row is not None and column is not None and cell is None:
            if not self.map.is_in_map(row, column):
                return None
            for hero in self.my_heroes:
                if hero.current_cell.row == row and hero.current_cell.column == column:
                    return hero
        return None

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
            return [target_cell]
        if start_cell.is_wall or start_cell == target_cell:
            return [start_cell]
        last_cell = None
        rey_cells = self.get_ray_cells(start_cell, target_cell)
        impact_cells = []

        for cell in rey_cells:
            if self.manhattan_distance(cell, start_cell) > ability_constant.range:
                continue
            last_cell = cell
            if self.is_affected(ability_constant, cell):
                impact_cells.append(cell)
                if not ability_constant.is_piercing:
                    break
        if last_cell not in impact_cells:
            impact_cells.append(last_cell)
        return impact_cells

    def is_affected(self, ability_constant, cell):
        return (self.get_opp_hero(cell) is not None and not ability_constant.type == AbilityType.HEAL) or (
                self.get_my_hero(cell) is not None and ability_constant.type == AbilityType.HEAL)

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
            if start.row is not current.row:
                return None
            if start.column > target.column:
                return self.map.get_cell(current.row, current.column - 1)
            else:
                return self.map.get_cell(current.row, current.column + 1)
        if start.column == target.column:
            if start.column is not current.column:
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
        if start_cell == end_cell:
            return []
        parents = [[None for _ in range(self.map.column_num)] for _ in range(self.map.row_num)]
        queue = [start_cell]
        visited = [[False for _ in range(self.map.column_num)] for _ in range(self.map.row_num)]
        visited[start_cell.row][start_cell.column] = True
        if self.bfs(parents, visited, queue, end_cell):
            result = []
            parent = parents[end_cell.row][end_cell.column]
            while parent[1] is not start_cell:
                result += [parent[0]]
                current = parent[1]
                parent = parents[current.row][current.column]
        result += [parent[0]]
        return list(reversed(result))

    def bfs(self, parents, visited, queue, target):
        if len(queue) == 0:
            return False
        current = queue[0]
        if current is target:
            return True
        for direction in Direction:
            neighbour = self.get_next_cell(current, direction)
            if neighbour is not None:
                if not visited[neighbour.row][neighbour.column]:
                    queue += [neihgbour]
                    parents[neighbour.row][neighbour.column] = [direction, current]
                    visited[neighbour.row][neighbour.column] = True
        return self.bfs(parents, visited, queue[1:], target)

    def get_cells_in_aoe(self, cell, area_of_effect):
        cells = []
        for row in range(cell.row - area_of_effect, cell.row + area_of_effect + 1):
            for col in range(cell.column - area_of_effect, cell.column + area_of_effect + 1):
                if not self.map.is_in_map(row, col):
                    continue
                if self.manhattan_distance(cell, self.map.get_cell(row, col)) <= area_of_effect:
                    cells.append(self.map.get_cell(row, col))
        return cells

    def get_ability_targets(self, ability_name, start_cell, end_cell):
        cells = []
        ability_constant = self.get_ability_constants(ability_name)
        cells = self.get_impact_cells(ability_name, start_cell, end_cell)
        affected_cells = set()
        for cell in cells:
            affected_cells.update(self.get_cells_in_aoe(cell, ability_constant.area_of_effect))
        if ability_constant.type == AbilityType.HEAL:
            return self.get_my_heroes_in_cells(cells)
        return self.get_opp_heroes_in_cells(cells)

    def get_my_heroes_in_cells(self, cells):
        heroes = []
        for cell in cells:
            hero = self.get_my_hero(cell)
            if hero:
                heroes.append(hero)
                heroes.ap
        return heroes

    def get_opp_heroes_in_cells(self, cells):
        heroes = []
        for cell in cells:
            hero = self.get_opp_hero(cell)
            if hero:
                heroes.append(hero)
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
    MESSAGE_TYPE_PICK = "pick"
    CHANGE_TYPE_ADD = "a"
    CHANGE_TYPE_DEL = "d"
    CHANGE_TYPE_MOV = "m"
    CHANGE_TYPE_ALT = "c"
