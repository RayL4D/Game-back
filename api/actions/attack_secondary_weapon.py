from .base_action import BaseAction
from ..models import Game, NPC
from .npc_state_utils import get_or_create_npc_saved_state

class AttackSecondaryWeaponAction(BaseAction):
    def validate(self):
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

    def execute(self):
        npc_id = self.request_data.get('npc_id')

        if not npc_id:
            raise ValueError("Veuillez spécifier l'ID du PNJ à attaquer.")
        
        target = NPC.objects.get(id=npc_id, tile=self.game.current_tile)

        # Récupérer ou créer l'état sauvegardé du NPC
        npc_saved_state = get_or_create_npc_saved_state(self.game, self.game.user, target)

        # Accéder à l'inventaire du personnage
        character_inventory = self.game.characterinventory_set.first()

        if not character_inventory:
            raise ValueError("L'inventaire du personnage est introuvable.")

        secondary_weapon = character_inventory.secondary_weapon

        # Attaque du joueur
        damage = self.game.attack_power
        if secondary_weapon:
            damage += secondary_weapon.attack_power

        result = {
            'message': "",
            'npc_hp': npc_saved_state.hp,
            'npc_attack_message': "",
            'npc_details': []  # Pour stocker les détails des NPCs agressifs
        }

        if npc_saved_state.hp > 0:
            # Dégâts infligés au NPC
            npc_saved_state.hp -= damage
            npc_saved_state.behaviour = 'NPCB_00001'  # Marquer comme agressif après l'attaque
            npc_saved_state.save()

            result['message'] = f"Vous avez infligé {damage} dégâts à {target.name}."

            if npc_saved_state.hp <= 0:
                npc_saved_state.is_dead = True
                npc_saved_state.save()
                # Ajouter l'expérience au joueur
                self.game.experience += target.experience_reward
                self.game.save()
                result['message'] = f"Vous avez tué {target.name} et gagné {target.experience_reward} points d'expérience."


        # Attaque des autres NPC agressifs après l'action du joueur
        npcs_on_tile = NPC.objects.filter(tile=self.game.current_tile, behaviour='NPCB_00001')  # Agressifs

        for npc in npcs_on_tile:
            npc_saved_state = get_or_create_npc_saved_state(self.game, self.game.user, npc)

            if npc_saved_state.hp > 0:  # Si le NPC agressif est encore vivant
                npc_damage = npc.attack_power  # Calcul des dégâts du NPC
                if npc_damage > 0:
                    self.game.hp -= npc_damage  # Soustraction des points de vie du joueur
                    result['npc_attack_message'] = f"{npc.name} vous attaque et vous inflige {npc_damage} dégâts."
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
                break  # Si le joueur est mort, on arrête les attaques

        # Enregistrer les changements dans le modèle Game
        self.game.save()

        return result
