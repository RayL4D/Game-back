# api/actions/take_action.py

from .base_action import BaseAction
from ..models import Item, Tile, CharacterInventory, ItemSavedState
import random

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

                # Ajout de l'argent dans l'inventaire en fonction de la taille du coffre
                self.add_money_to_inventory(item)

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

            # Ajout de l'argent dans l'inventaire en fonction de la taille du coffre
            self.add_money_to_inventory(item)

            item_saved_state = ItemSavedState.objects.create(
                game=self.game,
                user=self.game.user,
                item=item,
                tile=None
            )

        return {"success": "Item taken", "item": {"id": item.id, "name": item.name, "quantity": inventory_item.quantity}}


    def add_money_to_inventory(self, item):
        """
        Fonction pour ajouter de l'argent à l'inventaire en fonction de la taille du coffre.
        Elle génère également un montant aléatoire et convertit l'argent en pièces supérieures si nécessaire.
        """
        money_type = None
        money_amount = 0

        # Déterminer la somme d'argent et le type basé sur la taille du coffre
        if item.chest_size == 'ITMCS_00001':  # Small
            money_type = 'bronze'
            money_amount = random.randint(1, 50)  # Entre 1 et 10 pièces de bronze
        elif item.chest_size == 'ITMCS_00002':  # Medium
            money_type = 'silver'
            money_amount = random.randint(1, 10)  # Entre 1 et 20 pièces d'argent
        elif item.chest_size == 'ITMCS_00003':  # Large
            money_type = 'silver'
            money_amount = random.randint(1, 50)  # Entre 1 et 50 pièces d'or

        if money_type and money_amount:
            # Ajouter de l'argent au personnage
            inventory_money, created = CharacterInventory.objects.get_or_create(
                game=self.game,
                item=None,  # Aucun item, juste de l'argent
                money_type=money_type
            )
            inventory_money.money += money_amount
            inventory_money.save()

        # Convertir les monnaies si le joueur en a 100 de chaque type
        self.convert_money_if_needed()

    def convert_money_if_needed(self):
        """
        Convertit les pièces de bronze en argent et les pièces d'argent en or si le joueur en a 100.
        """
        # Convertir les pièces de bronze en argent
        bronze_inventory = CharacterInventory.objects.filter(game=self.game, money_type='bronze').first()
        if bronze_inventory and bronze_inventory.money >= 100:
            silver_inventory, created = CharacterInventory.objects.get_or_create(
                game=self.game,
                item=None,
                money_type='silver'
            )
            # Conversion : 100 pièces de bronze = 1 pièce d'argent
            silver_inventory.money += bronze_inventory.money // 100
            silver_inventory.save()
            bronze_inventory.money %= 100
            bronze_inventory.save()

        # Convertir les pièces d'argent en or
        silver_inventory = CharacterInventory.objects.filter(game=self.game, money_type='silver').first()
        if silver_inventory and silver_inventory.money >= 100:
            gold_inventory, created = CharacterInventory.objects.get_or_create(
                game=self.game,
                item=None,
                money_type='gold'
            )
            # Conversion : 100 pièces d'argent = 1 pièce d'or
            gold_inventory.money += silver_inventory.money // 100
            gold_inventory.save()
            silver_inventory.money %= 100
            silver_inventory.save()
# api/actions/base_action.py