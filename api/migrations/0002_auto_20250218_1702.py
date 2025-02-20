from django.db import migrations

def create_tiles_for_map(apps, map_id, grid_size, next_map_portal_tile_coords=None, portal_destination_coords=None):
    Tile = apps.get_model('api', 'Tile')
    Map = apps.get_model('api', 'Map')
    TileSavedState = apps.get_model('api', 'TileSavedState')  # Import TileSavedState

    map = Map.objects.get(pk=map_id)

    # Créer les tuiles
    tiles = {}
    for x in range(grid_size):
        for y in range(grid_size):
            tile = Tile.objects.create(map=map, posX=x, posY=y)
            tiles[(x, y)] = tile

            # Définir le portail vers la prochaine map
            if next_map_portal_tile_coords and (x, y) == next_map_portal_tile_coords:
                try:
                    next_map = Map.objects.get(pk=map.id + 1)
                    tile.portal_to_map = next_map

                    # Définir la destination sur la prochaine carte
                    if portal_destination_coords:
                        destination_tile = Tile.objects.filter(
                            map=next_map, posX=portal_destination_coords[0], posY=portal_destination_coords[1]
                        ).first()
                        tile.portal_destination_tile = destination_tile

                except Map.DoesNotExist:
                    pass  # Pas de map suivante, donc pas de portail

            tile.save()

    # Connecter les tuiles horizontalement et verticalement
    for y in range(grid_size):
        for x in range(grid_size):
            tile = tiles[(x, y)]
            if y < grid_size - 1:
                tile.east_door_level = max(tile.east_door_level, 1)
                tiles[(x, y + 1)].west_door_level = max(tiles[(x, y + 1)].west_door_level, 1)
            if x < grid_size - 1:
                tile.south_door_level = max(tile.south_door_level, 1)
                tiles[(x + 1, y)].north_door_level = max(tiles[(x + 1, y)].north_door_level, 1)
            if y > 0:
                tile.west_door_level = max(tile.west_door_level, 1)
                tiles[(x, y - 1)].east_door_level = max(tiles[(x, y - 1)].east_door_level, 1)
            if x > 0:
                tile.north_door_level = max(tile.north_door_level, 1)
                tiles[(x - 1, y)].south_door_level = max(tiles[(x - 1, y)].south_door_level, 1)
            tile.save()

