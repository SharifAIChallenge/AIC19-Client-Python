from enum import Enum


class AbilityName(Enum):
    SENTRY_ATTACK = "SENTRY_ATTACK"
    SENTRY_DODGE = "SENTRY_DODGE"
    SENTRY_RAY = "SENTRY_RAY"
    BLASTER_ATTACK = "BLASTER_ATTACK"
    BLASTER_DODGE = "BLASTER_DODGE"
    BLASTER_BOMB = "BLASTER_BOMB"
    HEALER_ATTACK = "HEALER_ATTACK"
    HEALER_DODGE = "HEALER_DODGE"
    HEALER_HEAL = "HEALER_HEAL"
    GUARDIAN_ATTACK = "GUARDIAN_ATTACK"
    GUARDIAN_DODGE = "GUARDIAN_DODGE"
    GUARDIAN_FORTIFY = "GUARDIAN_FORTIFY"


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class HeroName(Enum):
    SENTRY = "SENTRY"
    BLASTER = "BLASTER"
    HEALER = "HEALER"
    GUARDIAN = "GUARDIAN"


class AbilityType(Enum):
    DEFENSIVE = "DEFENSIVE"
    DODGE = "DODGE"
    OFFENSIVE = "OFFENSIVE"


class Phase(Enum):
    PICK = "PICK"
    MOVE = "MOVE"
    ACTION = "ACTION"


class AbilityConstants:
    def __init__(self, name, type, range, ap_cost, cooldown, area_of_effect, power, is_lobbing):
        self.name = name
        self.type = type
        self.range = range
        self.ap_cost = ap_cost
        self.cooldown = cooldown
        self.power = power
        self.area_of_effect = area_of_effect
        self.is_lobbing = is_lobbing


