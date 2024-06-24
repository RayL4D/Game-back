# api/actions/take_action.py

from .base_action import BaseAction
from ..models import Item, Tile, CharacterInventory

class TakeAction(BaseAction):
    def validate(self):
        # Validation spécifique à la prise d'objet
        item_id = self.request_data.get('item_id')
        if not item_id:
            raise ValueError("Missing 'item_id' parameter")

        try:
            item_id = int(item_id)
        except ValueError:
            raise ValueError("Invalid 'item_id' parameter")

        # Vérifier si l'objet existe sur la tuile actuelle
        current_tile = self.character.current_tile
        if not Item.objects.filter(id=item_id, tile=current_tile).exists():
            raise ValueError("Item not found on this tile")

        # Vérifier si le personnage a déjà l'objet dans son inventaire
        if CharacterInventory.objects.filter(character=self.character, item_id=item_id).exists():
            raise ValueError("Item already in inventory")

    def execute(self):
        item_id = int(self.request_data.get('item_id'))
        item = Item.objects.get(id=item_id)

        # Vérifier si l'inventaire est plein (20 objets différents maximum)
        if self.character.inventory.count() >= 20 and not CharacterInventory.objects.filter(character=self.character, item=item).exists():
            return {"error": "Inventory is full"}

        try:
            inventory_item = CharacterInventory.objects.get(character=self.character, item=item)
            # Vérifier si l'objet peut être empilé (10 exemplaires maximum)
            if inventory_item.quantity >= 10:
                return {"error": "Cannot stack more of this item"}
            inventory_item.quantity += 1
            inventory_item.save()
        except CharacterInventory.DoesNotExist:
            CharacterInventory.objects.create(character=self.character, item=item, quantity=1)

        # Supprimer l'objet de la tuile (si vous ne voulez pas qu'il reste là)
        item.tile = None
        item.save()

        return {"success": "Item taken", "item": {"id": item.id, "name": item.name, "quantity": inventory_item.quantity}}