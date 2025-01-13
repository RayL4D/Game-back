#graphGEFXServer/api/views.py


from django.shortcuts import render
from rest_framework import viewsets #,generics
from .serializers import UserSerializer, MapSerializer, CharacterSerializer, CharacterClassSerializer, SkillSerializer, CharacterSkillSerializer, ItemSerializer, CharacterInventorySerializer, TileSerializer, PNJSerializer, ShopSerializer, ShopItemSerializer, SavedGameStateSerializer 
from .models import  Map, Character, CharacterClass, Skill, CharacterSkill, Item, CharacterInventory, Tile, NPC, Shop, ShopItem, SavedGameState
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import viewsets 
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from rest_framework import status
from .actions.attack_action import AttackAction
from .actions.take_action import TakeAction
from .actions.move_action import MoveAction
from django.core import serializers

class GameActionsViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer toutes les actions du jeu.
    """

    @action(detail=False, methods=['post'])
    def perform_action(self, request):
        character_id = request.data.get('character_id')
        action_type = request.data.get('action_type')

        try:
            character = Character.objects.get(pk=character_id, user=request.user)
        except Character.DoesNotExist:
            return Response({"error": "Character not found"}, status=status.HTTP_404_NOT_FOUND)

        action_classes = {
            'move': MoveAction,
            'attack': AttackAction,
            'take': TakeAction,
            # Ajoutez d'autres actions ici
        }

        action_class = action_classes.get(action_type)
        if action_class:
            action = action_class(character, request.data)
            action.validate()
            result = action.execute()
            return action.handle_response(result)
        else:
            return Response({"error": "Invalid action type"}, status=status.HTTP_400_BAD_REQUEST)
        
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

def getRoutes(request):
    route = [
        'api/token/'
        'api/token/refresh'
    ]
    return Response(route)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # Autorise l'accès sans authentification


class MapViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Map.objects.all()
    serializer_class = MapSerializer

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

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        character = self.get_object()
        direction = request.data.get('direction')

        action = MoveAction(character, request.data)
        action.validate()
        result = action.execute()
        return action.handle_response(result)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Remove redundant world checks
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    def start_new_game(self, request):
        print("Données de la requête :", request.data)  

        character_id = request.data.get('character_id')

        if not character_id:
            return Response({"error": "L'ID du personnage est requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            character = Character.objects.get(id=character_id, user=request.user)  
            print("Personnage récupéré :", character)  

            # Récupérer les objets Item de l'inventaire du personnage
            inventory_items = character.inventory.all()
            
            # Sérialiser les objets Item en JSON (vous pouvez personnaliser la sérialisation si besoin)
            inventory_data = serializers.serialize('json', inventory_items)

            saved_game = SavedGameState.objects.create(
                user=request.user,
                character=character,
                current_tile=character.current_tile,
                inventory_data=inventory_data,  # Stocker les données d'inventaire sérialisées
                save_name=request.data.get('save_name', '')
            )
            print("SavedGameState créé :", saved_game)  

            saved_game_serializer = SavedGameStateSerializer(saved_game)
            return Response(saved_game_serializer.data, status=status.HTTP_201_CREATED)

        except Character.DoesNotExist:
            return Response({"error": "Personnage non trouvé ou n'appartient pas à l'utilisateur"}, status=status.HTTP_404_NOT_FOUND)
    
        except Exception as e:  # Capturez les exceptions potentielles lors de la création de la sauvegarde
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
        
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def get_saved_games(self, request):
        saved_games = self.get_queryset()  # Filtrer les sauvegardes de l'utilisateur
        serializer = self.get_serializer(saved_games, many=True)
        return Response(serializer.data)
    
class CharacterClassViewSet(viewsets.ModelViewSet):
    queryset = CharacterClass.objects.all()
    serializer_class = CharacterClassSerializer
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

class NPCViewSet(viewsets.ModelViewSet):
    queryset = NPC.objects.all()
    serializer_class = PNJSerializer
    permission_classes = [IsAuthenticated]

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

class ShopItemViewSet(viewsets.ModelViewSet):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = [IsAuthenticated]



    
