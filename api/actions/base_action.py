# api/actions/base_action.py

from rest_framework import status
from rest_framework.response import Response
from ..serializers import CharacterSerializer

class BaseAction:
    def __init__(self, character, request_data):
        self.character = character
        self.request_data = request_data

    def execute(self):
        """Méthode abstraite pour exécuter l'action spécifique."""
        raise NotImplementedError("Subclasses must implement the execute method")

    def validate(self):
        """Méthode pour valider les données de la requête."""
        # Validation de base, commune à toutes les actions (si nécessaire)
        pass

    def handle_response(self, result):
        """Méthode pour gérer la réponse de l'action."""
        if result.get('error'):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = CharacterSerializer(self.character)  # Assurez-vous d'avoir un CharacterSerializer
            return Response(serializer.data)
