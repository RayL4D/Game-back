from ..models import Tile, NPC
from actions.base_action import BaseAction
from rest_framework import status
from rest_framework.response import Response

class EastMove(BaseAction):
    def validate(self):
        direction = self.request_data.get('direction')
        if not direction:
            raise ValueError("Missing 'direction' parameter")

        valid_directions = ['east']
        if direction not in valid_directions:
            raise ValueError("Invalid direction")

        # Vérifier si la tuile actuelle a une porte dans la direction indiquée
        current_tile = self.game.current_tile
        door_field = f"{direction}_door_id"
        if not getattr(current_tile, door_field): 
            raise ValueError(f"No door in the {direction} direction")


    def execute(self):
        direction = self.request_data.get('direction')
        current_tile = self.game.current_tile

        # Vérifier la porte et la destination
        if direction == 'east':
            target_tile = current_tile.east_door

        if not target_tile:
            return {"error": f"No tile in the {direction} direction"}

        # Vérifier si la tuile de destination est accessible (exemple de vérification)
        if target_tile.is_blocked:
            return {"error": "The path is blocked"}

        # Vérifier si la porte est ouverte (vous pouvez personnaliser cette logique)
        if target_tile.door_is_locked:
            return {"error": "The door is locked"}
        
        # Vérifier s'il y a un PNJ sur la tuile actuelle
        if NPC.objects.filter(tile=current_tile).exists():
            return {"error": "You cannot move. There is an NPC on your current tile."}
        
        # npc = NPC.objects.get(tile=current_tile)
        # return {"options": [
        #    {"text": "Parler", "action": "talk"},
        #    {"text": "Attaquer", "action": "attack"}
        # ]}


        # Déplacer le personnage
        self.game.current_tile = target_tile
        self.game.save()
        self.game.save_game_state()

        return {
            "success": "Character moved", 
            "new_position": {"posX": target_tile.posX, "posY": target_tile.posY},
            "tile_data": {  # Données supplémentaires sur la tuile cible
                "has_npcs": NPC.objects.filter(tile=target_tile).exists(),
            }
        }