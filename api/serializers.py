#graphGEFXServer/api/serializers.py

from rest_framework import serializers
from .models import User, World, Character, CharacterClass, Skill, CharacterSkill, Item, CharacterInventory, Tile, Monster, Shop, ShopItem, Chest, ChestItem, SavedGameState

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Les champs que vous voulez exposer

class WorldSerializer(serializers.ModelSerializer):
    class Meta:
        model = World
        fields = '__all__'

class CharacterSerializer(serializers.ModelSerializer):
    character_class = serializers.PrimaryKeyRelatedField(queryset=CharacterClass.objects.all())

    class Meta:
        model = Character
        fields = '__all__'

    def create(self, validated_data):
        character_class = validated_data.pop('character_class')
        default_world = World.objects.first()

        if default_world:
            character = Character.objects.create(
                character_class=character_class,
                world=default_world,
                **validated_data
            )

            print("Character created:", character)  # Afficher l'objet Character créé
            print("Character class:", character.character_class)  # Vérifier si la classe est liée

    # Appliquer les paramètres par défaut après la création du personnage
            character.hp = character.get_default_hp()
            character.equip_starting_gear()
            character.assign_class_skills()

            print("Character HP after get_default_hp:", character.hp)  # Vérifier les HP
            print("Character inventory after equip_starting_gear:", list(character.inventory.all()))  # Vérifier l'inventaire
            print("Character skills after assign_class_skills:", list(character.skills.all()))  # Vérifier les compétences

            character.save()
            return character

        else:
            raise serializers.ValidationError("Aucun monde disponible")
    
class CharacterClassSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()  # Champ calculé pour le chemin de l'image

    class Meta:
        model = CharacterClass
        fields = ['id', 'name', 'description', 'image_path']  # Champs à renvoyer

    def get_image_path(self, obj):
        return obj.get_image_path()  # Appel de la méthode du modèle pour obtenir le chemin
        

class SkillSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'power', 'image_path']  # Incluez image_path

    def get_image_path(self, obj):
        return obj.get_image_path()

class CharacterSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterSkill
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class CharacterInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterInventory
        fields = '__all__'

class TileSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()  # Add this line

    class Meta:
        model = Tile
        fields = '__all__'   # Add 'image_path' here

    def get_image_path(self, obj):
        return obj.get_image_path() 

class MonsterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monster
        fields = '__all__'

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'

class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = '__all__'

class ChestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chest
        fields = '__all__'

class ChestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChestItem
        fields = '__all__'

class SavedGameStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedGameState
        fields = '__all__'

