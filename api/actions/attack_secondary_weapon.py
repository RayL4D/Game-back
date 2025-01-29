from .base_action import BaseAction
from ..models import Game, Skill, NPC, Item
from .npc_state_utils import get_or_create_npc_saved_state

class AttackSecondaryWeaponAction(BaseAction):
    def validate(self):
        attack = self.request_data.get('attack')
        if not attack:
            raise ValueError("Missing 'attack' parameter")

        valid_attack = ['attack_secondary_weapon']
        if attack not in valid_attack:
            raise ValueError("Invalid attack")
        
        current_tile = self.game.current_tile

        # Check if an NPC is present on the target tile
        npc = NPC.objects.filter(tile=current_tile).first()

        if npc is None:
            raise ValueError("No NPC to attack")
        if npc.behaviour == 'NPCB_00002':
            raise ValueError("Cannot attack a friendly NPC")
        
    def execute(self):
        npc_id = self.request_data.get('npc_id')

        if not npc_id:
            raise ValueError("Veuillez spécifier l'ID du PNJ à attaquer.")
        
        target = NPC.objects.get(id=npc_id, tile=self.game.current_tile)

        # Récupérer ou créer l'état sauvegardé
        npc_saved_state = get_or_create_npc_saved_state(self.game, self.game.user, target)

        if npc_saved_state.hp > 0:
            damage = self.game.attack_power

            if self.secondary_weapon:
                damage += self.secondary_weapon.attack_power

            npc_saved_state.hp -= damage
            npc_saved_state.behaviour = 'NPCB_00001'
            npc_saved_state.save()
            return {'message': f"Vous avez infligé {damage} dégâts à {target.name}."}
        else:
            npc_saved_state.is_dead = True
            npc_saved_state.save()

            # Ajouter l'expérience au joueur
            self.game.experience += target.experience_reward
            self.game.save()
            return {'message': f"Vous avez tué {target.name} et gagné {target.experience_reward} points d'expérience."}




