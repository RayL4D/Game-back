from rest_framework import status
from rest_framework.response import Response
from ..serializers import GameSerializer

class BaseAction:
    def __init__(self, game, request_data):
        self.game = game
        self.request_data = request_data

    def execute(self):
        """Méthode abstraite pour exécuter l'action spécifique."""
        raise NotImplementedError("Subclasses must implement the execute method")

    def validate(self):
        """Méthode pour valider les données de la requête."""
        # Vous pouvez ajouter une vérification de base ici si nécessaire, sinon chaque action peut la redéfinir
        pass

    def handle_response(self, result):
        """Méthode pour gérer la réponse de l'action."""
        if 'error' in result:
            # Si une erreur est présente dans le résultat, on renvoie une réponse 400
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
        
        # Sérialisation de l'objet Game
        serializer = GameSerializer(self.game)
        response_data = serializer.data  # Dictionnaire des données du jeu
        
        # Si le résultat contient des informations sur les NPCs, ajoute-les à la réponse
        if 'npc_details' in result:
            response_data['npc_details'] = result['npc_details']

        # Si des messages supplémentaires sont présents, les ajouter à la réponse
        if 'message' in result:
            response_data['message'] = result['message']
        
        # if 'npc_attack_message' in result:
        #     response_data['npc_attack_message'] = result['npc_attack_message']

        # Ajouter un message sur le statut du joueur si nécessaire
        if 'player_status' in result:
            response_data['player_status'] = result['player_status']
        
        return Response(response_data)
