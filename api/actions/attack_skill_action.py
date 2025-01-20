from .base_action import BaseAction
from ..models import Game, Skill, NPC, Item


class AttackSkillAction(BaseAction):
    def validate(self):
        attack = self.request_data.get('attack')
        if not attack:
            raise ValueError("Missing 'attack' parameter")

        if attack != 'attack_skill':
            raise ValueError("Invalid attack type")

        skill_id = self.request_data.get('skill_id')
        if not skill_id:
            raise ValueError("Missing 'skill_id' parameter")

        npc_id = self.request_data.get('npc_id')
        if not npc_id:
            raise ValueError("Missing 'npc_id' parameter")

        # Validation de la cible (similaire à AttackSimpleAction)
        self.validate_target(npc_id)

    def validate_target(self, npc_id):
        current_tile = self.game.current_tile
        npc = NPC.objects.filter(tile=current_tile).first()

        if npc is None:
            raise ValueError("No NPC to attack")
        if npc.behaviour == 'Friendly':
            raise ValueError("Cannot attack a friendly NPC")

    def execute(self):
        npc_id = self.request_data.get('npc_id')
        skill_id = self.request_data.get('skill_id')

        target = NPC.objects.get(id=npc_id)
        skill = Skill.objects.get(id=skill_id)

        damage = self.calculate_damage(self.game, skill_id)

        target.hp -= damage
        target.save()

        return {'message': f"Vous avez utilisé la compétence {skill.name} et infligé {damage} dégâts à {target.name}."}

    def calculate_damage(self, skill_id):

        base_damage = self.attack_power

        # Bonus de compétence
        if skill_id:
            skill = Skill.objects.get(id=skill_id)
            base_damage += skill.power

        return base_damage