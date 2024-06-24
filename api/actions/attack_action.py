# api/actions/attack_action.py

from .base_action import BaseAction
from ..models import Monster, CharacterInventory, Item
from rest_framework import status
from rest_framework.response import Response
from random import randint
from ..serializers import ItemSerializer, CharacterSerializer
class AttackAction(BaseAction):
    def validate(self):
        direction = self.request_data.get('direction')
        if not direction:
            raise ValueError("Missing 'direction' parameter")

        valid_directions = ['north', 'south', 'east', 'west']
        if direction not in valid_directions:
            raise ValueError("Invalid direction")

        # Vérifier si un monstre est présent dans la direction indiquée
        current_tile = self.character.current_tile
        target_tile = getattr(current_tile, f"{direction}_door")
        if target_tile is None:
            raise ValueError("No tile in that direction")
        monster = Monster.objects.filter(tile=target_tile).first()
        if monster is None:
            raise ValueError("No monster to attack in that direction")

    def execute(self):
        direction = self.request_data.get('direction')
        current_tile = self.character.current_tile
        target_tile = getattr(current_tile, f"{direction}_door")
        monster = Monster.objects.get(tile=target_tile)

        # Calcul des dégâts
        base_damage = self.character.attack_power
        weapon_damage = 0
        equipped_weapon = CharacterInventory.objects.filter(
            character=self.character,
            item__item_type='Weapon',
            item__is_equipped=True
        ).first()
        if equipped_weapon:
            weapon_stats = equipped_weapon.item.stats
            weapon_damage = weapon_stats.get('damage', 0)

        total_damage = base_damage + weapon_damage
        monster.hp -= total_damage

        if monster.hp <= 0:
            monster.delete()
            # Gain d'expérience
            self.character.experience += monster.experience
            self.character.save()

            # Récompenses (exemple simple)
            gold_reward = randint(1, 10)  # Récompense aléatoire d'or
            item = Item.objects.create(name="Potion de soin", item_type="Potion", tile=current_tile)  # Création d'une potion sur la tuile

            return {
                "success": "Monster defeated",
                "experience_gained": monster.experience,
                "gold_reward": gold_reward,
                "item_reward": {"id": item.id, "name": item.name}
            }
        else:
            monster.save()

            # Contre-attaque du monstre
            monster_damage = monster.attack_power
            self.character.hp -= monster_damage
            self.character.save()
            return {
                "success": "Monster attacked",
                "monster_hp": monster.hp,
                "character_hp": self.character.hp,
                "monster_damage": monster_damage
            }

    def handle_response(self, result):
        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = CharacterSerializer(self.character)
            response_data = serializer.data
            # Ajouter les détails de l'arme équipée à la réponse
            equipped_weapon = CharacterInventory.objects.filter(
                character=self.character,
                item__item_type='Weapon',
                item__is_equipped=True
            ).first()
            if equipped_weapon:
                response_data['equipped_weapon'] = ItemSerializer(equipped_weapon.item).data
            else:
                response_data['equipped_weapon'] = None
            return Response(response_data)