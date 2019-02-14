
import Model
from random import randint


class AI:

    def preprocess(self, world):
        print("preprocess")

    def pick(self, world):
        print("pick")
        hero_names = [hero_name for hero_name in Model.HeroName]
        world.pick_hero(hero_names[randint(0, len(hero_names) - 1)])

    def move(self, world):
        print("move")
        dirs = [direction for direction in Model.Direction]
        for hero in world.my_heroes:
            world.move_hero(hero=hero, direction=dirs[randint(0, len(dirs) - 1)])

    def action(self, world):
        print("action")
        for hero in world.my_heroes:
            row_num = randint(0, world.map.row_num)
            col_num = randint(0, world.map.column_num)
            abilities = hero.abilities
            world.cast_ability(hero=hero, ability=abilities[randint(0, len(abilities) - 1)],
                               cell=world.map.get_cell(row_num, col_num))