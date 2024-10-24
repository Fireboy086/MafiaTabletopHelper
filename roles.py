# roles.py

class Role:
    def __init__(self, name, color):
        self.name = name
        self.color = color  # Color code for the role

    def is_mafia_aligned(self):
        return False

class Mafia(Role):
    def __init__(self):
        super().__init__("Zombie", "red")  # Renamed to "Zombie"

    def is_mafia_aligned(self):
        return True

class DonMafia(Role):
    def __init__(self):
        super().__init__("Don Mafia", "darkred")  # Changed name to "Don Mafia"

    def is_mafia_aligned(self):
        return True

class Vampire(Role):
    def __init__(self):
        super().__init__("Vampire", "purple")

    def is_mafia_aligned(self):
        return True

class Werewolf(Role):
    def __init__(self):
        super().__init__("Werewolf", "brown")
        self.is_reborn = False  # Indicates if this Werewolf is from Reborn

    def is_mafia_aligned(self):
        return True

class Villager(Role):
    def __init__(self):
        super().__init__("Villager", "gray")

class Doctor(Role):
    def __init__(self):
        super().__init__("Doctor", "green")

class Hunter(Role):
    def __init__(self):
        super().__init__("Hunter", "blue")
        self.normal_bullets = 1
        self.silver_bullets = 1
        self.is_reborn = False  # Indicates if this Hunter is from Reborn

class Witch(Role):
    def __init__(self):
        super().__init__("Witch", "pink")

    def is_mafia_aligned(self):
        return True

class Occultist(Role):
    def __init__(self):
        super().__init__("Occultist", "darkpurple")

    def is_mafia_aligned(self):
        return True

class Ghost(Role):
    def __init__(self):
        super().__init__("Ghost", "lightgray")

class Maniac(Role):
    def __init__(self):
        super().__init__("Maniac", "black")

class Reborn(Role):
    def __init__(self):
        super().__init__("Reborn", "gold")

# Add new roles here following the same structure if needed
