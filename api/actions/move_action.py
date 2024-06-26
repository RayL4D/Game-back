# api/actions/move_action.py

from .base_action import BaseAction
from ..models import Tile
from rest_framework import status
from rest_framework.response import Response


class MoveAction(BaseAction):
    def validate(self):
        direction = self.request_data.get('direction')
        if not direction:
            raise ValueError("Missing 'direction' parameter")

        valid_directions = ['north', 'south', 'east', 'west']
        if direction not in valid_directions:
            raise ValueError("Invalid direction")

        # Vérifier si la tuile actuelle a une porte dans la direction indiquée
        current_tile = self.character.current_tile
        door_field = f"{direction}_door_id"
        if not getattr(current_tile, door_field): 
            raise ValueError(f"No door in the {direction} direction")

        # Vérifier si l'ID de la porte est 1 (ou l'ID que vous souhaitez)
        if getattr(current_tile, door_field) != 1:  # Remplacez 1 par l'ID de votre porte spécifique
            raise ValueError(f"Cannot move in the {direction} direction (wrong door)")

    def execute(self):
        direction = self.request_data.get('direction')
        current_tile = self.character.current_tile

        # Déterminer la tuile cible en fonction de la direction
        if direction == 'north':
            target_tile = current_tile.north_door
        elif direction == 'south':
            target_tile = current_tile.south_door
        elif direction == 'east':
            target_tile = current_tile.east_door
        elif direction == 'west':
            target_tile = current_tile.west_door

        if target_tile and target_tile.id == 1:  # Vérifier si la porte est ouverte (ID = 1)
            self.character.current_tile = target_tile
            self.character.save()
            self.character.save_game_state()
            return {"success": "Character moved", "new_position": {"posX": target_tile.posX, "posY": target_tile.posY}}
        else:
            return {"error": "Invalid move"}
