#graphGEFXServer/api/serializers.py

from rest_framework import serializers
from .models import User, Map, Game, CharacterClass, Skill, CharacterSkill, Item, CharacterInventory, Tile, NPC, Shop, ShopItem, TileSavedState, NPCSavedState, ItemSavedState

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Les champs que vous voulez exposer

class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    character_class = serializers.PrimaryKeyRelatedField(queryset=CharacterClass.objects.all())

    class Meta:
        model = Game
        fields = '__all__'

    def create(self, validated_data):
        character_class = validated_data.pop('character_class')
        default_map = Map.objects.first()

        if default_map:
            game = Game.objects.create(
                user=self.context['request'].user,  # Utilisez request.user ici
                character_class=character_class,
                map=default_map,
                **validated_data
            )

            print("Game created:", game)  # Afficher l'objet Character créé
            print("Character class:", game.character_class)  # Vérifier si la classe est liée

    # Appliquer les paramètres par défaut après la création du personnage
            game.hp = game.get_default_hp()
            game.assign_class_skills()
            game.get_default_attack_power()
            game.get_default_defense()

            print("Character HP after get_default_hp:", game.hp)  # Vérifier les HP
            print("Character skills after assign_class_skills:", list(game.skills.all()))  # Vérifier les compétences

            game.save()
            return game

        else:
            raise serializers.ValidationError("Aucune map disponible")
    
class CharacterClassSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()  # Champ calculé pour le chemin de l'image

    class Meta:
        model = CharacterClass
        fields = '__all__'  # Champs à renvoyer

    def get_image_path(self, obj):
        return obj.get_image_path()  # Appel de la méthode du modèle pour obtenir le chemin
        

class SkillSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = '__all__'  # Incluez image_path

    def get_image_path(self, obj):
        return obj.get_image_path()

class CharacterSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterSkill
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()  # Add this line
    class Meta:
        model = Item
        fields = '__all__'
        
    def get_image_path(self, obj):
        return obj.get_image_path() 
    
class CharacterInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterInventory
        fields = '__all__'

class TileSerializer(serializers.ModelSerializer):
    north_door_id = serializers.IntegerField(source='north_door.id', allow_null=True)  # Ajout de allow_null=True
    east_door_id = serializers.IntegerField(source='east_door.id', allow_null=True)
    south_door_id = serializers.IntegerField(source='south_door.id', allow_null=True)
    west_door_id = serializers.IntegerField(source='west_door.id', allow_null=True)


    class Meta:
        model = Tile
        fields = '__all__'   # Add 'image_path' here

    def get_image_path(self, obj):
        return obj.get_image_path() 

class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPC
        fields = '__all__'

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'

class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = '__all__'

class TileSavedStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TileSavedState
        fields = '__all__'

class NPCSavedStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPCSavedState
        fields = '__all__'


class ItemSavedStateSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()  # Add this line
    class Meta:
        model = ItemSavedState
        fields = '__all__'