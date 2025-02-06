from .base_move import BaseMove

class WestMove(BaseMove):
    def execute(self):
        valid_directions = ['west']
        self.validate(valid_directions)
        if not self.is_ok:
            return {"is_ok": False, "error_codes": self.error_codes}

        direction = self.request_data.get('direction')
        current_tile = self.game.current_tile

        # Calculer les nouvelles coordonnées en fonction de la direction
        new_posX, new_posY = current_tile.posX, current_tile.posY
        if direction == 'west':
            new_posX -= 1

        return super().execute(new_posX, new_posY)