# roles.py

class Role:
    def __init__(self, name, color):
        self.name = name
        self.color = color  # Color code for the role

    def is_mafia_aligned(self):
        return False

class Mafia(Role):
    def __init__(self):
        super().__init__("Mafia", "red")

    def is_mafia_aligned(self):
        return True

class Villager(Role):
    def __init__(self):
        super().__init__("Villager", "gray")

class Doctor(Role):
    def __init__(self):
        super().__init__("Doctor", "green")

class Sheriff(Role):
    def __init__(self):
        super().__init__("Sheriff", "blue")

class Prostitute(Role):
    def __init__(self):
        super().__init__("Prostitute", "pink")

    def is_mafia_aligned(self):
        return True

# You can add new roles here following the same structure
