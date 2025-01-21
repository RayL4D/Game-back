#graphGEFXServer/api/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User  # Import User model for potential user accounts
from django.utils import timezone
import datetime 
import json

# Create your models here.
    
class Map(models.Model):  # Added model for Map
    name = models.CharField(max_length=255, unique=True)  # Ensure unique map names
    description = models.TextField(blank=True)  # Optional map description
    starting_map = models.BooleanField(default=False)  # Flag to indicate the starting map

    def get_image_path(self):
        return f'/img/Map/map{self.id}.png'


class Tile(models.Model):
    map= models.ForeignKey(Map, on_delete=models.CASCADE, null=True, blank=True)
    posX = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    posY = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    visited = models.BooleanField(default=False)  # Flag to track if the tile has been visited
    north_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='north_connected_tile')
    south_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='south_connected_tile')
    east_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='east_connected_tile')
    west_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='west_connected_tile')
    portal_to_map = models.ForeignKey(Map, on_delete=models.SET_NULL, null=True, blank=True, related_name='portal_tiles') # Add this field    
  
    
    # Méthode pour changer de monde
    def change_map(self, game):
        if self.portal_to_map:
            game.map = self.portal_to_map
            game.save()

    
class CharacterClass(models.Model):  # New model for character classes
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    def get_image_path(self):
        # Construit le chemin de l'image en fonction de la classe du personnage
        class_image_filename = {
            'CHARCN_00001': 'Warrior1.png',
            'CHARCN_00002': 'Mage1.png',
            'CHARCN_00005': 'Priest1.png',
            'CHARCN_00003': 'Hunter1.png',
            'CHARCN_00004': 'Rogue1.png',

            # ... autres correspondances de classes et d'images ...
        }
        return f'/img/Classes/{class_image_filename.get(self.name, "default.png")}'

class Item(models.Model):
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=255, choices=[
        ('ITMT_00001', 'ITMT_00001'),
        ('ITMT_00002', 'ITMT_00002'),
        ('ITMT_00003', 'ITMT_00003'),
        ('ITMT_00004', 'ITMT_00004'),
        ('ITMT_00005', 'ITMT_00005'),
        ('ITMT_00006', 'ITMT_00006'),
        ('ITMT_00007', 'ITMT_00007'),
        ('ITMT_00008', 'ITMT_00008'),
        ('ITMT_00009', 'ITMT_00009'),
        ])
    is_equipped = models.BooleanField(default=False)
    description = models.TextField(blank=True)  # Optional item description
    attack_power = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Puissance d'attaque de l'arme
    defense = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Valeur de défense de l'armure
    healing = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Valeur de soin de la potion

    def get_image_path(self):
        return f'/img/Items/item{self.id}.png'
