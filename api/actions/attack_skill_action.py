from .base_action import BaseAction
from ..models import Game, Skill, NPC, CharacterSkill
from .npc_state_utils import get_or_create_npc_saved_state

class AttackSkillAction(BaseAction):
    def validate(self):
        skill_id = self.request_data.get('skill_id')
        if not skill_id:
            raise ValueError("Missing 'skill_id' parameter")

        current_tile = self.game.current_tile

        # Vérification de la présence de NPC sur la tuile
        npcs = NPC.objects.filter(tile=current_tile)

        if not npcs.exists():
            raise ValueError("Aucun PNJ à attaquer.")
        
        # Vérifier si le NPC est mort via son état sauvegardé
        npc_id = self.request_data.get('npc_id')
        if npc_id:
            target = NPC.objects.get(id=npc_id, tile=self.game.current_tile)

            # Récupérer l'état sauvegardé du NPC
            npc_saved_state = get_or_create_npc_saved_state(self.game, self.game.user, target)

            # Si le NPC est mort (soit HP <= 0 soit is_dead=True)
            if npc_saved_state.hp <= 0 or npc_saved_state.is_dead:
                raise ValueError(f"{target.name} est déjà mort. Vous ne pouvez pas l'attaquer.")

        if any(npc.behaviour == 'NPCB_00002' for npc in npcs):  # Vérification des NPC amicaux
            raise ValueError("Impossible d'attaquer un PNJ amical.")

        self.validate_target(npc_id)
        self.validate_skill(skill_id)

    def validate_target(self, npc_id):
        current_tile = self.game.current_tile
        npc = NPC.objects.filter(tile=current_tile).first()

        if npc is None:
            raise ValueError("No NPC to attack")
        if npc.behaviour == 'NPCB_00002':
            raise ValueError("Cannot attack a friendly NPC")

    def validate_skill(self, skill_id):
        """ Vérifie si la compétence appartient bien au joueur dans cette partie. """
        skill_exists = CharacterSkill.objects.filter(game=self.game, skill_id=skill_id).exists()
        if not skill_exists:
            raise ValueError("Vous ne pouvez pas utiliser cette compétence avec votre classe actuelle.")

    def execute(self):
        npc_id = self.request_data.get('npc_id')
        skill_id = self.request_data.get('skill_id')

        skill = Skill.objects.get(id=skill_id)
        target = NPC.objects.get(id=npc_id, tile=self.game.current_tile)

        npc_saved_state = get_or_create_npc_saved_state(self.game, self.game.user, target)

        result = {
            'npc_hp': npc_saved_state.hp,
            'npc_attack_message': "",
            'npc_details': [],  # Pour stocker les détails des NPCs agressifs
            'message': ""
        }

        if npc_saved_state.hp > 0:
            # **Attaque du joueur**
            damage = self.calculate_damage(skill)
            npc_saved_state.hp -= damage
            npc_saved_state.behaviour = 'NPCB_00001'  # NPC devient agressif après l'attaque
            npc_saved_state.save()

            result['message'] = f"Vous avez utilisé {skill.name} et infligé {damage} dégâts à {target.name}."
            result['npc_hp'] = npc_saved_state.hp

            if npc_saved_state.hp <= 0:
                npc_saved_state.hp = 0
                npc_saved_state.is_dead = True
                npc_saved_state.save()
                # Ajouter l'expérience au joueur
                self.game.experience += target.experience_reward
                self.game.save()
                result['message'] = f"Vous avez tué {target.name} et gagné {target.experience_reward} points d'expérience."

        # **Contre-attaque des NPC agressifs**
        npcs_on_tile = NPC.objects.filter(tile=self.game.current_tile, behaviour='NPCB_00001')  # Agressifs

        for npc in npcs_on_tile:
            npc_saved_state = get_or_create_npc_saved_state(self.game, self.game.user, npc)

            if npc_saved_state.hp > 0:  # Si le NPC est vivant
                npc_damage = npc.attack_power  # Dégâts du NPC
                if npc_damage > 0:
                    self.game.hp -= npc_damage  # Le joueur subit des dégâts
                    result['npc_attack_message'] = f"{npc.name} vous attaque et inflige {npc_damage} dégâts."
                else:
                    result['npc_attack_message'] = f"{npc.name} tente de vous attaquer, mais vous bloquez l'attaque !"

                # Ajouter les détails des NPC agressifs
                result['npc_details'].append({
                    'npc_name': npc.name,
                    'damage_to_player': npc_damage,
                    'npc_hp': npc_saved_state.hp,
                    'is_dead': False if npc_saved_state.hp > 0 else True
                })

            # Vérifier si le joueur est mort
            if self.game.hp <= 0:
                result['player_status'] = "Vous êtes mort."
                break  # Arrête le combat si le joueur est mort

        # Sauvegarde de l'état du joueur
        self.game.save()

        return result

    def calculate_damage(self, skill):
        """Calcul des dégâts basés sur la compétence et l'attaque du joueur."""
        return self.game.attack_power + skill.power
