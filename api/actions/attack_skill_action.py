from .base_action import BaseAction
from ..models import Game, Skill, NPC, Item, NPCSavedState
from .npc_state_utils import get_or_create_npc_saved_state


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

        self.validate_target(npc_id)

    def validate_target(self, npc_id):
        current_tile = self.game.current_tile
        npc = NPC.objects.filter(tile=current_tile).first()

        if npc is None:
            raise ValueError("No NPC to attack")
        if npc.behaviour == 'NPCB_00002':
            raise ValueError("Cannot attack a friendly NPC")

    def execute(self):
        npc_id = self.request_data.get('npc_id')
        skill_id = self.request_data.get('skill_id')

        target = NPC.objects.get(id=npc_id, tile=self.game.current_tile)

        # Récupérer ou créer l'état sauvegardé
        npc_saved_state = get_or_create_npc_saved_state(self.game, self.game.user, target)


        if npc_saved_state.hp > 0:
            damage = self.calculate_damage(self.game, skill_id)

            # Apply damage to NPCSavedState (not the original NPC)
            npc_saved_state.hp -= damage

            # Update behaviour based on the modified HP (in NPCSavedState)
            npc_saved_state.behaviour = 'NPCB_00001'

            # Save the modified NPCSavedState
            npc_saved_state.save()

            return {'message': f"Vous avez utilisé la compétence {Skill.objects.get(id=skill_id).name} et infligé {damage} dégâts à {target.name}."}

        else:
            # Handle dead NPC case (unchanged)
            npc_saved_state.is_dead = True
            npc_saved_state.save()

            self.game.experience += target.experience_reward
            self.game.save()

            return {'message': f"Vous avez tué {target.name} et gagné {target.experience_reward} points d'expérience."}


    def calculate_damage(self, skill_id):

        base_damage = self.attack_power

        # Bonus de compétence
        if skill_id:
            skill = Skill.objects.get(id=skill_id)
            base_damage += skill.power

        return base_damage