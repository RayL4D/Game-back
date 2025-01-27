# api/actions/take_action.py

from .base_action import BaseAction
from ..models import Item, Tile, CharacterInventory, ItemSavedState

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
        current_tile = self.game.current_tile
        if not Item.objects.filter(id=item_id, tile=current_tile).exists():
            raise ValueError("Item not found on this tile")

        # Vérifier si le personnage a déjà l'objet dans son inventaire
        if CharacterInventory.objects.filter(game=self.game, item_id=item_id).exists():
            raise ValueError("Item already in inventory")

    def execute(self):
        item_id = int(self.request_data.get('item_id'))
        item = Item.objects.get(id=item_id)


        # Check for ItemSavedState
        item_saved_state = ItemSavedState.objects.filter(game=self.game, user=self.game.user, item=item).first()

        if item_saved_state:
            # Item already saved, check tile association
            if item_saved_state.tile is None:
                # Tile is None, prevent pickup (item already taken)
                return {"error": "Item already taken"}
            else:
                # Tile is associated, proceed with taking the item
                # Vérifier si l'inventaire est plein (20 objets différents maximum)
                if self.game.inventory.count() >= 20 and not CharacterInventory.objects.filter(game=self.game, item=item).exists():
                    return {"error": "Inventory is full"}

                try:
                    inventory_item = CharacterInventory.objects.get(game=self.game, item=item)
                    # Vérifier si l'objet peut être empilé (10 exemplaires maximum)
                    if inventory_item.quantity >= 10:
                        return {"error": "Cannot stack more of this item"}
                    inventory_item.quantity += 1
                    inventory_item.save()
                except CharacterInventory.DoesNotExist:
                    CharacterInventory.objects.create(game=self.game, item=item, quantity=1)
                item_saved_state.tile = None
                item_saved_state.save()
        else:
            # Item not saved yet, take the item
            # Vérifier si l'inventaire est plein (20 objets différents maximum)
            if self.game.inventory.count() >= 20 and not CharacterInventory.objects.filter(game=self.game, item=item).exists():
                return {"error": "Inventory is full"}

            try:
                inventory_item = CharacterInventory.objects.get(game=self.game, item=item)
                # Vérifier si l'objet peut être empilé (10 exemplaires maximum)
                if inventory_item.quantity >= 10:
                    return {"error": "Cannot stack more of this item"}
                inventory_item.quantity += 1
                inventory_item.save()
            except CharacterInventory.DoesNotExist:
                CharacterInventory.objects.create(game=self.game, item=item, quantity=1)
            item_saved_state = ItemSavedState.objects.create(
                game=self.game,
                user=self.game.user,
                item=item,
                tile=None
            )


        return {"success": "Item taken", "item": {"id": item.id, "name": item.name, "quantity": inventory_item.quantity}}