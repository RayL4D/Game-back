#graphGEFXServer/api/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User  # Import User model for potential user accounts
from django.utils import timezone
import datetime 
import json
from django.core.exceptions import ValidationError

# Create your models here.
    
class Map(models.Model):  # Added model for Map
    name = models.CharField(max_length=255, unique=True)  # Ensure unique map names
    description = models.TextField(blank=True)  # Optional map description
    starting_map = models.BooleanField(default=False)  # Flag to indicate the starting map

    def get_image_path(self):
        return f'/img/Map/map{self.id}.png'

class Tile(models.Model):
    map = models.ForeignKey(Map, on_delete=models.CASCADE, null=True, blank=True)
    posX = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    posY = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    visited = models.BooleanField(default=False)  # Flag to track if the tile has been visited
    north_door_level = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    south_door_level = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    east_door_level = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    west_door_level = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    portal_to_map = models.ForeignKey(Map, on_delete=models.SET_NULL, null=True, blank=True, related_name='portal_tiles')
    portal_destination_tile = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='arrival_tiles')

    # Méthode pour changer de monde
    def change_map(self, game):
        if self.portal_to_map:
            game.map = self.portal_to_map

            # Si une destination est définie, on place le joueur sur cette Tile
            if self.portal_destination_tile:
                game.current_tile = self.portal_destination_tile
            else:
                # Sinon, on prend la première Tile de la nouvelle map par défaut
                game.current_tile = Tile.objects.filter(map=self.portal_to_map).first()

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
        ('ITMT_00010', 'ITMT_00010'),
        ] )

    description = models.TextField(blank=True)  # Optional item description
    attack_power = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Attack power for weapons
    defense = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Defense value for armor
    healing = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Healing value for consumables
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)


    # def get_image_path(self):
    #     return f'https://rayl4d.github.io/GameImages/Item/{self.id}'

    
class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional foreign key to User model
    name = models.CharField(max_length=255)
    map = models.ForeignKey(Map, on_delete=models.SET_NULL, null=True)
    character_class = models.ForeignKey(CharacterClass, on_delete=models.SET_NULL, null=True)  # Dynamic class
    attack_power = models.PositiveIntegerField(default=1)
    defense = models.PositiveIntegerField(default=1)
    hp = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])  # Minimum HP is 1
    experience = models.PositiveIntegerField(default=1)  # Experience points
    level = models.PositiveIntegerField(default=1)  # Niveau du personnage
    skill_points = models.IntegerField(default=0)
    bronze = models.PositiveIntegerField(default=0)
    silver = models.PositiveIntegerField(default=0)
    gold = models.PositiveIntegerField(default=0)

    current_tile = models.ForeignKey('Tile', on_delete=models.SET_NULL, null=True, related_name='game') 
    inventory = models.ManyToManyField('Item', through='CharacterInventory', through_fields=('game', 'bag'))    
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


    def save_from_game(self, game):
        self.current_tile = game.current_tile
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
            self.current_tile = Tile.objects.filter(map=self.map).first()
            self.hp = self.get_default_hp()  # Set HP based on character class
            self.attack_power = self.get_default_attack_power()
            self.defense = self.get_default_defense()


        super().save(*args, **kwargs)  # Call the parent class's save method

        # Save the first visited tile upon creation
        if creating and self.current_tile:
            #next_tile = Tile.objects.filter(id=self.current_tile.id + 1).first()

            TileSavedState.objects.create(
                game=self,
                user=self.user,
                tile=self.current_tile,
                visited=True
            )

            """
            if next_tile:
                TileSavedState.objects.create(
                    game=self,
                    user=self.user,
                    tile=next_tile,
                    visited=True
                )
            else:
                print("La tile suivante n'existe pas.")
            """


        if creating:
            self.assign_class_skills()  # Assign class skills
            self.create_default_inventory()  # Attribuer l'équipement par défaut

        # Vérifier si le personnage est mort après la contre-attaque
        if self.hp <= 0:
            self.respawn()  # Appeler une méthode pour gérer la réapparition
        

    def respawn(self):
        # Logique de réapparition
        self.hp = self.get_default_hp()  # Réinitialiser les HP 
        self.current_tile = Tile.objects.filter(map=self.map).first()
        self.save()
        # Vous pouvez également réinitialiser d'autres aspects du personnage ici si nécessaire

    def create_default_inventory(self):
        """Ajoute des objets par défaut à l'inventaire du joueur lors de la création de la partie."""
        # Chercher les items par leur nom
        default_items = Item.objects.filter(name__in=["ITMN_00001", "ITMN_00011", "ITMN_00002", "ITMN_00003", "ITMN_00004", "ITMN_00005", "ITMN_00006" ])

        # Création de l'inventaire du personnage
        character_inventory = CharacterInventory.objects.create(game=self)

        # Chercher l'item "Wooden Sword" pour l'assigner comme primary_weapon
        # wooden_sword = default_items.filter(name="ITMN_00001").first()
        # if wooden_sword:
        #     character_inventory.primary_weapon = wooden_sword  # Assigner l'item à la primary_weapon
        #     character_inventory.save()  # Sauvegarder la modification de l'inventaire

        # Ajouter les autres objets à l'inventaire (ex. Healing Potion)
        for item in default_items:
            character_inventory.bag.add(item)

        character_inventory.save()



        
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
    
        
    def level_up(self):
        # Vérifie si le joueur a assez d'expérience pour passer au niveau supérieur
        if self.experience >= self.get_next_level_experience():
            self.level += 1
            self.skill_points += 1  # Ou un autre nombre selon votre choix
            self.experience -= self.get_next_level_experience()
            self.save()

    def get_next_level_experience(self):
        return self.level * 100  # Formule pour calculer l'expérience nécessaire pour le prochain niveau

    def add_skill_point(self, skill_id):
        if self.skill_points > 0:
            character_skill, created = CharacterSkill.objects.get_or_create(
                game=self, skill_id=skill_id
            )
            character_skill.level += 1
            character_skill.save()
            self.skill_points -= 1
            self.save()

    def get_skill_power(self, skill_id):
        character_skill = CharacterSkill.objects.get(game=self, skill_id=skill_id)
        skill = character_skill.skill
        return skill.power * character_skill.level
    
    
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