class GameConstants:
    def __init__(self, max_ap, preprocess_timeout, first_move_timeout, normal_timeout,
                 max_turns, kill_score, objective_zone_score, max_score):
        self.max_ap = max_ap
        self.preprocess_timeout = preprocess_timeout
        self.first_move_timeout = first_move_timeout
        self.normal_timeout = normal_timeout
        self.max_turns = max_turns
        self.kill_score = kill_score
        self.objective_zone_score = objective_zone_score
        self.max_score = max_score
        if World.DEBUGGING_MODE:
            import datetime
            World.LOG_FILE_POINTER = open('client' + '-' +
                                          datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f") + '.log', 'w+')


class Ability:
    def __init__(self, ability_constants, rem_cooldown):
        self._update_constants(ability_constants)
        self.ability_constants = ability_constants
        self.rem_cooldown = rem_cooldown

    def _update_constants(self, ability_constants):
        self.name = ability_constants.name
        self.type = ability_constants.type
        self.range = ability_constants.range
        self.ap_cost = ability_constants.ap_cost
        self.cooldown = ability_constants.cooldown
        self.power = ability_constants.power
        self.area_of_effect = ability_constants.area_of_effect
        self.is_lobbing = ability_constants.is_lobbing

    def is_ready(self):
        return self.rem_cooldown <= 0

    def __str__(self):
        return 'name:' + self.name + '\trem_cooldown:' + str(self.rem_cooldown)


class HeroConstants:
    def __init__(self, hero_name, ability_names, max_hp, move_ap_cost, respawn_time):
        self.hero_name = hero_name
        self.ability_names = ability_names
        self.max_hp = max_hp
        self.move_ap_cost = move_ap_cost
        self.respawn_time = respawn_time

    @staticmethod
    def _get_ability_name_enum(param):
        for name in AbilityName:
            if name.value == param:
                return name
        return param


class Hero:
    def __init__(self, hero_id, hero_constant, abilities, recent_path=None):
        self.id = hero_id
        self.name = hero_constant.hero_name
        self.ability_names = hero_constant.ability_names
        self.max_hp = hero_constant.max_hp
        self.move_ap_cost = hero_constant.move_ap_cost
        self.respawn_time = hero_constant.respawn_time
        self.current_cell = None
        self.recent_path = recent_path
        self.recent_path = recent_path
        self.current_hp = 0
        self.update_abilities(abilities)

    def update_abilities(self, abilities):
        self.abilities = abilities
        self.defensive_abilities = []
        self.offensive_abilities = []
        self.dodge_abilities = []
        for ability in self.abilities:
            if ability.type == AbilityType.DEFENSIVE:
                self.defensive_abilities += [ability]
            if ability.type == AbilityType.OFFENSIVE:
                self.offensive_abilities += [ability]
            if ability.type == AbilityType.DODGE:
                self.dodge_abilities += [ability]

    def set_constants(self, hero_constant):
        self.name = hero_constant.hero_name
        self.ability_names = hero_constant.ability_names
        self.max_hp = hero_constant.max_hp
        self.move_ap_cost = hero_constant.move_ap_cost
        self.respawn_time = hero_constant.respawn_time

    def get_ability(self, ability_name):
        for ability in self.abilities:
            if ability_name is AbilityName and ability_name.value == ability.name or ability.name == ability_name:
                return ability
        return None

    def __eq__(self, other):
        if other is None:
            return False
        if type(self) is type(other):
            return self.id == other.id
        return False

    def __hash__(self):
        return self.id

    def __str__(self):
        return 'id:' + str(self.id) + '    name:' + self.name


class Cell:
    def __init__(self, row, column, is_wall, is_in_my_respawn_zone, is_in_opp_respawn_zone, is_in_objective_zone,
                 is_in_vision):
        self.is_wall = is_wall
        self.is_in_my_respawn_zone = is_in_my_respawn_zone
        self.is_in_opp_respawn_zone = is_in_opp_respawn_zone
        self.is_in_objective_zone = is_in_objective_zone
        self.is_in_vision = is_in_vision

        self.row = row
        self.column = column

    def __eq__(self, other):
        if other is None:
            return False
        if self.column == other.column and self.row == other.row:
            return True
        return False

    def __hash__(self):
        return self.row * 32 + self.column

    def __str__(self):
        return 'row:' + str(self.row) + '  column:' + str(self.column)


class Map:
    def __init__(self, cells, row_num, column_num, my_respawn_zone, opp_respawn_zone, objective_zone):
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
        if self.is_in_map(row, column):
            return self.cells[row][column]
        elif row == -1 and column == -1:
            return Cell(-1, -1, False, False, False, False, False)
        else:
            return None

    def __str__(self):
        string = ''
        for row in range(self.row_num):
            for col in range(self.column_num):
                string += str(self.get_cell(row, col))
            string += '\n'
        return string


class CastAbility:
    def __init__(self, caster_id, targeted_ids, start_cell, end_cell, ability_name):
        self.caster_id = caster_id
        self.targeted_ids = targeted_ids
        self.start_cell = start_cell
        self.end_cell = end_cell
        self.ability_name = ability_name

    def __str__(self):
        return "caster_id:{},   start_cell:{},  end_cell:{},   ability_name:{}".format(self.caster_id, self.start_cell,
                                                                                       self.end_cell, self.ability_name)


class World:
    DEBUGGING_MODE = False
    LOG_FILE_POINTER = None

    def __init__(self, world=None, queue=None):
        self.heroes = []
        self.my_heroes = []
        self.opp_heroes = []
        self.my_score = 0
        self.ap = 0
        self.opp_score = 0
        self.current_phase = Phase.PICK
        self.current_turn = 0
        self.move_phase_num = -1
        self.my_cast_abilities = []
        self.opp_cast_abilities = []
        if world is not None:
            game_constants = world._get_game_constants()
            self.game_constants = game_constants
            self.max_ap = game_constants.max_ap
            self.max_turns = game_constants.max_turns
            self.kill_score = game_constants.kill_score
            self.objective_zone_score = game_constants.objective_zone_score
            self.max_score = game_constants.max_score
            self.hero_constants = world.hero_constants
            self.ability_constants = world.ability_constants
            self.map = world.map
            self.queue = world.queue
            self.heroes = world.heroes
        else:
            self.queue = queue

    def _get_game_constants(self):
        return self.game_constants

    def get_my_dead_heroes(self):
        dead_heroes = []
        for hero in self.my_heroes:
            if hero.current_hp <= 0:
                dead_heroes += [hero]
        return dead_heroes

    def get_opp_dead_heroes(self):
        dead_memes = []
        for hero in self.opp_heroes:
            if hero.current_hp <= 0:
                dead_memes += [hero]
        return dead_memes

    def _handle_init_message(self, msg):
        if World.DEBUGGING_MODE:
            if World.LOG_FILE_POINTER is not None:
                World.LOG_FILE_POINTER.write(str(msg))
                World.LOG_FILE_POINTER.write('\n')
        msg = msg['args'][0]
        self._game_constant_init(msg['gameConstants'])
        self._map_init(msg["map"])
        self._ability_constants_init(msg["abilityConstants"])
        self._hero_init(msg["heroConstants"])

    def _handle_pick_message(self, msg):
        import copy
        msg = msg['args'][0]
        my_heroes = msg["myHeroes"]
        opp_heroes = msg["oppHeroes"]
        self.current_turn = msg["currentTurn"]
        for hero in my_heroes:
            for first_hero in self.heroes:
                if HeroName[hero["type"]] == first_hero.name:
                    my_hero = copy.copy(first_hero)
                    my_hero.id = hero["id"]
                    my_hero.update_abilities([Ability(self._get_ability_constants(ability_name), 0)
                                              for ability_name in my_hero.ability_names])
                    self.my_heroes.append(my_hero)
        for hero in opp_heroes:
            for first_hero in self.heroes:
                if hero["type"] == first_hero.name:
                    opp_hero = copy.copy(first_hero)
                    opp_hero.id = hero["id"]
                    opp_hero.update_abilities([Ability(self._get_ability_constants(ability_name), 0) for ability_name
                                               in opp_hero.ability_names])
                    self.opp_heroes.append(opp_hero)

    def _handle_turn_message(self, msg):
        msg = msg['args'][0]
        self.my_score = msg["myScore"]
        self.opp_score = msg["oppScore"]
        self.current_phase = Phase[msg["currentPhase"]]
        self.ap = msg["AP"]
        self.current_turn = msg["currentTurn"]
        self._update_map(msg["map"])
        my_heroes = msg["myHeroes"]
        opp_heroes = msg["oppHeroes"]
        self.move_phase_num = msg["movePhaseNum"]
        self._update_heroes(my_heroes, self.my_heroes)
        self._update_heroes(opp_heroes, self.opp_heroes)
        self._handle_cast_ability(msg["myCastAbilities"], "my")
        self._handle_cast_ability(msg["oppCastAbilities"], "opp")

    def _handle_cast_ability(self, cast_abilities, my_or_opp):
        cast_list = []
        for cast_ability in cast_abilities:
            targeted_list = []
            for target in cast_ability["targetHeroIds"]:
                targeted_list.append(target)
            cast_list.append(CastAbility(cast_ability["casterId"], targeted_list,
                                         self.map.get_cell(
                                             cast_ability["startCell"]["row"] if "startCell" in cast_ability else -1,
                                             cast_ability["startCell"][
                                                 "column"] if "startCell" in cast_ability else -1),
                                         self.map.get_cell(
                                             cast_ability["endCell"]["row"] if "endCell" in cast_ability else -1,
                                             cast_ability["endCell"]["column"] if "endCell" in cast_ability else -1),
                                         AbilityName[cast_ability["abilityName"]]))
        if my_or_opp == "my":
            self.my_cast_abilities = cast_list
        elif my_or_opp == "opp":
            self.opp_cast_abilities = cast_list

    def _get_ability_constants(self, name):
        for constant in self.ability_constants:
            if name == constant.name:
                return constant

    def _update_heroes(self, heroes_list, main_hero_list):
        import copy
        for new_hero in heroes_list:
            hero_name = HeroName[new_hero["type"]]
            hero = copy.copy(self._get_hero(hero_name))
            hero.id = new_hero["id"]
            hero.current_hp = new_hero["currentHP"]
            cooldowns = new_hero.get("cooldowns")
            hero.abilities = []
            hero.dodge_abilities = []
            hero.offensive_abilities = []
            hero.defensive_abilities = []
            if cooldowns is not None:
                hero.abilities += [Ability(self._get_ability_constants(AbilityName[cooldown["name"]]),
                                           cooldown["remCooldown"]) for cooldown in cooldowns]
            else:
                hero.abilities += [Ability(self._get_ability_constants(ability_name), -1)
                                   for ability_name in hero.ability_names]

            hero.dodge_abilities += [ability for ability in hero.abilities
                                     if ability.type == AbilityType.DODGE]
            hero.offensive_abilities += [ability for ability in hero.abilities
                                         if ability.type == AbilityType.OFFENSIVE]
            hero.defensive_abilities += [ability for ability in hero.abilities
                                         if ability.type == AbilityType.DEFENSIVE]

            if "currentCell" not in new_hero:
                hero.current_cell = Cell(row=-1, column=-1, is_wall=False, is_in_my_respawn_zone=False,
                                         is_in_opp_respawn_zone=False, is_in_objective_zone=False, is_in_vision=False)
            else:
                hero.current_cell = self.map.get_cell(new_hero["currentCell"]["row"], new_hero["currentCell"]["column"])
            recent_path = []
            for recent in new_hero["recentPath"]:
                recent_path.append(self.map.get_cell(recent["row"], recent["column"]))
            hero.recent_path = recent_path
            hero.respawn_time = new_hero["respawnTime"]
            main_hero_list.append(hero)

    def _update_map(self, cells_map):
        for row in range(int(self.map.row_num)):
            for col in range(int(self.map.column_num)):
                temp_cell = cells_map[row][col]
                self.map.cells[row][col].is_in_vision = temp_cell["isInVision"]

    def _ability_constants_init(self, ability_list):

        abilities = []
        for dic in ability_list:
            ability_constant = AbilityConstants(AbilityName[dic["name"]], AbilityType[dic["type"]], dic["range"],
                                                dic["APCost"], dic["cooldown"], dic["areaOfEffect"], dic["power"],
                                                dic["isLobbing"])
            abilities.append(ability_constant)
        self.ability_constants = abilities

    @staticmethod
    def _get_phase(param):
        if param == "PICK":
            return Phase.PICK
        if param == "MOVE":
            return Phase.MOVE
        else:
            return Phase.ACTION

    def _hero_init(self, heroes_list):
        heroes = []
        constants = []
        for step, h in enumerate(heroes_list):
            names = []
            for name in h["abilityNames"]:
                names.append(AbilityName[name])
            constant = HeroConstants(HeroName[h["name"]], names, h["maxHP"], h["moveAPCost"], h["respawnTime"])
            heroes.append(Hero(0, constant, []))
            constants.append(constant)
        self.heroes = heroes
        self.hero_constants = constants

    def _map_init(self, map):
        row_num = map["rowNum"]
        col_num = map["columnNum"]
        cells_map = map["cells"]
        cells = [[0 for _ in range(col_num)] for _ in range(row_num)]
        objective_zone = []
        my_respawn_zone = []
        opp_respawn_zone = []
        for row in range(int(row_num)):
            for col in range(int(col_num)):
                temp_cell = cells_map[row][col]
                c = Cell(row=row, column=col, is_wall=temp_cell["isWall"],
                         is_in_my_respawn_zone=temp_cell["isInMyRespawnZone"],
                         is_in_opp_respawn_zone=temp_cell["isInOppRespawnZone"],
                         is_in_objective_zone=temp_cell["isInObjectiveZone"], is_in_vision=False)
                cells[row][col] = c
                if c.is_in_objective_zone:
                    objective_zone.append(c)
                if c.is_in_my_respawn_zone:
                    my_respawn_zone.append(c)
                if c.is_in_opp_respawn_zone:
                    opp_respawn_zone.append(c)
        self.map = Map(cells, row_num, col_num, my_respawn_zone, opp_respawn_zone, objective_zone)

    def _game_constant_init(self, game_constants_msg):
        self.game_constants = GameConstants(max_ap=game_constants_msg["maxAP"],
                                            preprocess_timeout=game_constants_msg["preprocessTimeout"],
                                            first_move_timeout=game_constants_msg["firstMoveTimeout"],
                                            normal_timeout=game_constants_msg["normalTimeout"],
                                            max_turns=game_constants_msg["maxTurns"],
                                            kill_score=game_constants_msg["killScore"],
                                            objective_zone_score=game_constants_msg["objectiveZoneScore"],
                                            max_score=game_constants_msg["maxScore"])
        self.max_ap = self.game_constants.max_ap
        self.max_turns = self.game_constants.max_turns
        self.kill_score = self.game_constants.kill_score
        self.objective_zone_score = self.game_constants.objective_zone_score
        self.max_score = self.game_constants.max_score

    def _get_hero(self, hero_type):
        for hero in self.heroes:
            if hero.name == hero_type:
                return hero
        return None

    def get_hero(self, hero_id):
        for hero in self.my_heroes:
            if hero_id == hero.id:
                return hero
        for hero in self.opp_heroes:
            if hero_id == hero.id:
                return hero
        return None

    def get_hero_by_cell(self, allegiance, cell=None, row=None, column=None):
        if cell is not None:
            return self._get_hero_by_cell(allegiance, cell)
        elif row is not None and column is not None:
            if not self.map.is_in_map(row, column):
                return None
            return self._get_hero_by_cell(allegiance, self.map.get_cell(row, column))
        return None

    @staticmethod
    def _get_hero_by_cell(allegiance, cell):
        for hero in allegiance:
            if hero.current_cell == cell:
                return hero

    def _get_my_hero(self, cell=None, row=None, column=None):
        return self.get_hero_by_cell(self.my_heroes, cell, row, column)

    def _get_opp_hero(self, cell=None, row=None, column=None):
        return self.get_hero_by_cell(self.opp_heroes, cell, row, column)

    def get_impact_cell(self, ability=None, ability_name=None, start_cell=None, start_row=None,
                        start_column=None, target_cell=None, target_row=None, target_column=None):
        if ability is None:
            if ability_name is None:
                return None
            ability_constant = self._get_ability_constants(ability_name)
        else:
            ability_constant = ability.ability_constants
        if start_cell is None:
            if start_row is None or start_column is None:
                return None
            start_cell = self.map.get_cell(start_row, start_column)

        if target_cell is None:
            if target_row is None or target_column is None:
                return None
            target_cell = self.map.get_cell(target_row, target_column)
        return self.get_impact_cells(ability_constant, start_cell, target_cell)[-1]

    def get_impact_cells(self, ability_constant, start_cell, target_cell):
        if ability_constant.is_lobbing:
            if self.manhattan_distance(target_cell, start_cell) <= ability_constant.range:
                return [target_cell]
        if start_cell.is_wall or start_cell == target_cell and not ability_constant.is_lobbing:
            return [start_cell]
        last_cell = None
        ray_cells = self.get_ray_cells(start_cell, target_cell)
        impact_cells = []
        for cell in ray_cells:
            if self.manhattan_distance(cell, start_cell) > ability_constant.range:
                continue
            last_cell = cell
            if self.is_affected(ability_constant, cell) or ability_constant.is_lobbing:
                impact_cells.append(cell)
                break
        if last_cell not in impact_cells:
            impact_cells.append(last_cell)
        return impact_cells

    def is_affected(self, ability_constant, cell):
        return (self._get_opp_hero(cell) is not None and ability_constant.type == AbilityType.OFFENSIVE) or (
                self._get_my_hero(cell) is not None and ability_constant.type == AbilityType.DEFENSIVE)

    @staticmethod
    def manhattan_distance(start_cell=None, end_cell=None, start_cell_row=None, start_cell_column=None,
                           end_cell_row=None, end_cell_column=None):
        import math
        if start_cell is not None and end_cell is not None:
            return int(math.fabs(start_cell.row - end_cell.row) + math.fabs(start_cell.column - end_cell.column))
        elif start_cell_column is not None and start_cell_row is not None and end_cell_row is not None and \
                end_cell_column is not None:
            return int(math.fabs(start_cell_row - end_cell_row) + math.fabs(end_cell_column - start_cell_column))
        else:
            return None

    @staticmethod
    def _slope_equation(x1, y1, x2, y2, x3, y3):
        return y3 * (x1 - x2) - x3 * (y1 - y2) - (x1 * y2 - y1 * x2)

    def _calculate_neighbour(self, start, target, current, former):
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

                    if self._slope_equation(x1, y1, x2, y2, x3, y3) == 0:
                        if current is not former:
                            return possible_next_cell
                        options += [possible_next_cell]
                else:
                    x3 = (current.row + possible_next_cell.row) / 2 + (possible_next_cell.column - current.column) / 2
                    y3 = (possible_next_cell.column + current.column) / 2 + (possible_next_cell.row - current.row) / 2

                    x4 = (current.row + possible_next_cell.row) / 2 - (possible_next_cell.column - current.column) / 2
                    y4 = (possible_next_cell.column + current.column) / 2 - (possible_next_cell.row - current.row) / 2

                    if self._slope_equation(x1, y1, x2, y2, x3, y3) * self._slope_equation(x1, y1, x2, y2, x4, y4) < 0:
                        if current is not former:
                            return possible_next_cell
                        options += [possible_next_cell]

        def is_between(first, second, between):
            return (first.row <= between.row <= second.row or first.row >= between.row >= second.row) and \
                   (first.column <= between.column <= second.column or first.column >= between.column >= second.column)

        for option in options:
            if is_between(start, target, option):
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
            neighbour = self._calculate_neighbour(start_cell, end_cell, current, former)
            if neighbour is None:
                break
            if neighbour.is_wall:
                break
            if neighbour.row != current.row and neighbour.column != current.column and (
                    self.map.get_cell(current.row, neighbour.column).is_wall
                    or self.map.get_cell(neighbour.row, current.column).is_wall):
                break
            res += [neighbour]
            former = current
        return res

    def is_in_vision(self, start_cell=None, start_row=None, start_column=None, end_cell=None, end_row=None,
                     end_column=None):
        if start_cell is None:
            if start_column is None or start_row is None:
                return None
            start_cell = self.map.get_cell(start_row, start_column)

        if end_cell is None:
            if end_column is None or end_row is None:
                return None
            end_cell = self.map.get_cell(end_row, end_column)

        if start_cell == end_cell:
            return True
        ray_cells = self.get_ray_cells(start_cell, end_cell)
        if len(ray_cells) > 0 and end_cell == ray_cells[-1]:
            return True
        return False

    def is_accessible(self, row, column):
        if 0 <= row < self.map.row_num and 0 <= column < self.map.column_num:
            return not self.map.get_cell(row, column).is_wall
        return False

    def _get_next_cell(self, cell, direction):
        if self.is_accessible(cell.row - 1, cell.column) and direction == Direction.UP:
            return self.map.get_cell(cell.row - 1, cell.column)
        if self.is_accessible(cell.row, cell.column - 1) and direction == Direction.LEFT:
            return self.map.get_cell(cell.row, cell.column - 1)
        if self.is_accessible(cell.row + 1, cell.column) and direction == Direction.DOWN:
            return self.map.get_cell(cell.row + 1, cell.column)
        if self.is_accessible(cell.row, cell.column + 1) and direction == Direction.RIGHT:
            return self.map.get_cell(cell.row, cell.column + 1)
        return None

    def get_path_move_directions(self, start_cell=None, start_row=None, start_column=None, end_cell=None, end_row=None,
                                 end_column=None, not_pass=None):
        if not_pass is None:
            not_pass = []
        if start_cell is None:
            if start_row is None or start_column is None:
                return None
            start_cell = self.map.get_cell(start_row, start_column)
        if end_cell is None:
            if end_row is None or end_column is None:
                return None
            end_cell = self.map.get_cell(end_row, end_column)
        if start_cell == end_cell:
            return []
        parents = [[None for _ in range(self.map.column_num)] for _ in range(self.map.row_num)]
        queue = [start_cell]
        visited = [[False for _ in range(self.map.column_num)] for _ in range(self.map.row_num)]
        visited[start_cell.row][start_cell.column] = True
        if self._bfs(parents, visited, queue, end_cell, not_pass):
            result = []
            parent = parents[end_cell.row][end_cell.column]
            while parent[1] is not start_cell:
                result += [parent[0]]
                current = parent[1]
                parent = parents[current.row][current.column]
            result += [parent[0]]
            return list(reversed(result))
        return []

    def _bfs(self, parents, visited, queue, target, not_pass):
        if len(queue) == 0:
            return False
        current = queue[0]
        if current is target:
            return True
        for direction in Direction:
            neighbour = self._get_next_cell(current, direction)
            if neighbour is not None and not visited[neighbour.row][neighbour.column] and neighbour not in not_pass:
                queue += [neighbour]
                parents[neighbour.row][neighbour.column] = [direction, current]
                visited[neighbour.row][neighbour.column] = True
        return self._bfs(parents, visited, queue[1:], target, not_pass)

    def get_cells_in_aoe(self, cell, area_of_effect):
        cells = []
        for row in range(cell.row - area_of_effect, cell.row + area_of_effect + 1):
            for col in range(cell.column - area_of_effect, cell.column + area_of_effect + 1):
                if not self.map.is_in_map(row, col):
                    continue
                if self.manhattan_distance(cell, self.map.get_cell(row, col)) <= area_of_effect:
                    cells.append(self.map.get_cell(row, col))
        return cells

    def get_ability_targets(self, ability_name=None, ability=None, ability_constant=None, start_cell=None,
                            start_row=None, start_column=None, target_cell=None, target_row=None, target_column=None):
        if ability_constant is None:
            if ability is None:
                if ability_name is None:
                    return None
                ability_constant = self._get_ability_constants(ability_name)
            else:
                ability_constant = ability.ability_constants
        if start_cell is None:
            if start_row is None or start_column is None:
                return None
            start_cell = self.map.get_cell(start_row, start_column)

        if target_cell is None:
            if target_row is None or target_column is None:
                return None
            target_cell = self.map.get_cell(target_row, target_column)
        cells = self.get_impact_cells(ability_constant, start_cell, target_cell)
        if cells is None or cells is []:
            return []
        affected_cells = set()
        for cell in cells:
            affected_cells.update(self.get_cells_in_aoe(cell, ability_constant.area_of_effect))
        if ability_constant.type == AbilityType.DEFENSIVE:
            return self.get_my_heroes_in_cells(cells)
        return self._get_opp_heroes_in_cells(cells)

    def get_my_heroes_in_cells(self, cells):
        heroes = []
        for cell in cells:
            hero = self._get_my_hero(cell=cell)
            if hero:
                heroes.append(hero)
        return heroes

    def _get_opp_heroes_in_cells(self, cells):
        heroes = []
        for cell in cells:
            hero = self._get_opp_hero(cell)
            if hero:
                heroes.append(hero)
        return heroes

    def cast_ability(self, hero_id=None, hero=None, ability_name=None, ability=None, cell=None, row=None, column=None):
        if World.DEBUGGING_MODE and World.LOG_FILE_POINTER is not None:
            World.LOG_FILE_POINTER.write('-------cast_ability-------\n' + 'hero_id:' + str(hero_id) + '\thero:' +
                                         str(hero) + '\tability_name:' + str(ability_name) + '\nability:' +
                                         str(ability) + '\tcell:' + str(cell) + '\trow:' + str(row) + '\tcolumn:'
                                         + str(column))
        args = []
        if hero_id is not None:
            args += [hero_id]
        elif hero is not None:
            args += [hero.id]

        if ability_name is not None:
            args += [ability_name.value]
        elif ability is not None:
            args += [ability.name.value]

        if cell is not None:
            args += [cell.row, cell.column]
        elif row is not None and column is not None:
            args += [row, column]

        args += [self.current_turn]
        if len(args) == 5:
            self.queue.put(Event('cast', args))

    def move_hero(self, hero_id=None, hero=None, direction=None):
        if World.DEBUGGING_MODE and World.LOG_FILE_POINTER is not None:
            World.LOG_FILE_POINTER.write('\n' + '-------move hero-------\n' + 'hero_id:' + str(hero_id) +
                                         '\thero=' + str(hero) + '\n directions:' + str(direction) + '\n\n')
        if direction is None:
            return
        if hero_id is None and hero is None:
            return
        if hero is not None and hero_id is not None:
            return
        dir_val = direction.value
        if hero_id is not None:
            self.queue.put(Event('move', [hero_id, dir_val, self.current_turn, self.move_phase_num]))
        else:
            self.queue.put(Event('move', [hero.id, dir_val, self.current_turn, self.move_phase_num]))

    def pick_hero(self, hero_name):
        if World.DEBUGGING_MODE and World.LOG_FILE_POINTER is not None:
            World.LOG_FILE_POINTER.write('\n' + '-------pick hero-------' + '\n' + str(hero_name) + '\nturn: ' +
                                         str(self.current_turn) + '\n\n')
        self.queue.put(Event('pick', [hero_name.value, self.current_turn]))

    @staticmethod
    def _get_ability_type(param):
        if param == 'DODGE':
            return AbilityType.DODGE
        if param == 'OFFENSIVE':
            return AbilityType.OFFENSIVE
        if param == 'DEFENSIVE':
            return AbilityType.DEFENSIVE


class Event:
    EVENT = "event‌"

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
    MESSAGE_TYPE_PICK = "pick"
    MESSAGE_TYPE_SHUTDOWN = "shutdown"
    MESSAGE_TYPE_TURN = "turn"

    CHANGE_TYPE_ADD = "a"
    CHANGE_TYPE_DEL = "d"
    CHANGE_TYPE_MOV = "m"
    CHANGE_TYPE_ALT = "c"
