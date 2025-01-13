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
    # Add fields for items in the tile (consider a separate model for items in tiles)
  
    
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
            'Warrior': 'Warrior1.png',
            'Mage': 'Mage1.png',
            'Priest': 'Priest1.png',
            'Hunter': 'Hunter1.png',
            'Rogue': 'Rogue1.png',

            # ... autres correspondances de classes et d'images ...
        }
        return f'/img/Classes/{class_image_filename.get(self.name, "default.png")}'

class Item(models.Model):
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=255, choices=[
        ('Weapon', 'Weapon'),
        ('Armor', 'Armor'),
        ('Potion', 'Potion'),
        ('Consumable', 'Consumable'),
        ('Quest', 'Quest'),
        ('Junk', 'Junk'),
        ('Manuscript', 'Manuscript'),
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Bronze', 'Bronze'),
        ])
    is_equipped = models.BooleanField(default=False)
    description = models.TextField(blank=True)  # Optional item description
    stats = models.JSONField(blank=True)  # Optional field for numerical stats (damage, armor, etc.)
    damage = models.PositiveIntegerField(default=0)  # Dégâts supplémentaires de l'arme
    armor = models.PositiveIntegerField(default=0)

    def get_image_path(self):
        return f'/img/Items/item{self.id}.png'
class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional foreign key to User model
    name = models.CharField(max_length=255)
    Map = models.ForeignKey(Map, on_delete=models.SET_NULL, null=True)
    character_class = models.ForeignKey(CharacterClass, on_delete=models.SET_NULL, null=True)  # Dynamic class
    attack_power = models.PositiveIntegerField(default=1)

    hp = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])  # Minimum HP is 1
    current_tile = models.ForeignKey('Tile', on_delete=models.SET_NULL, null=True, related_name='game')  # Optional current tile
    inventory = models.ManyToManyField('Item', through='CharacterInventory')
    skills = models.ManyToManyField('Skill', through='CharacterSkill')
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)  # Date de la dernière mise à jour
    
    primary_weapon = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_primary_weapon')
    secondary_weapon = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_secondary_weapon')
    critical_hit_chance = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(100)])
    miss_chance = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(100)])

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
        starting_weapon = Item.objects.filter(name="Iron Sword").first()
        if starting_weapon:
            self.primary_weapon = starting_weapon
            self.save()


    def assign_class_skills(self):
        print("Assigning skills for class:", self.character_class.name)  # Vérification du nom de la classe

        class_skills = {
            "Warrior": ["Heroic Strike", "Shield Bash"],
            "Mage": ["Fireball", "Ice Bolt"],
            "Rogue": ["Backstab", "Gouge"],
            "Hunter": ["Aimed Shot", "Multi-Shot"],
            "Priest": ["Heal", "Holy Light"],
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
            'Warrior': 20,
            'Mage': 12,
            'Priest': 15,
            'Hunter': 18,
            'Rogue': 16,
        }
        return class_hp.get(self.character_class.name, 10)  # Utiliser self.character_class.name
    
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
            'Heroic Strike': 'A powerful melee attack that deals significant damage to a single target.',
            'Shield Bash': 'A stunning blow that interrupts the target''s actions and knocks them back.',
            'Fireball': 'A projectile that hurls a ball of fire at the target, dealing damage and igniting them.',
            'Ice Bolt': 'A projectile that hurls a bolt of ice at the target, dealing damage and slowing them.',
            'Backstab': 'A sneak attack that deals bonus damage if the target is facing away from the rogue.',
            'Gouge': 'A quick strike that stuns the target for a short duration.',
            'Aimed Shot': 'A precise shot that deals high damage to a single target.',
            'Multi-Shot': 'A rapid-fire attack that deals damage to multiple targets.',
            'Heal': 'A spell that restores health to a target.',
            'Holy Light': 'A powerful healing spell that also dispels harmful effects from the target.',
        }  
        return descriptions.get(self.name, '')  # Return the description or an empty string if not found
    
    
class CharacterSkill(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)  # Niveau de compétence
    experience = models.PositiveIntegerField(default=0)  # Expérience pour monter de niveau
    # Add fields for skill level, effects, etc. (optional)


class CharacterInventory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_equipped = models.BooleanField(default=False)
    
class NPC(models.Model):
    name = models.CharField(max_length=255)
    hp = models.PositiveIntegerField(default=1)  # Monsters should have at least 1 HP
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    species = models.CharField(max_length=255, choices=[
        ('Human', 'Human'),
        ('Orc', 'Orc'),
        ('Elf', 'Elf'),
        ('Dwarf', 'Dwarf'),
        ('Goblin', 'Goblin'),
        ('Troll', 'Troll'),
        ('Undead', 'Undead'),
        ('Dragon', 'Dragon'),
        ('Beast', 'Beast'),
    ])
    role = models.CharField(max_length=255)
    behaviour = models.CharField(max_length=255, choices=[
        ('Friendly', 'Friendly'),
        ('Neutral', 'Neutral'),
        ('Hostile', 'Hostile'),
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
    # Add fields for items, monsters, etc. on the tile (optional)

class NPCSavedState(models.Model):
    pnj = models.ForeignKey(NPC, on_delete=models.CASCADE)
    hp = models.IntegerField()
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    # Add fields for PNJ state (e.g., position, behavior, etc.) (optional)