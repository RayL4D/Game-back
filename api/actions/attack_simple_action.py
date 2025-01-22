from .base_action import BaseAction
from ..models import Game, Skill, NPC, Item

class AttackSimpleAction(BaseAction):
    def validate(self):
        attack = self.request_data.get('attack')
        if not attack:
            raise ValueError("Missing 'attack' parameter")

        valid_attack = ['attack_simple']
        if attack not in valid_attack:
            raise ValueError("Invalid attack")
        
        current_tile = self.game.current_tile

        # Check if an NPC is present on the target tile
        npc = NPC.objects.filter(tile=current_tile).first()
        if npc is None:
            raise ValueError("No NPC to attack")
        if npc.behaviour == 'Friendly':
            raise ValueError("Cannot attack a friendly NPC")
        
    def execute(self):
        npc_id = self.request_data.get('npc_id')

        target = NPC.objects.get(id=npc_id)

        base_damage = self.game.attack_power
        
        def calculate_damage(self, base_damage):
            # Bonus d'arme
            if self.primary_weapon:
                base_damage += self.primary_weapon.attack_power
            if self.secondary_weapon:
                base_damage += self.secondary_weapon.attack_power

            return base_damage

        if not target.is_dead:
            damage = calculate_damage(self, base_damage)
            target.hp -= damage
            target.behaviour = 'Hostile'
            target.save()
            return {'message': f"Vous avez infligé {damage} dégâts à {target.name}."}
    
        else:
            target.is_dead = True
            target.save()

            # Ajouter l'expérience au joueur
            self.game.experience += target.experience_reward
            self.game.save()

        return {'message': f"Vous avez tué {target.name} et gagné {target.experience_reward} points d'expérience."}


