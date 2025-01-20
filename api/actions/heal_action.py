from .base_action import BaseAction
from ..models import CharacterInventory

class HealAction(BaseAction):
    def validate(self):
        # Vérifier si l'action est bien un soin
        attack = self.request_data.get('attack')
        if attack != 'heal':
            raise ValueError("Action invalide : seul l'action 'heal' est autorisée pour cette méthode.")

        # Vérifier si le joueur a une potion équipée
        potion_instance = self.game.inventory.filter(item__item_type='Potion', is_equipped=True).first()
        if not potion_instance:
            raise ValueError("Vous n'avez pas de potion pour vous soigner.")

        # Vérifier si la potion a du pouvoir de guérison
        healing_power = potion_instance.item.healing
        if healing_power <= 0:
            raise ValueError("La potion sélectionnée n'a aucun pouvoir de guérison.")

    def execute(self):
        # Récupérer la première potion équipée de type "Potion"
        potion_instance = self.game.inventory.filter(item__item_type='Potion', is_equipped=True).first()
        if not potion_instance:
            raise ValueError("Vous n'avez pas de potion pour vous soigner.")

        # Récupérer la potion et ses informations
        potion_id = potion_instance.item.id
        healing_power = potion_instance.item.healing

        # Appliquer le soin
        self.game.hp += healing_power
        self.game.hp = min(self.game.hp.max_hp)
        self.game.save()

        # Consommer la potion (réduire la quantité ou supprimer si quantité = 1)
        if potion_instance.quantity > 1:
            potion_instance.quantity -= 1
            potion_instance.save()
        else:
            potion_instance.delete()

        potion_name = potion_instance.item.name
        
        return {'message': f"Vous avez utilisé une {potion_name} (ID {potion_id}) et récupéré {healing_power} points de vie."}
