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
        current_tile = self.game.current_tile
        door_field = f"{direction}_door_id"
        if not getattr(current_tile, door_field): 
            raise ValueError(f"No door in the {direction} direction")

        # Vérifier si l'ID de la porte est 1 (ou l'ID que vous souhaitez)
        if getattr(current_tile, door_field) != 1:  # Remplacez 1 par l'ID de votre porte spécifique
            raise ValueError(f"Cannot move in the {direction} direction (wrong door)")

    def execute(self):
        direction = self.request_data.get('direction')
        current_tile = self.game.current_tile

        # Vérifier la porte et la destination
        if direction == 'north':
            target_tile = current_tile.north_door
        elif direction == 'south':
            target_tile = current_tile.south_door
        elif direction == 'east':
            target_tile = current_tile.east_door
        elif direction == 'west':
            target_tile = current_tile.west_door
        else:
            raise ValueError("Invalid direction")

        if not target_tile:
            return {"error": f"No tile in the {direction} direction"}

        # Vérifier si la tuile de destination est accessible (exemple de vérification)
        if target_tile.is_blocked:
            return {"error": "The path is blocked"}

        # Vérifier si la porte est ouverte (vous pouvez personnaliser cette logique)
        if target_tile.door_is_locked:
            return {"error": "The door is locked"}

        # Déplacer le personnage
        self.game.current_tile = target_tile
        self.game.save()
        self.game.save_game_state()

        # Gérer les événements liés au déplacement (optionnel)
        self.trigger_events(target_tile)

        return {"success": "Character moved", "new_position": {"posX": target_tile.posX, "posY": target_tile.posY}}