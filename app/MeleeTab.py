"""
@file MeleeTab.py
@author Ryan Missel

Handles the logic and state for the PyQT tab related to melee generation
"""
import os
from pathlib import Path

from classes.MeleeWeapon import MeleeWeapon
# from classes.MeleeImage import MeleeImage

from app.tab_utils import add_stat_to_layout
from classes.json_reader import get_file_data

from api.foundryVTT.FoundryTranslator import FoundryTranslator

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5 import QAxContainer, QtCore
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel, QWidget, QPushButton,
                             QCheckBox, QFileDialog, QLineEdit)


class MeleeTab(QWidget):
    def __init__(self, basedir, statusbar, foundry_translator):
        super(MeleeTab, self).__init__()

        # Load classes
        self.basedir = basedir
        self.statusbar = statusbar

        # PDF and Image Classes
        # self.melee_images = MeleeImage(self.basedir)
        # self.melee_pdf = MeleePDF(self.basedir, self.statusbar, self.melee_images)

        # API Classes
        self.foundry_translator = foundry_translator

        ###################################
        ###  BEGIN: Base Stats Grid     ###
        ###################################
        base_stats_group = QGroupBox("Configuration")
        base_stats_layout = QGridLayout()
        base_stats_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Font to share for section headers
        font = QFont("Times", 9, QFont.Bold)
        font.setUnderline(True)

        ##### Information Separator
        information_separator = QLabel("Melee Information")
        information_separator.setFont(font)
        information_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(information_separator, idx, 0, 1, -1)
        idx += 1

        # Melee Name
        self.name_line_edit = add_stat_to_layout(base_stats_layout, "Melee Name:", idx)
        idx += 1

        # Item Level
        base_stats_layout.addWidget(QLabel("Item Level: "), idx, 0)
        self.item_level_box = QComboBox()
        self.item_level_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/gun_types.json").get("pistol").keys():
            self.item_level_box.addItem(item)
        base_stats_layout.addWidget(self.item_level_box, idx, 1)
        idx += 1

        # Guild
        # TODO: swap this out for real guilds
        base_stats_layout.addWidget(QLabel("Guild: "), idx, 0)
        self.guild_type_box = QComboBox()
        self.guild_type_box.addItem("Random")
        for item in get_file_data(basedir + "resources/guns/guild_table.json").keys():
            self.guild_type_box.addItem(item.capitalize())
        base_stats_layout.addWidget(self.guild_type_box, idx, 1)
        idx += 1

        # Rarity
        rarities = ["Random", "Common", "Uncommon", "Rare", "Epic", "Legendary"]
        base_stats_layout.addWidget(QLabel("Rarity: "), idx, 0)
        self.rarity_type_box = QComboBox()
        for item in rarities:
            self.rarity_type_box.addItem(item)
        base_stats_layout.addWidget(self.rarity_type_box, idx, 1)
        idx += 1

        # Prefix: [None, Random, Selection]
        # TODO: swap this out for melee prefixes
        base_stats_layout.addWidget(QLabel("Prefix: "), idx, 0)
        self.prefix_box = QComboBox()
        self.prefix_box.addItem("None")
        self.prefix_box.addItem("Random")
        for pidx, (key, item) in enumerate(get_file_data(basedir + "resources/guns/prefix.json").items()):
            self.prefix_box.addItem(f"[{pidx + 1}] {item['name']}")
        self.prefix_box.setStatusTip("Choose whether to add a random Prefix or a specific one")
        base_stats_layout.addWidget(self.prefix_box, idx, 1)
        idx += 1

        # Redtext Name
        self.redtext_line_edit = add_stat_to_layout(base_stats_layout, "RedText: ", idx)
        self.redtext_line_edit.setStatusTip("")
        idx += 1

        # Redtext Effect
        self.redtext_effect_line_edit = add_stat_to_layout(base_stats_layout, "RedText Effect: ", idx)
        self.redtext_effect_line_edit.setStatusTip("")
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Element Separator
        element_separator = QLabel("Element Selection")
        element_separator.setFont(font)
        element_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(element_separator, idx, 0, 1, -1)
        idx += 1

        # Forcing specific elements to be present
        element_icon_paths = {
            "cryo": "Cryo.png",
            "corrosive": "Corrosion.png",
            "explosive": "Explosive.png",
            "incendiary": "Incendiary.png",
            "radiation": "Radiation.png",
            "shock": "Shock.png"
        }

        # Build a dictionary of button object IDs
        self.element_checkboxes = dict()
        element_buttons = QGridLayout()
        for i, icon in enumerate(element_icon_paths.keys()):
            element_checkbox = QCheckBox()
            element_checkbox.setIcon(QIcon(f"resources/images/element_icons/{element_icon_paths[icon]}"))
            element_checkbox.setStatusTip(f"Choose whether the {icon.title()} element is always added.")

            if i < len(element_icon_paths.keys()) // 2:
                element_buttons.addWidget(element_checkbox, 0, i)
            else:
                element_buttons.addWidget(element_checkbox, 1, i % 3)
            self.element_checkboxes[icon] = element_checkbox

        base_stats_layout.addWidget(QLabel("Select Specific Elements:"), idx, 0, QtCore.Qt.AlignTop)
        base_stats_layout.addLayout(element_buttons, idx, 1, QtCore.Qt.AlignTop)
        idx += 2

        # Setting a custom element damage die
        self.element_damage_die_edit = add_stat_to_layout(base_stats_layout, "Custom Element Damage:", idx, placeholder='e.g. 1d8')
        self.element_damage_die_edit.setStatusTip("Choose a specific damage die (e.g. 1d20) to replace the elemental damage bonus.")
        idx += 1

        # Whether to force an element roll on the table
        element_roll_text_label = QLabel("Force an Element Roll: ")
        element_roll_text_label.setStatusTip(
            "Choose whether to always add an element roll regardless of the rarity rolled. "
            "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(element_roll_text_label, idx, 0)
        self.element_roll = QCheckBox()
        self.element_roll.setStatusTip(
            "Choose whether to always add an element roll regardless of the rarity rolled. "
            "This does NOT guarantee an element, just rolling on the table.")
        base_stats_layout.addWidget(self.element_roll, idx, 1)
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        ##### Art Separator
        art_separator = QLabel("Custom Art Selection")
        art_separator.setFont(font)
        art_separator.setAlignment(QtCore.Qt.AlignCenter)
        base_stats_layout.addWidget(art_separator, idx, 0, 1, -1)
        idx += 1

        # Filepath display for custom art
        self.art_filepath = QLineEdit("")

        # Buttons and file dialog associated with selecting local files
        art_gridlayout = QGridLayout()
        self.art_filedialog = QFileDialog()
        self.art_filedialog.setStatusTip("Uses custom art on the melee art side when given either a local image path or a URL.")

        self.art_select = QPushButton("Open")
        self.art_select.clicked.connect(self.open_file)
        self.art_select.setStatusTip("Used to select an image to use in place of the Borderlands melee art.")

        art_gridlayout.addWidget(self.art_filepath, 0, 1)
        art_gridlayout.addWidget(self.art_select, 0, 2)

        base_stats_layout.addWidget(QLabel("Custom Art File/URL:"), idx, 0)
        base_stats_layout.addLayout(art_gridlayout, idx, 1)
        idx += 1

        # Whether to show rarity-based color splashes behind the melee
        rarity_border_label = QLabel("Use Color Splashes: ")
        rarity_border_label.setStatusTip("Choose whether to outline the melee art in a colored-outline based on rarity.")
        base_stats_layout.addWidget(rarity_border_label, idx, 0)
        self.rarity_border_check = QCheckBox()
        self.rarity_border_check.setStatusTip("Choose whether to outline the melee art in a colored-outline based on rarity.")
        self.rarity_border_check.setChecked(True)
        base_stats_layout.addWidget(self.rarity_border_check, idx, 1)
        idx += 1

        # Add spacing between groups
        base_stats_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Grid layout
        base_stats_group.setLayout(base_stats_layout)
        ###################################
        ###  END: Base Stats Grid       ###
        ###################################

        ###################################
        ###  START: Generation          ###
        ###################################
        generation_group = QGroupBox("Single-Melee Generation")
        generation_layout = QGridLayout()
        generation_layout.setAlignment(Qt.AlignTop)

        # Generate button
        button = QPushButton("Generate Melee")
        button.setStatusTip("Handles generating the melee.")
        button.clicked.connect(lambda: self.generate_melee())
        generation_layout.addWidget(button, 1, 0, 1, -1)

        # Label for savefile output
        self.output_pdf_label = QLabel()
        generation_layout.addWidget(self.output_pdf_label, 2, 0, 1, -1)

        # Grid layout
        generation_group.setLayout(generation_layout)
        ###################################
        ###  END: Generation            ###
        ###################################

        ###################################
        ###  START: Melee Display       ###
        ###################################
        melee_card_group = QGroupBox("Melee Card")
        melee_card_layout = QGridLayout()
        melee_card_layout.setAlignment(Qt.AlignTop)

        # Index counter for gridlayout across all widgets
        idx = 0

        # Pixmap for the MeleeWeapon Image
        self.melee_display = QLabel()
        self.melee_pixmap = QPixmap("resources/images/slamminsalmon.png").scaled(300, 300, Qt.KeepAspectRatio)
        self.melee_display.setAlignment(Qt.AlignCenter)
        self.melee_display.setPixmap(self.melee_pixmap)
        melee_card_layout.addWidget(self.melee_display, idx, 0, 1, -1)
        idx += 1

        # Add spacing between groups
        melee_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Melee Weapon Name
        self.melee_name = add_stat_to_layout(melee_card_layout, "Name: ", idx)
        idx += 1

        # Melee Weapon Item Level
        self.melee_item_level = add_stat_to_layout(melee_card_layout, "Item Level: ", idx)
        idx += 1

        # Melee Weapon Item Level
        self.melee_rarity = add_stat_to_layout(melee_card_layout, "Rarity: ", idx)
        idx += 1

        # Melee Weapon Guild
        self.melee_guild = add_stat_to_layout(melee_card_layout, "Guild: ", idx)
        idx += 1

        # Melee Weapon Guild
        self.melee_guild_effect = add_stat_to_layout(melee_card_layout, "Guild Effect: ", idx)
        idx += 1

        # Add spacing between groups
        melee_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Melee Weapon Prefix
        self.melee_prefix = add_stat_to_layout(melee_card_layout, "Prefix: ", idx)
        idx += 1

        # Melee Weapon RedText
        self.melee_redtext_name = add_stat_to_layout(melee_card_layout, "RedText Name: ", idx)
        idx += 1

        # Melee Weapon Guild
        self.melee_redtext_effect = add_stat_to_layout(melee_card_layout, "RedText Effect: ", idx)
        idx += 1

        # Add spacing between groups
        melee_card_layout.addWidget(QLabel(""), idx, 0)
        idx += 1

        # Build a dictionary of button object IDs
        self.melee_element_checkboxes = dict()
        self.melee_elements = QGridLayout()
        self.melee_elements.setAlignment(Qt.AlignCenter)
        for i, icon in enumerate(element_icon_paths.keys()):
            element_checkbox = QCheckBox()
            element_checkbox.setIcon(QIcon(f"resources/images/element_icons/{element_icon_paths[icon]}"))

            if i < len(element_icon_paths.keys()) // 2:
                self.melee_elements.addWidget(element_checkbox, 0, i)
            else:
                self.melee_elements.addWidget(element_checkbox, 1, i % 3)
            self.melee_element_checkboxes[icon] = element_checkbox

        melee_card_layout.addWidget(QLabel("Elements:"), idx, 0, QtCore.Qt.AlignTop)
        melee_card_layout.addLayout(self.melee_elements, idx, 1, QtCore.Qt.AlignTop)
        idx += 2

        # Melee Weapon Guild
        self.melee_element_damage = add_stat_to_layout(melee_card_layout, "Element Die: ", idx)
        idx += 1

        # Grid layout
        melee_card_group.setLayout(melee_card_layout)
        ###################################
        ###  END: melee Display           ###
        ###################################

        # Setting appropriate column widths
        base_stats_group.setFixedWidth(300)
        generation_group.setFixedWidth(300)
        melee_card_group.setFixedWidth(325)

        # Setting appropriate layout heights
        base_stats_group.setFixedHeight(550)
        generation_group.setFixedHeight(300)
        melee_card_group.setFixedHeight(850)

        # melee Generation Layout
        self.melee_generation_layout = QGridLayout()
        self.melee_generation_layout.setAlignment(Qt.AlignLeft)
        self.melee_generation_layout.addWidget(base_stats_group, 0, 0)
        self.melee_generation_layout.addWidget(generation_group, 1, 0)
        self.melee_generation_layout.addWidget(melee_card_group, 0, 1, -1, 1)

        self.melee_tab = QWidget()
        self.melee_tab.setLayout(self.melee_generation_layout)

    def get_tab(self):
        return self.melee_tab

    def open_file(self):
        """ Handles opening a file for the art path images; if an invalid image then show a message to the statusbar """
        filename = self.art_filedialog.getOpenFileName(self, 'Load File', self.basedir + '/')[0]

        # Error handling for image paths
        if '.png' not in filename and '.jpg' not in filename:
            self.statusbar.showMessage("Filename invalid, select again!", 3000)
        else:
            self.art_filepath.setText(filename)

    def generate_melee(self):
        """ Handles performing the call to generate a melee given the parameters and updating the melee Card image """
        # Load in properties that are currently set in the program
        name = None if self.name_line_edit.text() == "" else self.name_line_edit.text()
        item_level = self.item_level_box.currentText().lower()
        guild = self.guild_type_box.currentText().lower()
        rarity = self.rarity_type_box.currentText().lower()

        element_damage = self.element_damage_die_edit.text()
        element_roll = self.element_roll.isChecked()

        prefix = self.prefix_box.currentText()
        if ']' in prefix:
            prefix = prefix[1:prefix.index("]")]

        color_check = self.rarity_border_check.isChecked()
        art_filepath = self.art_filepath.text()

        # Build list of elements that are manually selected
        selected_elements = []
        for element_key in self.element_checkboxes.keys():
            if self.element_checkboxes[element_key].isChecked():
                selected_elements.append(element_key)

        # Generate the melee object
        self.melee_images = None
        melee = MeleeWeapon(self.basedir, self.melee_images,
                  name=name, item_level=item_level, melee_guild=guild, melee_rarity=rarity,
                  element_damage=element_damage, rarity_element=element_roll, selected_elements=selected_elements,
                  prefix=prefix, melee_art=art_filepath)

        # Assign to card
        self.melee_name.setText(melee.name)
        self.melee_item_level.setText(melee.item_level)
        self.melee_rarity.setText(melee.rarity.title())
        self.melee_guild.setText(melee.guild.title())
        self.melee_guild_effect.setText(melee.guild_mod)

        # TODO: Change this to prefix name and info
        self.melee_prefix.setText(melee.prefix_name)
        self.melee_redtext_name.setText(self.redtext_line_edit.text())
        self.melee_redtext_effect.setText(self.redtext_effect_line_edit.text())

        for element in self.melee_element_checkboxes.keys():
            if element in melee.element:
                self.melee_element_checkboxes[element].setChecked(True)
            else:
                self.melee_element_checkboxes[element].setChecked(False)

        self.melee_element_damage.setText(melee.element_bonus)