from django.db import models
from django.core.exceptions import ValidationError

class CharacterInventory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    bag = models.ManyToManyField(Item, related_name='character_inventory')  # Permet plusieurs items

    primary_weapon = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_primary_weapon')
    secondary_weapon = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_secondary_weapon')
    helmet = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_helmet')
    chestplate = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_chestplate')
    leggings = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_leggings')
    boots = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipped_as_boots')

    def equip_item(self, item):
        """Équipe un item en remplaçant l'ancien si nécessaire"""
        equip_slots = {
            'ITMT_00001': ['primary_weapon', 'secondary_weapon'],  # Weapons
            'ITMT_00002': ['helmet'],
            'ITMT_00003': ['chestplate'],
            'ITMT_00004': ['leggings'],
            'ITMT_00005': ['boots'],
        }

        if item.item_type not in equip_slots:
            raise ValidationError("Cet item ne peut pas être équipé.")

        # Gestion des armes
        if item.item_type == 'ITMT_00001':  # Weapon
            if self.primary_weapon is None:
                self.primary_weapon = item
            elif self.secondary_weapon is None:
                self.secondary_weapon = item
            else:
                self.primary_weapon = item  # Remplace l'arme primaire si les deux sont pleins
        else:
            for slot in equip_slots[item.item_type]:
                current_item = getattr(self, slot)
                if current_item:
                    self.bag.add(current_item)  # Remet l'ancien item dans le bag
                setattr(self, slot, item)  # Équipe l'item

        # Retirer l'item du bag après équipement
        if item in self.bag.all():
            self.bag.remove(item)

        self.save()

    def unequip_item(self, item):
        """Déséquipe un item et le remet dans le bag"""
        slots = ['primary_weapon', 'secondary_weapon', 'helmet', 'chestplate', 'leggings', 'boots']
        for slot in slots:
            if getattr(self, slot) == item:
                setattr(self, slot, None)
                self.bag.add(item)
                self.save()
                return True
        return False

    def add_item(self, item):
        """Ajoute un item à l'inventaire"""
        self.bag.add(item)

    def remove_item(self, item):
        """Retire un item de l'inventaire et le déséquipe s'il était équipé"""
        self.unequip_item(item)  # Vérifie si l'item est équipé et le retire
        self.bag.remove(item)

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
    experience_reward = models.PositiveIntegerField(default=1)  # Exemple de valeur d'expérience


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
    game = models.ForeignKey(Game, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    visited = models.BooleanField(default=False)
    class Meta:
        unique_together = (('game', 'user', 'tile'),)  # Ensure unique combination of game, user, and tile

class NPCSavedState(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    npc = models.ForeignKey(NPC, on_delete=models.CASCADE)
    hp = models.IntegerField()
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
    behaviour = models.CharField(max_length=255, choices=[
        ('NPCB_00002', 'NPCB_00002'),
        ('NPCB_00003', 'NPCB_00003'),
        ('NPCB_00001', 'NPCB_00001'),
    ])
    is_dead = models.BooleanField(default=False)

class ItemSavedState(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    tile = models.ForeignKey(Tile, on_delete=models.CASCADE)
