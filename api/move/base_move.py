from rest_framework import status
from rest_framework.response import Response
from ..serializers import GameSerializer
from ..models import Tile, TileSavedState

class BaseMove:
    def __init__(self, game, request_data):
        self.game = game
        self.request_data = request_data
        self.error_codes = []
        self.is_ok = True

    def validate(self, valid_directions):
        direction = self.request_data.get('direction')
        if not direction:
            self.error_codes.append("D001")
            self.is_ok = False
            return

        if direction not in valid_directions:
            self.error_codes.append("D002")
            self.is_ok = False
            return

        # Vérifier si la tuile actuelle a une porte dans la direction indiquée
        current_tile = self.game.current_tile
        door_level_field = f"{direction}_door_level"
        door_level = getattr(current_tile, door_level_field, None)

        if door_level is None:
            self.error_codes.append("D003")
            self.is_ok = False
            return

        if door_level == 0:
            self.error_codes.append("D004")
            self.is_ok = False
            return

        # Vérifier si une clé est nécessaire pour les portes de niveau 2 ou 3
        if door_level > 1:
            key_level = self.request_data.get('key_level', 0)
            if key_level < door_level:
                self.error_codes.append("D006")
                self.is_ok = False
                return

    def execute(self, new_posX, new_posY):
        
        current_tile = self.game.current_tile

        # Vérifier la nouvelle tuile
        target_tile = Tile.objects.filter(map=current_tile.map, posX=new_posX, posY=new_posY).first()

        if not target_tile:
            self.error_codes.append("D005")
            return

        # Déplacer le personnage
        self.game.current_tile = target_tile
        self.game.save()
        self.game.save_game_state()

        # Vérifier et créer TileSavedState si nécessaire
        tile_saved_state, created = TileSavedState.objects.get_or_create(
            game=self.game,
            user=self.game.user,
            tile=target_tile,
            defaults={'visited': True}
        )

        # Si le TileSavedState existait déjà, on peut vouloir le mettre à jour
        if not created and not tile_saved_state.visited:
            tile_saved_state.visited = True
            tile_saved_state.save()

        return

    def handle_response(self, result):
        """Méthode pour gérer la réponse de l'action."""
        if result.get('status') == "is ko!":
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = GameSerializer(self.game)
            return Response(serializer.data)