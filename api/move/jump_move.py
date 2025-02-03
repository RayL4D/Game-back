from ..models import Tile, TileSavedState
from .base_move import BaseMove

class JumpMove(BaseMove):
    def validate(self):
        # Vérifier si le joueur est sur une tuile avec un portail
        current_tile = self.game.current_tile
        if not current_tile.portal_to_map:
            raise ValueError("No portal on the current tile")

    def execute(self):
        current_tile = self.game.current_tile

        # Vérifier si le joueur veut utiliser le portail
        use_portal = self.request_data.get('use_portal', False)

        if not use_portal:
            return {"message": "You chose not to use the portal"}

        # Vérifier que la map cible existe
        new_map = current_tile.portal_to_map
        if not new_map:
            return {"error": "No destination map found"}

        # Trouver la tile de destination
        destination_tile = current_tile.portal_destination_tile or Tile.objects.filter(map=new_map).first()
        if not destination_tile:
            return {"error": "No destination tile found in the new map"}

        # Mettre à jour la position du joueur
        self.game.map = new_map
        self.game.current_tile = destination_tile
        self.game.save()
        self.game.save_game_state()

        # Enregistrer la visite de la nouvelle tuile
        tile_saved_state, created = TileSavedState.objects.get_or_create(
            game=self.game,
            user=self.game.user,
            tile=destination_tile,
            defaults={'visited': True}
        )

        if not created and not tile_saved_state.visited:
            tile_saved_state.visited = True
            tile_saved_state.save()

        return {
            "success": "Character teleported through the portal",
            "new_position": {"posX": destination_tile.posX, "posY": destination_tile.posY},
            "tile_data": {
                "first_visit": created
            }
        }