def add_initial_data(apps, schema_editor):
    Map = apps.get_model('api', 'Map')
    CharacterClass = apps.get_model('api', 'CharacterClass')
    CharacterInventory = apps.get_model('api', 'CharacterInventory')
    Tile = apps.get_model('api', 'Tile')
    Skill = apps.get_model('api', 'Skill')
    NPC = apps.get_model('api', 'NPC')
    Item = apps.get_model('api', 'Item')
    Dialogue = apps.get_model('api', 'Dialogue')
    Shop = apps.get_model('api', 'Shop')
    ShopItem = apps.get_model('api', 'ShopItem')
    Game = apps.get_model('api', 'Game')
    User = apps.get_model('auth', 'User')
    TileSavedState = apps.get_model('api', 'TileSavedState')  # Import TileSavedState

    # Création de mondes
    map1a = Map.objects.create(name='MAPN_00001', description='MAPD_00001', starting_map=True)
    map2a = Map.objects.create(name='MAPN_00002', description='MAPD_00002')
    map3a = Map.objects.create(name='MAPN_00003', description='MAPD_00003')
    map4a = Map.objects.create(name='MAPN_00004', description='MAPD_00004')

    map1b = Map.objects.create(name='MAPN_00005', description='MAPD_00005', starting_map=True)

    # Création de classes de personnages
    characterclass1 = CharacterClass.objects.create(name='CHARCN_00001', description='CHARCD_00001')
    characterclass2 = CharacterClass.objects.create(name='CHARCN_00002', description='CHARCD_00002')
    characterclass3 = CharacterClass.objects.create(name='CHARCN_00003', description='CHARCD_00003')
    characterclass4 = CharacterClass.objects.create(name='CHARCN_00004', description='CHARCD_00004')
    characterclass5 = CharacterClass.objects.create(name='CHARCN_00005', description='CHARCD_00005')

    # Créer des tuiles pour chaque monde avec portails et destination d'arrivée  
    create_tiles_for_map(apps, map1a.id, 3, next_map_portal_tile_coords=(2, 1), portal_destination_coords=(0, 0))
    create_tiles_for_map(apps, map2a.id, 5, next_map_portal_tile_coords=(4, 0), portal_destination_coords=(2, 2))
    create_tiles_for_map(apps, map3a.id, 10, next_map_portal_tile_coords=(9, 4), portal_destination_coords=(5, 5))
    create_tiles_for_map(apps, map4a.id, 4)

    create_tiles_for_map(apps, map1b.id, 3)

    # Création de compétences
    descriptions = {
        'SKLN_00001': 'SKLD_00001',
        'SKLN_00002': 'SKLD_00002',
        'SKLN_00003': 'SKLD_00003',
        'SKLN_00004': 'SKLD_00004',
        'SKLN_00005': 'SKLD_00005',
        'SKLN_00006': 'SKLD_00006',
        'SKLN_00007': 'SKLD_00007',
        'SKLN_00008': 'SKLD_00008',
        'SKLN_00009': 'SKLD_00009',
        'SKLN_00010': 'SKLD_00010',
    }
    
    for skill_name, skill_description in descriptions.items():
        Skill.objects.create(name=skill_name, description=skill_description)

    # Création de monstres
    npc1 = NPC.objects.create(
        name='NPCN_00001',
        hp=1,
        tile=Tile.objects.get(map=map1a, posX=1, posY=0),
        species='NPCS_00007',
        role='NPCR_00001',
        behaviour='Hostile',
        attack_power=1,
        defense=2,
        experience_reward=20,
    )

    npc2 = NPC.objects.create(
        name='NPCN_00002',
        hp=5,
        tile=Tile.objects.get(map=map1a, posX=2, posY=0),
        species='NPCS_00005',
        role='NPCR_00001',
        behaviour='NPCB_00001',
        attack_power=2,
        defense=1,
        experience_reward=30,
    )

    npc3 = NPC.objects.create(
        name='NPCN_00003',
        hp=3,
        tile=Tile.objects.get(map=map1a, posX=2, posY=1),
        species='NPCS_00009',
        role='NPCR_00001',
        behaviour='NPCB_00001',
        attack_power=1,
        defense=0,
        experience_reward=15,
    )

    npc4 = NPC.objects.create(
        name='NPCN_00004',
        hp=100,
        tile=Tile.objects.get(map=map2a, posX=4, posY=3),
        species='NPCS_00008',
        role='NPCR_00002',
        behaviour='NPCB_00001',
        attack_power=30,
        defense=10,
        experience_reward=100,
    )

    # Épée en bois
    wooden_sword = Item.objects.create(
        name="ITMN_00001",
        type="ITMT_00001",
        description="ITMD_00001",
        attack_power=1,
        bodypart="AB",
        tile=Tile.objects.get(map=map1a, posX=0, posY=0),
    )

    # Casque en bois
    wooden_helmet = Item.objects.create(
        name='ITMN_00002',
        type='ITMT_00002',  # Helmet
        description='ITMD_00002',
        defense=2,
        bodypart="C",
        tile=Tile.objects.get(map=map1a, posX=0, posY=1),
    )

    # Plastron en bois
    wooden_chestplate = Item.objects.create(
        name='ITMN_00003',
        type='ITMT_00003',  # Chestplate
        description='ITMD_00003',
        defense=5,
        bodypart="D",
        tile=Tile.objects.get(map=map1a, posX=2, posY=2),
    )

    # Jambières en bois
    wooden_leggings = Item.objects.create(
        name='ITMN_00004',
        type='ITMT_00004',  # Leggings
        description='ITMD_00004',
        defense=3,
        bodypart="E",
        tile=Tile.objects.get(map=map4a, posX=2, posY=2),
    )

    # Bottes en bois
    wooden_boots = Item.objects.create(
        name='ITMN_00005',
        type='ITMT_00005',  # Boots
        description='ITMD_00005',
        defense=1,
        bodypart="F",
        tile=Tile.objects.get(map=map1a, posX=2, posY=2),
    )

    # Consommable (exemple : potion)
    potion1 = Item.objects.create(
        name='ITMN_00006',
        type='ITMT_00006',  # Consumable
        description='ITMD_00006',
        healing=20,
        tile=Tile.objects.get(map=map2a, posX=2, posY=3),
    )

    # Objet de quête
    scroll1 = Item.objects.create(
        name='ITMN_00007',
        type='ITMT_00007',  # Quest
        description='ITMD_00007',
        tile=Tile.objects.get(map=map2a, posX=4, posY=3),
    )

    # Objet inutilisable (par exemple, un déchet)
    junk1 = Item.objects.create(
        name='ITMN_00008',
        type='ITMT_00008',  # Junk
        description='ITMD_00008',
        tile=Tile.objects.get(map=map2a, posX=1, posY=3),
    )

    # Manuscrit
    manuscript1 = Item.objects.create(
        name='ITMN_00009',
        type='ITMT_00009',  # Manuscript
        description='ITMD_00009',
        tile=Tile.objects.get(map=map2a, posX=0, posY=1),
    )

    # Clé
    key1 = Item.objects.create(
        name='ITMN_00010',
        type='ITMT_00010',  # Key
        description='ITMD_00010',
        tile=Tile.objects.get(map=map1a, posX=2, posY=1),
    )

    # Lance en bois
    wooden_spear = Item.objects.create(
        name='ITMN_00011',
        type='ITMT_00001',  # Weapon
        description='ITMD_00011',
        attack_power=5,
        bodypart="AB",
        tile=Tile.objects.get(map=map1a, posX=0, posY=0),
    )

    # Bouclier en bois
    wooden_shield = Item.objects.create(
        name='ITMN_00012',
        type='ITMT_00001',  # Weapon
        description='ITMD_00012',
        defense=5,
        bodypart="AB",
        tile=Tile.objects.get(map=map1a, posX=0, posY=0),
    )

    # Hache en bois
    wooden_axe = Item.objects.create(
        name='ITMN_00013',
        type='ITMT_00001',  # Weapon
        description='ITMD_00013',
        attack_power=5,
        bodypart="A",
        bodypart_lock = "B",
        tile=Tile.objects.get(map=map1a, posX=0, posY=0),
    )
    
    dialogue1 = Dialogue.objects.create(
        CodeText='DIALT_00001',
        CodeResponse1='2',
        CodeResponse2='3',
        CodeResponse3='4',  
    )
    
    dialogue2 = Dialogue.objects.create(
        CodeText='DIALT_00002',
        CodeResponse1='5', 
    )
    
    dialogue3 = Dialogue.objects.create(
        CodeText='DIALT_00003',
        CodeResponse1='9',  
    )
    
    dialogue4 = Dialogue.objects.create(
        CodeText='DIALT_00004',
        CodeResponse1='13', 
    )
    
    dialogue5 = Dialogue.objects.create(
        CodeText='DIALT_00005',
        CodeResponse1='6',
        CodeResponse2='7',
        CodeResponse3='8',  
    )
    
    dialogue6 = Dialogue.objects.create(
        CodeText='DIALT_00006',
    )
    
    dialogue7 = Dialogue.objects.create(
        CodeText='DIALT_00007',
    )
    
    dialogue8 = Dialogue.objects.create(
        CodeText='DIALT_00008',
    )
    
    dialogue9 = Dialogue.objects.create(
        CodeText='DIALT_00009',
        CodeResponse1='10',
        CodeResponse2='11',
        CodeResponse3='12', 
    )
    
    dialogue10 = Dialogue.objects.create(
        CodeText='DIALT_00010', 
    )
    
    dialogue11 = Dialogue.objects.create(
        CodeText='DIALT_00011',
    )
    
    dialogue12 = Dialogue.objects.create(
        CodeText='DIALT_00012',
    )
    
    dialogue13 = Dialogue.objects.create(
        CodeText='DIALT_00013',
        CodeResponse1='14',
        CodeResponse2='15',
        CodeResponse3='16',  
    )
    
    dialogue14 = Dialogue.objects.create(
        CodeText='DIALT_00014',
    )
    
    dialogue15 = Dialogue.objects.create(
        CodeText='DIALT_00015', 
    )
    
    dialogue16 = Dialogue.objects.create(
        CodeText='DIALT_00016', 
        CodeResponse2='17',
    )
    
    dialogue17 = Dialogue.objects.create(
        CodeText='DIALT_00017',
        Code_action='O',   
    )

    npc5 = NPC.objects.create(
        name='NPCN_00005',
        hp=100,
        tile=Tile.objects.get(map=map1a, posX=2, posY=2),
        species='NPCS_00010',
        role='NPCR_00003',
        behaviour='NPCB_00003',
        attack_power=30,
        defense=10,
        experience_reward=100,
        dialogue=Dialogue.objects.get(id=1),
    )
        
class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]