from .base_action import BaseAction
from ..models import NPC, CharacterInventory, Item
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

        # Check if a tile exists in the indicated direction
        current_tile = self.character.current_tile
        target_tile = getattr(current_tile, f"{direction}_door")
        if target_tile is None:
            raise ValueError("No tile in that direction")

        # Check if an NPC is present on the target tile
        npc = NPC.objects.filter(tile=target_tile).first()
        if npc is None:
            raise ValueError("No NPC to attack in that direction")
        if npc.behaviour == 'Friendly':
            raise ValueError("Cannot attack a friendly NPC")

    def execute(self):
        direction = self.request_data.get('direction')
        current_tile = self.character.current_tile
        target_tile = getattr(current_tile, f"{direction}_door")
        npc = NPC.objects.get(tile=target_tile)

        # Calculate base damage
        base_damage = self.character.attack_power

        # Consider equipped weapon damage
        equipped_weapon = CharacterInventory.objects.filter(
            character=self.character,
            item__item_type='Weapon',
            item__is_equipped=True
        ).first()
        weapon_damage = 0
        if equipped_weapon:
            weapon_stats = equipped_weapon.item.stats
            weapon_damage = weapon_stats.get('damage', 0)


        # Calculate total damage
        base_damage = self.character.attack_power

        # Critical hit chance
        critical_hit_chance = self.character.critical_hit_chance

        # Miss chance
        miss_chance = self.character.miss_chance

        # Roll for critical hit, miss, or normal hit
        attack_roll = randint(1, 100)

        if attack_roll <= self.character.critical_hit_chance:
            # Critical hit! Double the damage
            total_damage *= 2
            result = "Critical hit!"
        elif attack_roll <= self.character.critical_hit_chance + self.character.miss_chance:
            # Miss! No damage dealt
            total_damage = 0
            result = "Miss!"
        else:
            # Normal hit
            result = "Normal hit"


        # Apply damage to NPC
        npc.hp -= total_damage
        # Si le PNJ était neutre, le rendre hostile et le faire contre-attaquer
        if npc.behaviour == 'Neutral':
            npc.behaviour = 'Hostile'
            npc.save()
            # Calculer les dégâts de l'attaque du PNJ
            npc_damage = npc.attack_power
            self.character.hp -= npc_damage
            self.character.save()
        
        if npc.hp <= 0:
            npc.delete()
            # Gain experience (optional, adjust as needed)
            self.character.experience += npc.experience
            self.character.save()

            # Rewards (simple example)
            gold_reward = randint(1, 10)  # Random gold reward
            item = Item.objects.create(name="Potion de soin", item_type="Potion", tile=current_tile)  # Create a potion on the tile

            return {
                "success": "NPC defeated",
                "gold_reward": gold_reward,
                "item_reward": {"id": item.id, "name": item.name}
            }
        else:
            npc.save()

            # No counter-attack for NPCs (adjust as needed)
            # monster_damage = npc.attack_power
            # self.character.hp -= monster_damage
            # self.character.save()

            return {
                "success": result,
                "npc_hp": npc.hp,
                "character_hp": self.character.hp,
            }


    def handle_response(self, result):
        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = CharacterSerializer(self.character)
            response_data = serializer.data
            # Add details of the equipped weapon to the response
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