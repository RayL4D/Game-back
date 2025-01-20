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

        damage = calculate_damage(self, base_damage)

        target.hp -= damage
        target.save()

        return {'message': f"Vous avez infligé {damage} dégâts à {target.name}."}

    def calculate_damage(self, base_damage):
        # Bonus d'arme
        if self.primary_weapon:
            base_damage += self.primary_weapon.attack_power
        if self.secondary_weapon:
            base_damage += self.secondary_weapon.attack_power

        return base_damage      




class UseSkillAction(BaseAction):
    def execute(self):
        skill_id = self.request_data.get('skill_id')
        target_id = self.request_data.get('target_id')

        attacker = self.game.character
        skill = Skill.objects.get(id=skill_id)
        target = NPC.objects.get(id=target_id) if target_id else attacker  # Pour les sorts de soin

        # Vérifier si le personnage a assez de mana
        if attacker.mana < skill.mana_cost:
            return {'error': 'Vous n\'avez pas assez de mana.'}

        # Appliquer les effets de la compétence
        if skill.effect == 'damage':
            damage = calculate_damage(attacker, target, skill_id)
            target.hp -= damage
            target.save()
        elif skill.effect == 'heal':
            attacker.hp += skill.power
            attacker.hp = min(attacker.hp, attacker.max_hp)
            attacker.save()
        # ... autres effets possibles

        attacker.mana -= skill.mana_cost
        attacker.save()

        return {'message': f"Vous avez utilisé {skill.name}."}

class DefendAction(BaseAction):
    def execute(self):
        # Augmenter la défense du personnage pour le prochain tour
        self.game.character.defense += 2
        self.game.character.save()
        return {'message': 'Vous vous mettez sur la défensive.'}

# Fonction pour calculer les dégâts
def calculate_damage(attacker, target, skill_id=None):
    base_damage = attacker.strength
    if skill_id:
        skill = Skill.objects.get(id=skill_id)
        base_damage += skill.power

    # Appliquer des modificateurs (critique, esquive, etc.)
    # ...

    return base_damage