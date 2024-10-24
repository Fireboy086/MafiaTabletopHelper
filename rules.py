# rules.py

from roles import *
from players import Player

class GameRules:
    def __init__(self, players):
        self.players = players
        self.night_count = 0
        self.logbook = []

    def check_win_condition(self):
        mafia_count = sum(
            1 for p in self.players if p.alive and p.role.is_mafia_aligned()
        )
        villager_count = sum(
            1
            for p in self.players
            if p.alive
            and not p.role.is_mafia_aligned()
            and not isinstance(p.role, Maniac)
        )
        maniac_alive = any(
            isinstance(p.role, Maniac) and p.alive for p in self.players
        )

        if mafia_count == 0 and not maniac_alive:
            return "Villagers Win"
        elif mafia_count >= villager_count and villager_count > 0 and not maniac_alive:
            return "Mafia Wins"
        elif maniac_alive and mafia_count == 0 and villager_count == 0:
            return "Maniac Wins"
        else:
            return None

    def reset_night_actions(self):
        for player in self.players:
            player.reset_status()

    def execute_night_actions(self):
        self.night_count += 1
        night_log = []
        mafia_target = None
        don_mafia = None
        doctor_targets = []
        hunter_checks = []
        witch_target = None
        occultist_target = None
        maniac_target = None

        # Don Mafia selects target
        don_mafia_players = [
            p for p in self.players if p.alive and isinstance(p.role, DonMafia)
        ]
        if don_mafia_players:
            don_mafia = don_mafia_players[0]
            if don_mafia.action_target and don_mafia.action_target.alive:
                mafia_target = don_mafia.action_target
                night_log.append(f"Don Mafia targeted {mafia_target.name}")
            else:
                night_log.append("Don Mafia did not select a target")
        else:
            # If Don Mafia is dead, Mafias can collectively select a target
            mafia_players = [
                p for p in self.players
                if p.alive and p.role.is_mafia_aligned() and not isinstance(p.role, DonMafia)
            ]
            if mafia_players:
                # Collectively choose a target (assuming they have agreed on one)
                targets = [p.action_target for p in mafia_players if p.action_target and p.action_target.alive]
                if targets:
                    # Assuming majority vote among Mafias for target
                    mafia_target = max(set(targets), key=targets.count)
                    night_log.append(f"Mafias collectively targeted {mafia_target.name}")
                else:
                    night_log.append("Mafias did not select a target")
            else:
                night_log.append("No Mafias alive to select a target")

        # Doctor selects targets
        doctor_players = [
            p for p in self.players if p.alive and isinstance(p.role, Doctor)
        ]
        for doctor in doctor_players:
            if doctor.action_target and doctor.action_target.alive:
                doctor_targets.append(doctor.action_target)
                night_log.append(f"Doctor {doctor.name} healed {doctor.action_target.name}")
            else:
                night_log.append(f"Doctor {doctor.name} did not select a target")

        # Hunter actions
        hunter_players = [
            p for p in self.players if p.alive and isinstance(p.role, Hunter)
        ]
        for hunter in hunter_players:
            if hunter.shooting_action:
                bullet_type = hunter.shooting_action["bullet_type"]
                target = hunter.shooting_action["target"]
                if bullet_type == "silver" and hunter.role.silver_bullets > 0:
                    hunter.role.silver_bullets -= 1
                    if isinstance(target.role, Vampire):
                        target.eliminate()
                        night_log.append(
                            f"Hunter {hunter.name} used silver bullet to kill Vampire {target.name}"
                        )
                    else:
                        night_log.append(
                            f"Silver bullet had no effect on {target.name}"
                        )
                elif bullet_type == "normal" and hunter.role.normal_bullets > 0:
                    hunter.role.normal_bullets -= 1
                    if not isinstance(target.role, Vampire):
                        target.eliminate()
                        night_log.append(
                            f"Hunter {hunter.name} used normal bullet to kill {target.name}"
                        )
                    else:
                        night_log.append(
                            f"Normal bullet had no effect on Vampire {target.name}"
                        )
                else:
                    night_log.append(f"Hunter {hunter.name} has no bullets left")
                # Reset shooting action
                hunter.shooting_action = None
            elif hunter.action_target and hunter.action_target.alive:
                target = hunter.action_target
                # Check alignment
                if isinstance(target.role, DonMafia):
                    alignment = "Bloody Red"
                elif target.role.is_mafia_aligned():
                    alignment = "Red"
                else:
                    alignment = "Black"
                night_log.append(
                    f"Hunter {hunter.name} checked {target.name}, {alignment}"
                )
                hunter_checks.append((hunter, target, alignment))
            else:
                night_log.append(f"Hunter {hunter.name} did not select an action")

        # Witch actions
        witch_players = [
            p for p in self.players if p.alive and isinstance(p.role, Witch)
        ]
        if witch_players:
            witch = witch_players[0]
            if witch.action_target and witch.action_target.alive:
                witch_target = witch.action_target
                witch_target.disabled = True
                night_log.append(f"Witch disabled {witch_target.name}")
            else:
                night_log.append("Witch did not select a target")

        # Occultist actions
        occultist_players = [
            p for p in self.players if p.alive and isinstance(p.role, Occultist)
        ]
        if occultist_players:
            occultist = occultist_players[0]
            if occultist.action_target and occultist.action_target.alive:
                occultist_target = occultist.action_target
                occultist_target.disabled = True
                night_log.append(f"Occultist disabled {occultist_target.name}")
                # Check if target is Ghost
                if isinstance(occultist_target.role, Ghost):
                    occultist_target.eliminate()
                    night_log.append(
                        f"Ghost {occultist_target.name} was eliminated by Occultist"
                    )
            else:
                night_log.append("Occultist did not select a target")

        # Maniac actions
        maniac_players = [
            p for p in self.players if p.alive and isinstance(p.role, Maniac)
        ]
        if maniac_players:
            maniac = maniac_players[0]
            if maniac.action_target and maniac.action_target.alive:
                maniac_target = maniac.action_target
                maniac_target.eliminate()
                night_log.append(f"Maniac {maniac.name} killed {maniac_target.name}")
            else:
                night_log.append("Maniac did not select a target")

        # Resolve Mafia attack
        if mafia_target and mafia_target.alive:
            if mafia_target in doctor_targets:
                night_log.append(
                    f"{mafia_target.name} was attacked but healed by Doctor(s)"
                )
            elif isinstance(mafia_target.role, Ghost):
                night_log.append(f"Ghost {mafia_target.name} cannot be killed by Mafia")
            else:
                mafia_target.eliminate()
                night_log.append(f"{mafia_target.name} was killed by the Mafia")

        # Prepare summary
        summary = []
        # Include all deaths and effects
        for player in self.players:
            if not player.alive and not player.reported_dead:
                summary.append(f"{player.name} was found dead")
                player.reported_dead = True
            elif player.disabled and not player.reported_disabled:
                summary.append(f"{player.name} is unable to act today")
                player.reported_disabled = True

        night_log.append("SUMMARY:")
        night_log.extend(summary)
        night_log.append("----------------------")

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
