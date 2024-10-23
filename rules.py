# rules.py

from roles import Mafia, Villager, Doctor, Sheriff, Prostitute
from players import Player

class GameRules:
    def __init__(self, players):
        self.players = players  # List of Player instances
        self.night_count = 0
        self.logbook = []  # List to store log entries

    def check_win_condition(self):
        mafia_count = sum(1 for p in self.players if p.alive and p.role.is_mafia_aligned())
        citizen_count = sum(1 for p in self.players if p.alive and not p.role.is_mafia_aligned())

        if mafia_count == 0:
            return "Citizens Win"
        elif mafia_count >= citizen_count and citizen_count > 0:
            return "Mafia Wins"
        else:
            return None

    def reset_night_actions(self):
        for player in self.players:
            player.reset_status()

    def execute_night_actions(self):
        self.night_count += 1
        night_log = []
        mafia_target = None
        doctor_target = None
        sheriff_investigations = []
        prostitute_target = None

        # Mafia select target
        mafia_players = [p for p in self.players if p.alive and isinstance(p.role, Mafia)]
        if mafia_players:
            for player in mafia_players:
                if player.action_target and player.action_target.alive:
                    mafia_target = player.action_target
                    night_log.append(f"Mafia targeted {mafia_target.name}")
                    break  # Only one target per night
            if not mafia_target:
                night_log.append("Mafia did not select a target")

        # Doctor selects target (can self-heal)
        doctor_players = [p for p in self.players if p.alive and isinstance(p.role, Doctor)]
        if doctor_players:
            doctor = doctor_players[0]
            if doctor.action_target and doctor.action_target.alive:
                doctor_target = doctor.action_target
                night_log.append(f"Doctor healed {doctor_target.name}")
            else:
                night_log.append("Doctor did not select a target")

        # Sheriff investigates
        sheriff_players = [p for p in self.players if p.alive and isinstance(p.role, Sheriff)]
        if sheriff_players:
            sheriff = sheriff_players[0]
            if sheriff.action_target and sheriff.action_target.alive:
                target = sheriff.action_target
                alignment = "Red" if target.role.is_mafia_aligned() else "Black"
                night_log.append(f"Sheriff checked {target.name}, {alignment}")
                sheriff_investigations.append((sheriff, target, alignment))
            else:
                night_log.append("Sheriff did not select a target")

        # Prostitute selects target
        prostitute_players = [p for p in self.players if p.alive and isinstance(p.role, Prostitute)]
        if prostitute_players:
            prostitute = prostitute_players[0]
            if prostitute.action_target and prostitute.action_target.alive:
                prostitute_target = prostitute.action_target
                prostitute_target.disabled = True
                night_log.append(f"Prostitute slept with {prostitute_target.name}")
            else:
                night_log.append("Prostitute did not select a target")

        # Resolve Mafia attack
        if mafia_target and mafia_target.alive:
            if doctor_target == mafia_target:
                night_log.append(f"{mafia_target.name} was attacked but healed by Doctor.")
                # Player is saved; no elimination
            else:
                mafia_target.eliminate()
                night_log.append(f"{mafia_target.name} was killed by the Mafia.")

        # Prepare summary
        summary = []
        if mafia_target and not mafia_target.alive:
            summary.append(f"{mafia_target.name} was killed")
        else:
            summary.append("No one was killed")

        if prostitute_target:
            summary.append(f"{prostitute_target.name} cannot talk or vote today")

        night_log.append("SUMMARY:")
        night_log.extend(summary)
        night_log.append("----------------------")  # Add separator line

        # Add night log to the logbook
        self.logbook.append(f"Night {self.night_count} Actions:")
        self.logbook.extend(night_log)

        # Reset night actions
        for player in self.players:
            player.action_target = None

        return night_log, summary

    def resolve_votes(self):
        max_votes = max(p.votes for p in self.players if p.alive)
        candidates = [p for p in self.players if p.votes == max_votes and p.alive]

        if len(candidates) == 1:
            eliminated_player = candidates[0]
            eliminated_player.eliminate()
            self.logbook.append(f"{eliminated_player.name} was eliminated by voting.")
            return eliminated_player
        else:
            # Tie occurred
            return "Tie"

    def alive_players(self):
        return [p for p in self.players if p.alive]
