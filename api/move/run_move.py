from .base_move import BaseMove

class RunMove(BaseMove):
    def execute(self):
        if not self.game.previous_tile:
            self.error_codes.append("R100")
            self.is_ok = False
            return {"is_ok": False, "error_codes": self.error_codes}

        # Déplacer le joueur vers la tuile précédente
        self.game.current_tile = self.game.previous_tile
        self.game.previous_tile = None  # Réinitialiser la tuile précédente
        self.game.save()

        # Créer ou mettre à jour le TileSavedState
        tile_saved_state, created = self.game.tilesavedstate_set.get_or_create(
            game=self.game,
            user=self.game.user,
            tile=self.game.current_tile,
            defaults={'visited': True}
        )

        if not created and not tile_saved_state.visited:
            tile_saved_state.visited = True
            tile_saved_state.save()

        return {"is_ok": True, "message": "Successfully ran away"}