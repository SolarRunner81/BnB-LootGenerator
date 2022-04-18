<p align="center"><img src="https://user-images.githubusercontent.com/32918812/163755438-a98ff76f-7ce8-4ff5-978d-a4a3ef8b138e.png" /></p>

<hr>

LootGenerator is a local- and (soon-to-be) web-based application to handle Gun and Lootsplosion generation in the Nerdvana TTRPG, <a href="https://nerdvanagames.myshopify.com/">Bunkers & Badasses</a>. Additionally, it includes transcribed roll tables from the source book for all item types in the game.
 
## Running:
There are two ways to use LootGenerator, either through the local application or by using the web application <a href=''>TBD URL NAME</a>. 

The local option is a PyQT GUI application in which the user can specify specific gun attributes to roll with. 
This will save a local PDF that can be printed off or sent to players.
![Screenshot 2022-04-17 184044](https://user-images.githubusercontent.com/32918812/163734919-97850aab-4466-44ee-be26-a2f4eaba70ba.png)


## Folder Layout:
```
  BnB-LootGenerator/
  │
  ├── app.py            - Main entrypoint for the web application
  ├── Dockerfile        - Enables localized container starting
  ├── requirements      - Automatically installs needed pypi packages
  ├── generate_gun_cmd  - Local generation of a Gun Card PDF via command line
  |
  ├── classes/
  │   ├── Gun.py     - Gun generation script
  ├── resources/
  │   ├── chests/    - Tables for chests, caches, etc
  │   ├── elements/  - Tables for element rolling
  │   ├── guilds/    - Tables for guild mod tables
  │   ├── images/    - Tables that have URL PNG links to gun art from all Borderland games
  │   ├── misc/      - Currently holds placeholder folders for planned features (grenades, moxxtails, etc)
  ├── tests/
```
  
## Custom Additions:
LootGenerator allows for easily adding customized rules/mods to expand the generation options. As the generation script dynamically parses
the JSON files on runtime, one just needs to add a new item to the relevant JSON file in the resources/ folder.

#### Available custom parts include:
<ul>
    <li>Elements (Type/Rolling Tiers)</li>
    <li>Guilds</li>
    <li>Gun Types</li>
    <li>Gun Prefixes</li>
    <li>Gun Images</li>
    <li>Red Text Mod</li>
</ul>

#### Instructions for adding:
For example, to add a new Guild, add a new JSON item to the "resources/guild.json" file in line to the
attributes of the others.

Adding an item to the JSON:

![adding_to_json](https://user-images.githubusercontent.com/32918812/163227008-68b1253e-3fa5-4602-bc8d-35cf4c4bfb91.png)

## TO-DO:
There are still a number of features in the works of being implemented. This includes the primary goal of outputting full loot generation tables
for encounters given a Badass Rank or type of Container (cache, disk chest, etc).

These are the components to be fleshed out yet (we're welcome to take contributions for these!):
<ul>
      <li><b> Grenades</b>: Roll tables for grenades and grenade effects and class.</li>
      <li><b> Potions</b>: Roll tables for regular n' Tina potions and class needed.</li>
      <li><b> Moxx-Tails</b>: Roll tables and class needed.</li>
      <li><b> Relic</b>: Roll tables for guild n' effects and class needed.</li>
      <li><b> Shield</b>: Roll tables for guild n' effects and class needed.</li>
      <li><b> Containers</b>: Roll tables for cache, cache size, dice chests, and unassuming chests need to be input. As well, a class that handles rolling and providing function calls to relevant classes is needed.</li>
</ul>


## Issues and Contributions
Please feel free to put up any issues that are found or enhancements that would improve this work. As well, please feel welcome to put up PRs for any improvements that you can do!

## Credit
This tool is an unofficial automated tool for the Nerdvana TTRPG, <a href="https://nerdvanagames.myshopify.com/">Bunkers & Badasses</a>.

Gun art images are used from the Borderlands <a href="https://www.lootlemon.com/db/borderlands-3/weapons">Lootlemon</a> and images displayed are URL links to their hosted images.

All credit for source material and gun images belongs to Nerdvana and GearBox Software.
