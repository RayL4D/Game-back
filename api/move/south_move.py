from ..models import Tile, NPC, TileSavedState
from .base_move import BaseMove
from rest_framework import status
from rest_framework.response import Response

class SouthMove(BaseMove):
    def validate(self):
        direction = self.request_data.get('direction')
        if not direction:
            raise ValueError("Missing 'direction' parameter")

        valid_directions = ['south']
        if direction not in valid_directions:
            raise ValueError("Invalid direction")

        # Vérifier si la tuile actuelle a une porte dans la direction indiquée
        current_tile = self.game.current_tile
        door_level_field = f"{direction}_door_level"
        door_level = getattr(current_tile, door_level_field)

        if door_level == 0:
            raise ValueError(f"No door in the {direction} direction")

        # Vérifier si une clé est nécessaire pour les portes de niveau 2 ou 3
        if door_level > 1:
            key_level = self.request_data.get('key_level', 0)
            if key_level < door_level:
                raise ValueError(f"A key of level {door_level} or higher is required to move in the {direction} direction")

    def execute(self):
        direction = self.request_data.get('direction')
        current_tile = self.game.current_tile

        # Calculer les nouvelles coordonnées en fonction de la direction
        new_posX, new_posY = current_tile.posX, current_tile.posY
        if direction == 'south':
            new_posY += 1

        # Vérifier la nouvelle tuile
        target_tile = Tile.objects.filter(map=current_tile.map, posX=new_posX, posY=new_posY).first()


        if not target_tile:
            return {"error": f"No tile in the {direction} direction"}


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

        return {
            "success": "Character moved", 
            "new_position": {"posX": target_tile.posX, "posY": target_tile.posY},
            "tile_data": {  # Données supplémentaires sur la tuile cible
                "has_npcs": NPC.objects.filter(tile=target_tile).exists(),
                "first_visit": created  # Indique si c'est la première visite de cette tuile
            }
        }