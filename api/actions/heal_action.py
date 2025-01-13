# api/actions/heal_action.py

from .base_action import BaseAction
from ..models import CharacterInventory

class HealAction(BaseAction):
    def validate(self):
        # Validation spécifique à l'utilisation de potion (présence de potion, etc.)
        pass

    def execute(self):
        # Logique de soin avec potion
        potion = CharacterInventory.objects.filter(
            game=self.game,
            item__item_type='Potion'
        ).first()

        if potion:
            potion_stats = potion.item.stats
            healing_amount = potion_stats.get('healing', 0)
            self.game.hp += healing_amount
            self.game.hp = min(self.game.hp, self.game.get_default_hp())  # Limiter les HP au maximum
            self.game.save()
            potion.delete()  # Supprimer la potion après utilisation
            return {"success": "Character healed", "healing_amount": healing_amount}
        else:
            return {"error": "No potion available"}
