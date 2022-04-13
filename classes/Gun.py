"""
@file Gun.py
@author Ryan Missel

Class that handles generating and holding the state of a Gun.
Takes in user-input on gun type, gun guild, and item level - if provided.

Unless a gun type is input, then the gun table is only rolled through Gun Table 1-6 on Pg. 81.
"""
from random import randint
from classes.json_reader import get_file_data


class Gun:
    def __init__(self, name=None, item_level=None, gun_type=None, gun_guild=None, gun_rarity=None, prefix=True, redtext=True):
        """
        Handles generating a gun completely from scratch with no user input
        TODO: add user-input modifying the control patch
        """
        # If item level is to be generated
        if item_level in ["random", None]:
            item_level = self.get_random_ilevel()

        # Roll for a random name
        if name in ['random', None]:
            roll_name_len = randint(1, 2)
            name_table = get_file_data('guns/lexicon.json')
            number_names = len(name_table.keys()) - 1
            names = [name_table.get(str(randint(1, number_names))) for _ in range(roll_name_len)]
            self.name = ''.join(names)

        # Get relevant portion of the gun table based on the roll
        roll_type = str(randint(1, 6))
        roll_guild = str(randint(1, 6))
        gun_table = get_file_data("guns/gun_table.json").get(roll_type)

        # Get gun type and gun guild
        self.type = gun_table.get("type")
        self.item_level = item_level

        self.guild = gun_table.get("guild").get(roll_guild)
        self.guild_table = get_file_data("guns/guild_table.json").get(self.guild)
        self.guild_element_roll = self.guild_table.get("element_roll")

        # Get gun stats table
        self.stats = get_file_data("guns/" + self.type + ".json").get(item_level)
        self.accuracy = self.stats['accuracy']
        self.range = self.stats['range']
        self.damage = self.stats['damage']

        # Roll for gun rarity
        roll_row = str(randint(1, 4))
        roll_col = str(randint(1, 6))
        self.rarity = get_file_data("guns/rarity_table.json").get(str(roll_row)).get(roll_col)

        # Check if it was an elemental roll and if it can have an element based on guild type
        self.rarity_element_roll = False
        if type(self.rarity) is list:
            self.rarity_element_roll = True
            self.rarity = self.rarity[0]

        # Get guild information
        self.guild_mod = self.guild_table.get("tiers").get(self.rarity)
        self.guild_info = self.guild_table.get("gun_info")

        # Roll for element iff it has an appropriate guild and rarity
        self.element = None
        if self.guild_element_roll is True and self.rarity_element_roll is True:
            roll_element = str(randint(1, 100))
            roll_element = self.check_element_boost(roll_element, self.guild, self.rarity)

            element_table = get_file_data("elements/elemental_table.json")
            self.element = element_table.get(self.get_element_tier(roll_element, element_table)).get(self.rarity)

        # If the gun is Malefactor guild and it does not have an element yet, keep rolling until an element is picked
        if self.guild == "malefactor" and self.element is None:
            while self.element is None:
                roll_element = str(randint(1, 100))
                roll_element = self.check_element_boost(roll_element, self.guild, self.rarity)

                element_table = get_file_data("elements/elemental_table.json")
                self.element = element_table.get(self.get_element_tier(roll_element, element_table)).get(self.rarity)

        # Get element info if it exists
        self.element_info = None
        if self.element is not None:
            if type(self.element) == str:
                element = self.element.split(' ')[0]   # make sure to remove bonuses when parsing
                self.element_info = get_file_data("elements/elemental_type.json").get(element)

            if type(self.element) == list:
                self.element_info = [
                    get_file_data("elements/elemental_type.json").get(self.element[0]),
                    get_file_data("elements/elemental_type.json").get(self.element[1])
                ]

        # If prefix addition is checked, roll for a prefix and append to the gun's name
        if prefix is True:
            roll_prefix = str(randint(1, 100))
            prefix_table = get_file_data("guns/prefix.json").get(roll_prefix)
            self.prefix_name = prefix_table['name']
            self.prefix_info = prefix_table['info']
            self.name = self.prefix_name + ' ' + self.name

        # If redtext checked and the gun is epic or legendary, roll for it
        self.redtext_name = None
        self.redtext_info = None
        if redtext is True and self.rarity in ['epic', 'legendary']:
            roll_redtext = str(randint(1, 100))
            redtext_table = get_file_data('guns/redtext.json')
            redtext_item = redtext_table.get(self.get_redtext_tier(roll_redtext, redtext_table))
            self.redtext_name = redtext_item['name']
            self.redtext_info = redtext_item['info']

    def get_random_ilevel(self):
        """ Handles rolling for a random item level and giving back the tier key for it """
        roll_level = randint(1, 30)

        tier = None
        for key in get_file_data("guns/pistol.json").keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll_level <= upper:
                tier = key

        return tier

    def check_element_boost(self, roll, guild, rarity):
        """
        Malefactor weapons get a boost to their element roll on the table.
        Checks if the given rolled gun gets that treatment.
        :param roll: given base element roll
        :param guild: guild to check if its malefactor
        :param rarity: rarity of the gun
        :return: roll with modified cost if its malefactor and rare enough
        """
        roll = int(roll)

        if rarity == "rare" and guild == "malefactor":
            roll = roll + int(roll * 0.10)
        elif rarity == "epic" and guild == "malefactor":
            roll = roll + int(roll * 0.15)
        elif rarity == "legendary" and guild == "malefactor":
            roll = roll + int(roll * 0.20)

        roll = min(roll, 100)
        return str(roll)

    def get_element_tier(self, roll, element_table):
        """
        Handles getting the tier in which the element roll resides.
        The tiers are non-uniform and range-based in JSON, so this is an easy solution.
        :param roll: 1-100 random roll
        :param element_table: loaded in dictionary of elemental_table.json
        :return: JSON key of the tier rolled
        """
        roll = int(roll)

        tier = None
        for key in element_table.keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll <= upper:
                tier = key

        return tier

    def get_redtext_tier(self, roll, redtext_table):
        """
        Handles getting the tier of redtext in which the given roll resides
        The tiers are non-uniform and range-based in JSON, so this is an easy solution.
        :param roll: 1-100 random roll
        :param redtext_table: loaded in dictionary of redtext.json
        :return: JSON key of the tier rolled
        """
        roll = int(roll)

        tier = None
        for key in redtext_table.keys():
            lower, upper = [int(i) for i in key.split('-')]
            if lower <= roll <= upper:
                tier = key

        return tier

    def __str__(self):
        """ Outputs a formatted block of the Guns' stats and what checks where made for elemental rolls """
        return  "Name: {}\n"\
                "Type: {}\n"\
                "Guild: {}\n" \
                "Rarity: {}\n" \
                "Item Level: {}\n"\
                "---\n"\
                "Damage: {}\n"\
                "Range: {}\n"\
                "Accuracy: {}\n"\
                "---\n"\
                "Guild Mod: {}\n"\
                "Guild Info:\n{}\n"\
                "---\n"\
                "Element Guild Check: {}\n"\
                "Element Rarity Check: {}\n"\
                "Element: {}\n"\
                "Element Info:\n{}\n"\
                "---\n"\
                "Prefix: {}\n"\
                "Prefix Info: {}\n"\
                "---\n"\
                "RedText: {}\n"\
                "RedText Info: {}\n".format(
            self.name, self.type, self.guild, self.rarity, self.item_level,
            self.damage, self.range, self.accuracy,
            self.guild, self.guild_info,
            self.guild_element_roll, self.rarity_element_roll, self.element, self.element_info,
            self.prefix_name, self.prefix_info,
            self.redtext_name, self.redtext_info)
