from .base_move import BaseMove

class SouthMove(BaseMove):
    def execute(self):
        valid_directions = ['south']
        self.validate(valid_directions)
        if not self.is_ok:
            return {"is_ok": False, "error_codes": self.error_codes}

        direction = self.request_data.get('direction')
        current_tile = self.game.current_tile

        # Calculer les nouvelles coordonnées en fonction de la direction
        new_posX, new_posY = current_tile.posX, current_tile.posY
        if direction == 'south':
            new_posY -= 1

        return super().execute(new_posX, new_posY)