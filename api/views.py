#graphGEFXServer/api/views.py


from django.shortcuts import render
from rest_framework import viewsets #,generics
from .serializers import UserSerializer, WorldSerializer, CharacterSerializer, CharacterClassSerializer, SkillSerializer, CharacterSkillSerializer, ItemSerializer, CharacterInventorySerializer, TileSerializer, MonsterSerializer, ShopSerializer, ShopItemSerializer, ChestSerializer, ChestItemSerializer, SavedGameStateSerializer 
from .models import World, Character, CharacterClass, Skill, CharacterSkill, Item, CharacterInventory, Tile, Monster, Shop, ShopItem, Chest, ChestItem, SavedGameState
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Suppression des vérifications redondantes concernant le monde
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])  
    def action(self, request, pk=None):
        character = self.get_object()
        action_type = request.data.get('action_type')

        action_classes = {
            'attack': AttackAction,
            'take': TakeAction,
            'move': MoveAction,
        }

        action_class = action_classes.get(action_type)
        if action_class:
            action = action_class(character, request.data)
            action.validate()  # Valider les données de la requête
            result = action.execute()  # Exécuter l'action
            return action.handle_response(result)  # Gérer la réponse
        else:
            return Response({"error": "Invalid action type"}, status=status.HTTP_400_BAD_REQUEST)

    def start_new_game(self, request):
        character_id = request.data.get('character_id')
        save_name = request.data.get('save_name', '')  # Optionnel: nom de la sauvegarde

        try:
            character = Character.objects.get(pk=character_id, user=request.user)  # Vérifier que le personnage appartient à l'utilisateur
        except Character.DoesNotExist:
            return Response({"error": "Character not found"}, status=status.HTTP_404_NOT_FOUND)

        # Réinitialiser l'état du jeu
        character.reset_character()

        # Créer une nouvelle sauvegarde (SavedGameState)
        saved_game = SavedGameState.objects.create(
            user=request.user,
            character=character,
            current_tile=character.current_tile,
            save_name=save_name
        )

        serializer = SavedGameStateSerializer(saved_game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

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

    def get_queryset(self):
        # Filtrer les sauvegardes pour l'utilisateur actuel
        return SavedGameState.objects.filter(user=self.request.user)