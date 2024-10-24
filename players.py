# players.py

class Player:
    def __init__(self, player_id, name="Player"):
        self.player_id = player_id
        self.name = f"{name} {player_id}"
        self.role = None  # Role will be assigned later
        self.alive = True
        self.votes = 0  # Number of votes received during voting phase
        self.action_target = None  # Target selected during night actions
        self.disabled = False  # Disabled by Witch or Occultist
        self.has_acted = False  # Has the player acted during the night
        self.reported_dead = False  # Used for night summary
        self.reported_disabled = False  # Used for night summary
        self.shooting_action = None  # For Hunter's shooting action

    def assign_role(self, role):
        self.role = role

    def reset_votes(self):
        self.votes = 0

    def eliminate(self):
        self.alive = False

    def reset_status(self):
        self.votes = 0
        self.action_target = None
        self.disabled = False
        self.has_acted = False
        self.shooting_action = None