class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional foreign key to User model
    name = models.CharField(max_length=255)
    map = models.ForeignKey(Map, on_delete=models.SET_NULL, null=True)
    character_class = models.ForeignKey(CharacterClass, on_delete=models.SET_NULL, null=True)  # Dynamic class
    attack_power = models.PositiveIntegerField(default=1)
    defense = models.PositiveIntegerField(default=1)
    hp = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])  # Minimum HP is 1
    experience = models.PositiveIntegerField(default=0)  # Expérience pour monter de niveau
    level = models.PositiveIntegerField(default=1)  # Niveau du personnage

    current_tile = models.ForeignKey('Tile', on_delete=models.SET_NULL, null=True, related_name='game') 
    inventory = models.ManyToManyField('Item', through='CharacterInventory', through_fields=('game', 'item'))    
    skills = models.ManyToManyField('Skill', through='CharacterSkill')
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)  # Date de la dernière mise à jour
    


    def save_game_state(self):
        # Serialize character data and store it in the session
        session = Session.objects.get_or_create(expire_date=timezone.now() + datetime.timedelta(days=1))[0]  # Create or get session
        self.session_key = session
        game_data = {
            'name': self.name,
            'current_tile': self.current_tile.id if self.current_tile else None,
            'inventory': [item.id for item in self.characterinventory_set.all()],  # Get inventory item IDs
        }
        session.session_data['game_data'] = json.dumps(game_data)  # Serialize data to JSON
        session.save()
        self.save()  # Save character with updated session key

    def load_game_state(self):
        # Check if a session exists with character data
        session = self.session_key
        if session and 'game_data' in session.session_data:
            game_data = json.loads(session.session_data['game_data'])
            self.current_tile = Tile.objects.get(pk=game_data['current_tile']) if game_data['current_tile'] else None
            # Load inventory items based on retrieved IDs (consider using bulk operations for efficiency)
            self.characterinventory_set.clear()  # Clear existing inventory before loading
            for item_id in game_data['inventory']:
                item = Item.objects.get(pk=item_id)
                CharacterInventory.objects.create(game=self, item=item)
        else:
            print("No saved game state found")

    def save(self, *args, **kwargs):
        # Limiter le nombre de sauvegardes à 5 par utilisateur
        existing_saves = Game.objects.filter(user=self.user).count()
        if existing_saves >= 5 and self.pk is None:  # self.pk is None signifie que c'est une nouvelle sauvegarde
            raise ValueError("Maximum number of saves reached (5)")
        super().save(*args, **kwargs)

    def save_from_game(self, game):
        self.current_tile = game.current_tile
        self.inventory_data = json.dumps([  # Serialize inventory item IDs
            item.id for item in game.characterinventory_set.all()
        ])
        self.save()

    def equip_starting_gear(self):
        starting_weapon = Item.objects.filter(name="ITMN_00001").first()
        if starting_weapon:
            self.primary_weapon = starting_weapon
            self.save()


    def assign_class_skills(self):
        print("Assigning skills for class:", self.character_class.name)  # Vérification du nom de la classe

        class_skills = {
            "CHARCN_00001": ["SKLN_00001", "SKLN_00002"],
            "CHARCN_00002": ["SKLN_00003", "SKLN_00004"],
            "CHARCN_00004": ["SKLN_00005", "SKLN_00006"],
            "CHARCN_00003": ["SKLN_00007", "SKLN_00008"],
            "CHARCN_00005": ["SKLN_00009", "SKLN_00010"],
        }
    
    # Vérification si la classe existe dans le dictionnaire
        if self.character_class.name not in class_skills:
            print(f"No skills defined for class '{self.character_class.name}'")
            return  # Quitter la méthode si aucune compétence n'est définie pour la classe

        for skill_name in class_skills.get(self.character_class.name, []):
            try:
                skill = Skill.objects.get(name=skill_name)
                print("Adding skill:", skill_name)
                self.skills.add(skill)
            except Skill.DoesNotExist:
                print(f"Skill '{skill_name}' does not exist in the database.")



    def save(self, *args, **kwargs):
        creating = not self.pk  # Check if the character is being created
        if creating:
            # Set default values for new characters
            self.map = Map.objects.first()  # Set the starting map
            self.current_tile = Tile.objects.filter(link_map=self.map).first()
            self.hp = self.get_default_hp()  # Set HP based on character class
            self.attack_power = self.get_default_attack_power()
            self.defense = self.get_default_defense()

        super().save(*args, **kwargs)  # Call the parent class's save method

        if creating:
            self.equip_starting_gear()  # Equip starting gear
            self.assign_class_skills()  # Assign class skills

        # Vérifier si le personnage est mort après la contre-attaque
        if self.hp <= 0:
            self.respawn()  # Appeler une méthode pour gérer la réapparition

    def respawn(self):
        # Logique de réapparition
        self.hp = self.get_default_hp()  # Réinitialiser les HP 
        self.current_tile = Tile.objects.filter(link_map=self.map).first()
        self.save()
        # Vous pouvez également réinitialiser d'autres aspects du personnage ici si nécessaire

    def get_default_hp(self):
        # Define default HP based on character class
        class_hp = {
            'CHARCN_00001': 20,
            'CHARCN_00002': 12,
            'CHARCN_00005': 15,
            'CHARCN_00003': 18,
            'CHARCN_00004': 16,
        }
        return class_hp.get(self.character_class.name, 10)  # Utiliser self.character_class.name
    
    def get_default_attack_power(self):
        # Renvoie la puissance d'attaque par défaut en fonction de la classe du personnage.
        class_stats = {
            'CHARCN_00001': 12,  # Puissance d'attaque élevée pour les guerriers
            'CHARCN_00002': 8,     # Puissance d'attaque moyenne pour les mages
            'CHARCN_00005': 6,     # Faible puissance d'attaque pour les prêtres
            'CHARCN_00003': 10,    # Bonne puissance d'attaque pour les chasseurs
            'CHARCN_00004': 9,     # Bonne puissance d'attaque pour les rôdeurs
        }
        return class_stats.get(self.character_class.name, 1)
    
    def get_default_defense(self):
        # Renvoie la défense par défaut en fonction de la classe du personnage.
        class_stats = {
            'CHARCN_00001': 8,     # Bonne défense pour les guerriers
            'CHARCN_00002': 4,     # Faible défense pour les mages
            'CHARCN_00005': 6,     # Défense moyenne pour les prêtres
            'CHARCN_00003': 5,     # Défense moyenne pour les chasseurs
            'CHARCN_00004': 7,     # Bonne défense pour les rôdeurs
        }
        return class_stats.get(self.character_class.name, 1)
    
    def equip_weapon(self, item):
        if not item or not isinstance(item, Item):
            return

        if item.item_type != 'Weapon':
            print(f"Cannot equip {item.name} as a weapon (wrong item type)")
            return

        # Unequip current weapon if necessary
        if self.primary_weapon:
            self.primary_weapon = None
        elif self.secondary_weapon:
            self.secondary_weapon = None

        # Equip the new weapon (check for empty slot)
        if not self.primary_weapon:
            self.primary_weapon = item
        elif not self.secondary_weapon:
            self.secondary_weapon = item
        self.save()

        # Update equipped flag in CharacterInventory (if applicable)
        if hasattr(self, 'characterinventory_set'):
            for entry in self.characterinventory_set.filter(item=item):
                entry.is_equipped = True
                entry.save()

