from .base_move import BaseMove

class AllMove(BaseMove):
    def execute(self):
        valid_directions = ['north', 'south', 'east', 'west']
        self.validate(valid_directions)
        if not self.is_ok:
            return {"is_ok": False, "error_codes": self.error_codes}

        direction = self.request_data.get('direction')
        current_tile = self.game.current_tile

        # Calculer les nouvelles coordonnées en fonction de la direction
        new_posX, new_posY = current_tile.posX, current_tile.posY
        if direction == 'north':
            new_posY -= 1
        elif direction == 'south':
            new_posY += 1
        elif direction == 'east':
            new_posX += 1
        elif direction == 'west':
            new_posX -= 1

        return super().execute(new_posX, new_posY)