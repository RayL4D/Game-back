from rest_framework import serializers
from .models import User, World, Character, Skill, CharacterSkill, Item, CharacterInventory, Tile, Monster, Shop, ShopItem, Chest, ChestItem, SavedGameState

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Les champs que vous voulez exposer

class WorldSerializer(serializers.ModelSerializer):
    class Meta:
        model = World
        fields = '__all__'

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

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
    class Meta:
        model = Tile
        fields = '__all__'

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