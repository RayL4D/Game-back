# api/actions/move_action.py

from .base_action import BaseAction
from ..models import Tile
from rest_framework import status
from rest_framework.response import Response


class MoveAction(BaseAction):
    def validate(self):
        new_posX = self.request_data.get('posX')
        new_posY = self.request_data.get('posY')

        if not new_posX or not new_posY:
            raise ValueError("Missing 'posX' or 'posY' parameter")

        try:
            new_posX = int(new_posX)
            new_posY = int(new_posY)
        except ValueError:
            raise ValueError("Invalid 'posX' or 'posY' parameter")

        # Vérifier si la tuile existe dans le monde du personnage
        if not Tile.objects.filter(link_world=self.character.world, posX=new_posX, posY=new_posY).exists():
            raise ValueError("Invalid tile coordinates")

    def execute(self):
        new_posX = int(self.request_data.get('posX'))
        new_posY = int(self.request_data.get('posY'))
        new_tile = Tile.objects.get(link_world=self.character.world, posX=new_posX, posY=new_posY)

        # Vérifier si le mouvement est valide (si la tuile est adjacente)
        if (
            new_tile.north_door == self.character.current_tile or
            new_tile.south_door == self.character.current_tile or
            new_tile.east_door == self.character.current_tile or
            new_tile.west_door == self.character.current_tile
        ):
            self.character.current_tile = new_tile
            self.character.save()

            # Sauvegarder l'état du jeu dans la session
            self.character.save_game_state()

            return {"success": "Character moved", "new_position": {"posX": new_posX, "posY": new_posY}}
        else:
            return {"error": "Invalid move"}
