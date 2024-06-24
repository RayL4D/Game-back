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
            character=self.character,
            item__item_type='Potion'
        ).first()

        if potion:
            potion_stats = potion.item.stats
            healing_amount = potion_stats.get('healing', 0)
            self.character.hp += healing_amount
            self.character.hp = min(self.character.hp, self.character.get_default_hp())  # Limiter les HP au maximum
            self.character.save()
            potion.delete()  # Supprimer la potion après utilisation
            return {"success": "Character healed", "healing_amount": healing_amount}
        else:
            return {"error": "No potion available"}
