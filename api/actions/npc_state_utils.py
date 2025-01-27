from ..models import NPCSavedState

def get_or_create_npc_saved_state(game, user, npc):
    """
    Retrieves or creates a NPCSavedState for the given NPC, game, and user.

    Args:
        game (Game): The game instance.
        user (User): The user instance.
        npc (NPC): The NPC instance.

    Returns:
        NPCSavedState: The retrieved or created NPCSavedState instance.
    """

    npc_saved_state = NPCSavedState.objects.filter(game=game, user=user, npc=npc).first()
    if not npc_saved_state:
        npc_saved_state = NPCSavedState.objects.create(
            game=game,
            user=user,
            npc=npc,
            # Initialize other fields with default values or based on the NPC
            hp=npc.hp,
            tile=npc.tile,
            behaviour=npc.behaviour,
            is_dead=False,
        )
    return npc_saved_state