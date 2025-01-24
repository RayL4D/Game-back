#graphGEFXServer/api/views.py


from django.shortcuts import render
from rest_framework import viewsets #,generics
from .serializers import UserSerializer, MapSerializer, GameSerializer, CharacterClassSerializer, SkillSerializer, CharacterSkillSerializer, ItemSerializer, CharacterInventorySerializer, TileSerializer, NPCSerializer, ShopSerializer, ShopItemSerializer, TileSavedStateSerializer, NPCSavedStateSerializer 
from .models import  Map, Game, CharacterClass, Skill, CharacterSkill, Item, CharacterInventory, Tile, NPC, Shop, ShopItem, TileSavedState, NPCSavedState
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
from django.core import serializers

class GameActionsViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer toutes les actions du jeu.
    """

    @action(detail=False, methods=['post'])
    def perform_action(self, request):
        game_id = request.data.get('game_id')
        action_type = request.data.get('action_type')

        try:
            game = Game.objects.get(pk=game_id, user=request.user)
        except Game.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)

        action_classes = {
            'attack': AttackAction,
            'take': TakeAction,
            # Ajoutez d'autres actions ici
        }

        action_class = action_classes.get(action_type)
        if action_class:
            action = action_class(game, request.data)
            action.validate()
            result = action.execute()
            return action.handle_response(result)
        else:
            return Response({"error": "Invalid action type"}, status=status.HTTP_400_BAD_REQUEST)
        
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer 

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajouter des informations personnalisées au token
        token['username'] = user.username 
        if user.is_staff:
            token['is_admin'] = True

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/token/refresh',
        '/api/user/',]
    return Response(routes)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

class MapViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Map.objects.all()
    serializer_class = MapSerializer

    @swagger_auto_schema(
        operation_description="Obtient la liste des map ou crée une nouvelle map."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

#class WorldView(generics.CreateAPIView):  (generics.ListAPIView)
#   queryset = World.objects.all()
#   serializer_class = WorldSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]
    """
    @action(detail=False, methods=['post'])
    def start_new_game(self, request):
        # Récupérer les données nécessaires pour créer un nouveau jeu
        character_class_id = request.data.get('character_class_id')
        game_name = request.data.get('name')

        if not character_class_id:
            return Response(
                {"error": "Une classe de personnage est requise"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Récupérer la classe de personnage
            character_class = CharacterClass.objects.get(id=character_class_id)

            # Créer un nouveau jeu
            new_game = Game.objects.create(
                user=request.user,
                name=game_name,
                character_class=character_class,
                # Les autres attributs seront définis par les méthodes de save() du modèle
            )

            # La méthode save() du modèle Game va automatiquement :
            # - Définir la première map
            # - Définir la première tuile
            # - Définir les HP par défaut
            # - Équiper l'équipement de départ
            # - Assigner les compétences de classe

            # Sauvegarde automatique de la première tuile comme visitée
            if new_game.current_tile:
                TileSavedState.objects.create(
                    game=new_game, 
                    user=request.user, 
                    tile=new_game.current_tile, 
                    visited=True
                )

            # Utiliser le serializer pour renvoyer les données du nouveau jeu
            serializer = self.get_serializer(new_game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except CharacterClass.DoesNotExist:
            return Response(
                {"error": "Classe de personnage non trouvée"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        """
    
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
    serializer_class = NPCSerializer
    permission_classes = [IsAuthenticated]

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

class ShopItemViewSet(viewsets.ModelViewSet):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = [IsAuthenticated]


class TileSavedStateViewSet(viewsets.ModelViewSet):
    queryset = TileSavedState.objects.all()
    serializer_class = TileSavedStateSerializer
    permission_classes = [IsAuthenticated]
    
class NPCSavedStateViewSet(viewsets.ModelViewSet):
    queryset = NPCSavedState.objects.all()
    serializer_class = NPCSavedStateSerializer
    permission_classes = [IsAuthenticated]
