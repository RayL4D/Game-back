# myapp/views.py

from django.shortcuts import render
from rest_framework import viewsets #,generics
from .serializers import WorldSerializer, CharacterSerializer, SkillSerializer, CharacterSkillSerializer, ItemSerializer, CharacterInventorySerializer, TileSerializer, MonsterSerializer, ShopSerializer, ShopItemSerializer, ChestSerializer, ChestItemSerializer, SavedGameStateSerializer 
from .models import World, Character, Skill, CharacterSkill, Item, CharacterInventory, Tile, Monster, Shop, ShopItem, Chest, ChestItem, SavedGameState
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response


class WorldViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = World.objects.all()
    serializer_class = WorldSerializer

    @swagger_auto_schema(
        operation_description="Obtient la liste des mondes ou crée un nouveau monde."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

#class WorldView(generics.CreateAPIView):  (generics.ListAPIView)
#   queryset = World.objects.all()
#   serializer_class = WorldSerializer

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated]


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

class CharacterSkillViewSet(viewsets.ModelViewSet):
    queryset = CharacterSkill.objects.all()
    serializer_class = CharacterSkillSerializer
    permission_classes = [IsAuthenticated]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

class CharacterInventoryViewSet(viewsets.ModelViewSet):
    queryset = CharacterInventory.objects.all()
    serializer_class = CharacterInventorySerializer
    permission_classes = [IsAuthenticated]

class TileViewSet(viewsets.ModelViewSet):
    queryset = Tile.objects.all()
    serializer_class = TileSerializer
    permission_classes = [IsAuthenticated]

class MonsterViewSet(viewsets.ModelViewSet):
    queryset = Monster.objects.all()
    serializer_class = MonsterSerializer
    permission_classes = [IsAuthenticated]

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

class ShopItemViewSet(viewsets.ModelViewSet):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = [IsAuthenticated]

class ChestViewSet(viewsets.ModelViewSet):
    queryset = Chest.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

class ChestItemViewSet(viewsets.ModelViewSet):
    queryset = ChestItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = [IsAuthenticated]

class SavedGameStateViewSet(viewsets.ModelViewSet):
    queryset = SavedGameState.objects.all()
    serializer_class = SavedGameStateSerializer
    permission_classes = [IsAuthenticated]