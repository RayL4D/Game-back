#graphGEFXServer/api/serializers.py

from rest_framework import serializers
from .models import User, Map, Game, CharacterClass, Skill, CharacterSkill, Item, CharacterInventory, Tile, NPC, Shop, ShopItem, TileSavedState, NPCSavedState, ItemSavedState, Dialogue, DialogueSavedState

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = '__all__'  # Les champs que vous voulez exposer
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

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
        user = self.context['request'].user  # Récupération de l'utilisateur depuis le contexte
        character_class = validated_data.pop('character_class')
        default_map = Map.objects.first()

        # Vérification de la limite de 5 jeux par utilisateur
        if Game.objects.filter(user=user).count() >= 5:
            raise serializers.ValidationError("Vous avez atteint la limite de 5 jeux créés.")

        if default_map:
            game = Game.objects.create(
                user=user,  # Utilisation de l'utilisateur connecté
                character_class=character_class,
                map=default_map,
                **validated_data
            )

            # Appliquer les paramètres par défaut après la création du jeu
            game.hp = game.get_default_hp()
            game.assign_class_skills()
            game.get_default_attack_power()
            game.get_default_defense()
            game.save()

            return game
        else:
            raise serializers.ValidationError("Aucune map disponible.")
    
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
    class Meta:
        model = Item
        fields = '__all__'
        
    
class CharacterInventorySerializer(serializers.ModelSerializer):
    bag = ItemSerializer(many=True)  # Liste des items dans le bag
    primary_weapon = ItemSerializer(required=False, allow_null=True)  
    secondary_weapon = ItemSerializer(required=False, allow_null=True)
    helmet = ItemSerializer(required=False, allow_null=True)
    chestplate = ItemSerializer(required=False, allow_null=True)
    leggings = ItemSerializer(required=False, allow_null=True)
    boots = ItemSerializer(required=False, allow_null=True)

    class Meta:
        model = CharacterInventory
        fields = '__all__'


class TileSerializer(serializers.ModelSerializer):
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
        
class DialogueSerializer(serializers.Serializer):
    model = Dialogue()
    fields = '__all__'
    
class DialogueSavedStateSerializer(serializers.Serializer):
    model = DialogueSavedState()
    fields = '__all__'
    
class MapContextSerializer(serializers.Serializer):
    tile = TileSerializer()
    tile_saved_state = TileSavedStateSerializer()

class TileContextSerializer(serializers.Serializer):
    tile = TileSerializer()
    tile_saved_state = TileSavedStateSerializer()
    
class DialogueContextSerializer(serializers.Serializer):
    Dialogue = DialogueSerializer()
    Dialogue_Saved_State = DialogueSavedStateSerializer()
