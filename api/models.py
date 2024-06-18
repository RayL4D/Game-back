#graphGEFXServer/api/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User  # Import User model for potential user accounts
from django.utils import timezone
import datetime 
import json

# Create your models here.

    
class World(models.Model):  # Added model for World
    name = models.CharField(max_length=255, unique=True)  # Ensure unique world names
    description = models.TextField(blank=True)  # Optional world description
        
    def get_image_path(self):
        return f'assets/images/world/world{self.id}.png'

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


class Character(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional foreign key to User model
    name = models.CharField(max_length=255)
    world = models.ForeignKey(World, on_delete=models.SET_NULL, null=True)
    character_class = models.ForeignKey(CharacterClass, on_delete=models.SET_NULL, null=True)  # Dynamic class

    hp = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])  # Minimum HP is 1
    current_tile = models.ForeignKey('Tile', on_delete=models.SET_NULL, null=True, related_name='character')  # Optional current tile
    inventory = models.ManyToManyField('Item', through='CharacterInventory')
    skills = models.ManyToManyField('Skill', through='CharacterSkill')
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)

    def save_game_state(self):
        # Serialize character data and store it in the session
        session = Session.objects.get_or_create(expire_date=timezone.now() + datetime.timedelta(days=1))[0]  # Create or get session
        self.session_key = session
        character_data = {
            'name': self.name,
            'current_tile': self.current_tile.id if self.current_tile else None,
            'inventory': [item.id for item in self.characterinventory_set.all()],  # Get inventory item IDs
        }
        session.session_data['character_data'] = json.dumps(character_data)  # Serialize data to JSON
        session.save()
        self.save()  # Save character with updated session key

    def load_game_state(self):
        # Check if a session exists with character data
        session = self.session_key
        if session and 'character_data' in session.session_data:
            character_data = json.loads(session.session_data['character_data'])
            self.current_tile = Tile.objects.get(pk=character_data['current_tile']) if character_data['current_tile'] else None
            # Load inventory items based on retrieved IDs (consider using bulk operations for efficiency)
            self.characterinventory_set.clear()  # Clear existing inventory before loading
            for item_id in character_data['inventory']:
                item = Item.objects.get(pk=item_id)
                CharacterInventory.objects.create(character=self, item=item)
        else:
            print("No saved game state found")

    def equip_starting_gear(self):
        sword = Item.objects.filter(name="Iron Sword").first()  # Assuming a default sword exists
        if sword:
            self.inventory.add(sword, through_defaults={'quantity': 1})

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
            self.world = World.objects.first()  # Set the starting world
            self.current_tile = Tile.objects.filter(link_world=self.world).first()
            self.hp = self.get_default_hp()  # Set HP based on character class

        super().save(*args, **kwargs)  # Call the parent class's save method

        if creating:
            self.equip_starting_gear()  # Equip starting gear
            self.assign_class_skills()  # Assign class skills

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
    

class Skill(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # Optional skill description
    power = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Puissance d'attaque de la compétence
    def get_image_path(self):
        return f'assets/images/skills/skill{self.id}.png'

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
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    # Add fields for skill level, effects, etc. (optional)

class Item(models.Model):
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=255, choices=[
        ('Weapon', 'Weapon'),
        ('Potion', 'Potion'),
        ('Manuscript', 'Manuscript'),
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Food', 'Food'),
        ('Equipment', 'Equipment'),
    ])
    is_equipped = models.BooleanField(default=False)
    description = models.TextField(blank=True)  # Optional item description
    stats = models.JSONField(blank=True)  # Optional field for numerical stats (damage, armor, etc.)
    def get_image_path(self):
        return f'assets/images/items/item{self.id}.png'

class CharacterInventory(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Allow stacking items

class Tile(models.Model):
    link_world = models.ForeignKey(World, on_delete=models.CASCADE, null=True, blank=True)
    posX = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    posY = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    visited = models.BooleanField(default=False)  # Flag to track if the tile has been visited
    north_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='north_connected_tile')
    south_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='south_connected_tile')
    east_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='east_connected_tile')
    west_door = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='west_connected_tile')
    portal_to_world = models.ForeignKey(World, on_delete=models.SET_NULL, null=True, blank=True, related_name='portal_tiles') # Add this field    
    # Add fields for items in the tile or chest (consider a separate model for items in tiles)
    def get_image_path(self):
        return f'assets/images/tiles/tile{self.id}.png'    
    
    # Méthode pour changer de monde
    def change_world(self, character):
        if self.portal_to_world:
            character.world = self.portal_to_world
            character.save()


class Monster(models.Model):
    name = models.CharField(max_length=255)
    hp = models.PositiveIntegerField(default=1)  # Monsters should have at least 1 HP
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    monster_type = models.CharField(max_length=255, choices=[
        ('Goblin', 'Goblin'),
        ('Skeleton', 'Skeleton'),
        ('Slime', 'Slime'),
        ('Dragon', 'Dragon'),
        ('Troll', 'Troll'),
        ('Vampire', 'Vampire'),
    ])
    attack = models.PositiveIntegerField(default=1)  # Monster attack power
    def get_image_path(self):
        return f'assets/images/monsters/monster{self.id}.png'
    #experience = models.PositiveIntegerField(default=0)  # Experience gained from defeating the monster
    # Add fields for monster defense, special abilities, loot drops, etc. (optional)

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

class Chest(models.Model):
    name = models.CharField(max_length=255)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    inventory = models.ManyToManyField(Item, through='ChestItem')
    def get_image_path(self):
        return f'assets/images/chests/chest{self.id}.png'

class ChestItem(models.Model):
    chest = models.ForeignKey(Chest, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

class SavedGameState(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    current_tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    inventory_data = models.TextField(blank=True)  # Store serialized inventory data

    def save_from_character(self, character):
        self.current_tile = character.current_tile
        self.inventory_data = json.dumps([  # Serialize inventory item IDs
            item.id for item in character.characterinventory_set.all()
        ])
        self.save()

