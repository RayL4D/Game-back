# Generated by Django 5.0.6 on 2025-01-13 12:55

from django.db import migrations

def create_tiles_for_map(apps, map_id, grid_size, next_map_portal_tile_coords=None):
    Tile = apps.get_model('api', 'Tile')
    Map = apps.get_model('api', 'Map')
    map = Map.objects.get(pk=map_id)

    # Créer les tuiles
    tiles = {}
    for x in range(grid_size):
        for y in range(grid_size):
            tile = Tile.objects.create(map=map, posX=x, posY=y)
            tiles[(x, y)] = tile
            
          # Set portal if specified and coordinates match
            if next_map_portal_tile_coords and (x, y) == next_map_portal_tile_coords:
                try:
                    next_map = Map.objects.get(pk=map.id + 1)
                    tile.portal_to_map = next_map
                except Map.DoesNotExist:
                    pass  # No next map, so ignore portal

            tile.save()

    # Connecter les tuiles horizontalement et verticalement
    for y in range(grid_size):
        for x in range(grid_size):
            tile = tiles[(x, y)]
            if y < grid_size - 1:
                tile.east_door = tiles[(x, y + 1)]
            if x < grid_size - 1:
                tile.south_door = tiles[(x + 1, y)]
            if y > 0:
                tile.west_door = tiles[(x, y - 1)]
            if x > 0:
                tile.north_door = tiles[(x - 1, y)]
            tile.save()

def add_initial_data(apps, schema_editor):
    Map = apps.get_model('api', 'Map')
    CharacterClass = apps.get_model('api', 'CharacterClass')
    Tile = apps.get_model('api', 'Tile')
    Skill = apps.get_model('api', 'Skill')
    NPC = apps.get_model('api', 'NPC')
    Item = apps.get_model('api', 'Item')
    Shop = apps.get_model('api', 'Shop')
    ShopItem = apps.get_model('api', 'ShopItem')

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

    # Créer des tuiles pour chaque monde
    create_tiles_for_map(apps, map1a.id, 3, next_map_portal_tile_coords=(2, 1))
    create_tiles_for_map(apps, map2a.id, 5, next_map_portal_tile_coords=(4, 0))
    create_tiles_for_map(apps, map3a.id, 10, next_map_portal_tile_coords=(9, 4))
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
        experience=20,
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
        experience=30,
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
        experience=15,
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
        experience=100,
    )

    # Création d'objets
    sword = Item.objects.create(
        name='ITMN_00001',
        item_type='ITMT_00001',
        description='ITMD_00001',
        attack_power = 1,
    )

    potion = Item.objects.create(
        name='ITMN_00002',
        item_type='ITMT_00003',
        description='ITMD_00002',
        healing=10,    
        )

    # Création de magasins
    alchemy_shop = Shop.objects.create(
        name='SHPN_00001',
        tile=Tile.objects.get(map=map1a, posX=0, posY=2),
    )
    ShopItem.objects.create(shop=alchemy_shop, item=potion, price=15)

    equipment_shop = Shop.objects.create(
        name='SHPN_00002',
        tile=Tile.objects.get(map=map2a, posX=1, posY=3),
    )
    armor = Item.objects.create(
        name='ITMN_00003',
        item_type='ITMT_00002',
        description='ITMD_00003',
        defense=10,
    )
    ShopItem.objects.create(shop=equipment_shop, item=armor, price=100)

    food_shop = Shop.objects.create(
        name='SHPN_00003',
        tile=Tile.objects.get(map=map3a, posX=4, posY=2),
    )
    bread = Item.objects.create(
        name='ITMN_00004',
        item_type='ITMT_00004',
        description='ITMD_00004',
        healing=2,
        )
    ShopItem.objects.create(shop=food_shop, item=bread, price=5)

    manuscript_shop = Shop.objects.create(
        name='SHPN_00004',
        tile=Tile.objects.get(map=map4a, posX=2, posY=1),
    )
    scroll = Item.objects.create(
        name='ITMN_00005',
        item_type='ITMT_00007',
        description='ITMD_00005',
        )
    ShopItem.objects.create(shop=manuscript_shop, item=scroll, price=50)

    golden_amulet = Item.objects.create(
        name='ITMN_00006',
        item_type='ITMT_00002',
        description='ITMD_00006',
        
        )

    scroll_of_wisdom = Item.objects.create(
        name='ITMN_00007',
        item_type='ITMT_00007',
        description='ITMD_00007',
        
    )

    dragon_scale_armor = Item.objects.create(
        name='ITMN_00008',
        item_type='ITMT_00002',
        description='ITMD_00008',
        defense=20,
    )
    flameforged_sword = Item.objects.create(
        name='ITMN_00009',
        item_type='ITMT_00001',
        description='ITMD_00009',
        attack_power=10,
    )

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]


