# myapp/views.py

from django.shortcuts import render
from rest_framework import viewsets #,generics
from .serializers import WorldSerializer, CharacterSerializer, SkillSerializer, CharacterSkillSerializer, ItemSerializer, CharacterInventorySerializer, TileSerializer, MonsterSerializer, ShopSerializer, ShopItemSerializer, ChestSerializer, ChestItemSerializer, SavedGameStateSerializer 
from .models import World, Character, Skill, CharacterSkill, Item, CharacterInventory, Tile, Monster, Shop, ShopItem, Chest, ChestItem, SavedGameState

class WorldViewSet(viewsets.ModelViewSet):
    queryset = World.objects.all()
    serializer_class = WorldSerializer


#class WorldView(generics.CreateAPIView):  (generics.ListAPIView)
#   queryset = World.objects.all()
#   serializer_class = WorldSerializer

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class CharacterSkillViewSet(viewsets.ModelViewSet):
    queryset = CharacterSkill.objects.all()
    serializer_class = CharacterSkillSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class CharacterInventoryViewSet(viewsets.ModelViewSet):
    queryset = CharacterInventory.objects.all()
    serializer_class = CharacterInventorySerializer

class TileViewSet(viewsets.ModelViewSet):
    queryset = Tile.objects.all()
    serializer_class = TileSerializer

class MonsterViewSet(viewsets.ModelViewSet):
    queryset = Monster.objects.all()
    serializer_class = MonsterSerializer

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

class ShopItemViewSet(viewsets.ModelViewSet):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer

class ChestViewSet(viewsets.ModelViewSet):
    queryset = Chest.objects.all()
    serializer_class = ShopSerializer

class ChestItemViewSet(viewsets.ModelViewSet):
    queryset = ChestItem.objects.all()
    serializer_class = ShopItemSerializer

class SavedGameStateViewSet(viewsets.ModelViewSet):
    queryset = SavedGameState.objects.all()
    serializer_class = SavedGameStateSerializer