class Skill(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # Optional skill description
    power = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Puissance d'attaque de la compétence
    def get_image_path(self):
        return f'/img/Skills/skill{self.id}.png'

    def generate_description(self):
        # Example: Generate a description based on the skill name
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
        return descriptions.get(self.name, '')  # Return the description or an empty string if not found
    
    
class CharacterSkill(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)  # Niveau de compétence
    # Add fields for skill level, effects, etc. (optional)


class CharacterInventory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_equipped = models.BooleanField(default=False)
    primary_weapon = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_primary_weapon')
    secondary_weapon = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_secondary_weapon')
    
class NPC(models.Model):
    name = models.CharField(max_length=255)
    hp = models.PositiveIntegerField(default=1)  # Monsters should have at least 1 HP
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    is_dead = models.BooleanField(default=False)
    species = models.CharField(max_length=255, choices=[
        ('NPCS_00001', 'NPCS_00001'),
        ('NPCS_00002', 'NPCS_00002'),
        ('NPCS_00003', 'NPCS_00003'),
        ('NPCS_00004', 'NPCS_00004'),
        ('NPCS_00005', 'NPCS_00005'),
        ('NPCS_00006', 'NPCS_00006'),
        ('NPCS_00007', 'NPCS_00007'),
        ('NPCS_00008', 'NPCS_00008'),
        ('NPCS_00009', 'NPCS_00009'),
    ])
    role = models.CharField(max_length=255)
    behaviour = models.CharField(max_length=255, choices=[
        ('NPCB_00002', 'NPCB_00002'),
        ('NPCB_00003', 'NPCB_00003'),
        ('NPCB_00001', 'NPCB_00001'),
    ])
    attack_power = models.PositiveIntegerField(default=1)
    defense = models.PositiveIntegerField(default=1)
    experience = models.PositiveIntegerField(default=10)  # Exemple de valeur d'expérience


    def get_image_path(self):
        return f'assets/images/monsters/monster{self.id}.png'
    # Add fields for monster defense, special abilities, loot drops, etc. (optional)

class Dialogue(models.Model):
    text = models.TextField()
    NPC = models.ForeignKey(NPC, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    def get_image_path(self):
        return f'assets/images/dialogues/dialogue{self.id}.png'

class Shop(models.Model):
    name = models.CharField(max_length=255)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    inventory = models.ManyToManyField(Item, through='ShopItem')
    def get_image_path(self):
        return f'assets/images/shops/shop{self.id}.png'

class ShopItem(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)  # Price of the item in the shop


class TileSavedState(models.Model):
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    visited = models.BooleanField(default=False)

class NPCSavedState(models.Model):
    npc = models.ForeignKey(NPC, on_delete=models.CASCADE)
    hp = models.IntegerField()
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    behaviour = models.CharField(max_length=255, choices=[
        ('NPCB_00002', 'NPCB_00002'),
        ('NPCB_00003', 'NPCB_00003'),
        ('NPCB_00001', 'NPCB_00001'),
    ])
    is_dead = models.BooleanField(default=False)
