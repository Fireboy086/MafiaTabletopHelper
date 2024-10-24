# main.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

from roles import (
    Mafia,
    DonMafia,
    Vampire,
    Werewolf,
    Villager,
    Doctor,
    Hunter,
    Witch,
    Occultist,
    Ghost,
    Maniac,
    Reborn,
)
from players import Player
from rules import GameRules


class MafiaApp(App):
    def build(self):
        self.title = "Mafia Tabletop Helper"
        Window.size = (800, 600)
        self.sm = ScreenManager()
        self.sm.add_widget(MainMenuScreen(name="mainmenu"))
        self.sm.add_widget(GameScreen(name="game"))
        return self.sm


class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

        self.title_label = Label(text="Mafia Tabletop Helper", font_size="40sp")
        self.player_count_label = Label(text="Enter number of players (1 to 23):")
        self.player_count_input = TextInput(
            multiline=False, input_filter="int", font_size="20sp", halign="center"
        )

        self.start_button = Button(
            text="Start Game", font_size="24sp", size_hint=(1, 0.2)
        )
        self.start_button.bind(on_press=self.start_game)

        # Developer Test Mode Buttons
        self.dev_mode_label = Label(text="Developer Test Mode:", font_size="24sp")
        self.small_game_button = Button(text="Small Game", font_size="20sp")
        self.big_game_button = Button(text="Big Game", font_size="20sp")
        self.custom_game_button = Button(text="Custom Game", font_size="20sp")

        self.small_game_button.bind(on_press=self.start_small_game)
        self.big_game_button.bind(on_press=self.start_big_game)
        self.custom_game_button.bind(on_press=self.start_custom_game)

        layout.add_widget(self.title_label)
        layout.add_widget(self.player_count_label)
        layout.add_widget(self.player_count_input)
        layout.add_widget(self.start_button)
        layout.add_widget(self.dev_mode_label)
        layout.add_widget(self.small_game_button)
        layout.add_widget(self.big_game_button)
        layout.add_widget(self.custom_game_button)
        self.add_widget(layout)

    def start_game(self, instance):
        try:
            player_count = int(self.player_count_input.text)
            if player_count > 23:
                raise ValueError("The maximum number of players is 23.")
            self.manager.get_screen("game").setup_game(player_count)
            self.manager.current = "game"
        except ValueError as e:
            popup = Popup(
                title="Error",
                content=Label(text=str(e)),
                size_hint=(None, None),
                size=(400, 200),
            )
            popup.open()

    def start_small_game(self, instance):
        # Predefined small game setup
        player_count = 5
        self.manager.get_screen("game").setup_game(player_count)
        game_screen = self.manager.get_screen("game")
        roles = [DonMafia(), Villager(), Witch(), Doctor(), Hunter()]
        for i, player in enumerate(game_screen.players):
            player.assign_role(roles[i])
            player.button.background_color = game_screen.get_color(player.role.color)
            player.button.text = f"{player.name}\n[Role: {player.role.name}]"
        self.manager.current = "game"
        game_screen.current_phase = "Night"
        game_screen.phase_label.text = f"Current Phase: {game_screen.current_phase}"
        game_screen.next_phase_button.disabled = True  # Disable during the night
        game_screen.night_phase()

    def start_big_game(self, instance):
        # Predefined big game setup
        player_count = 23
        self.manager.get_screen("game").setup_game(player_count)
        game_screen = self.manager.get_screen("game")
        roles = [
            DonMafia(),
            Vampire(),
            Vampire(),
            Werewolf(),
            Werewolf(),
            Mafia(),  # Zombie
            Villager(),
            Villager(),
            Villager(),
            Villager(),
            Villager(),
            Villager(),
            Villager(),
            Doctor(),
            Doctor(),
            Hunter(),
            Hunter(),
            Witch(),
            Occultist(),
            Ghost(),
            Maniac(),
            Reborn(),
            Mafia(),  # Zombie
        ]
        for i, player in enumerate(game_screen.players):
            player.assign_role(roles[i])
            player.button.background_color = game_screen.get_color(player.role.color)
            player.button.text = f"{player.name}\n[Role: {player.role.name}]"
        self.manager.current = "game"
        game_screen.current_phase = "Night"
        game_screen.phase_label.text = f"Current Phase: {game_screen.current_phase}"
        game_screen.next_phase_button.disabled = True  # Disable during the night
        game_screen.night_phase()

    def start_custom_game(self, instance):
        # Additional test modes can be implemented here
        pass


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.players = []
        self.game_rules = None
        self.current_phase = "Role Assignment"
        self.layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        self.add_widget(self.layout)
        self.log_button = None

    def setup_game(self, player_count):
        self.layout.clear_widgets()
        self.players = [Player(player_id=i + 1) for i in range(player_count)]
        self.game_rules = GameRules(self.players)
        self.current_phase = "Role Assignment"

        self.phase_label = Label(
            text=f"Current Phase: {self.current_phase}", font_size="24sp"
        )
        self.layout.add_widget(self.phase_label)

        self.player_grid = GridLayout(cols=5, spacing=10, size_hint_y=None)
        self.player_grid.bind(minimum_height=self.player_grid.setter("height"))

        for player in self.players:
            btn = Button(
                text=f"{player.name}\n[Role: {'Unassigned'}]",
                size_hint_y=None,
                height=100,
                font_size="18sp",
                markup=True,
            )
            btn.bind(on_press=self.on_player_button_press)
            btn.player = player
            player.button = btn
            self.player_grid.add_widget(btn)

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.player_grid)
        self.layout.add_widget(scroll_view)

        self.controls = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50, spacing=10
        )

        self.next_phase_button = Button(text="Next Phase", font_size="20sp")
        self.next_phase_button.bind(on_press=self.next_phase)

        self.log_button = Button(text="View Logbook", font_size="20sp")
        self.log_button.bind(on_press=self.view_logbook)

        self.controls.add_widget(self.next_phase_button)
        self.controls.add_widget(self.log_button)
        self.layout.add_widget(self.controls)

    def on_player_button_press(self, instance):
        if self.current_phase == "Role Assignment":
            self.assign_role_popup(instance.player)
        elif self.current_phase == "Night":
            self.record_night_action(instance.player)
        elif self.current_phase in ["Voting", "Revote"]:
            self.cast_vote(instance.player)

    def assign_role_popup(self, player):
        roles = [
            "Don Mafia",
            "Vampire",
            "Werewolf",
            "Zombie",
            "Villager",
            "Doctor",
            "Hunter",
            "Witch",
            "Occultist",
            "Ghost",
            "Maniac",
            "Reborn",
        ]

        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for role_name in roles:
            # Check if the maximum count for the role has been reached
            if self.role_count(role_name) < self.get_max_role_count(role_name):
                btn = Button(text=role_name, size_hint_y=None, height=40)
                btn.bind(
                    on_press=lambda btn_instance, rn=role_name: self.assign_role(
                        player, rn
                    )
                )
                grid.add_widget(btn)

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(grid)
        content.add_widget(scroll_view)

        popup = Popup(
            title=f"Assign Role to {player.name}",
            content=content,
            size_hint=(None, None),
            size=(300, 400),
        )
        popup.open()
        player.role_popup = popup

    def role_count(self, role_name):
        return sum(
            1
            for p in self.players
            if p.role and p.role.name == role_name
        )

    def get_max_role_count(self, role_name):
        max_counts = {
            "Don Mafia": 1,
            "Vampire": 2,
            "Werewolf": 2,  # Reborn can become an extra Werewolf
            "Zombie": 1,  # Renamed Mafia
            "Villager": 7,
            "Doctor": 2,
            "Hunter": 2,  # Reborn can become an extra Hunter
            "Witch": 1,
            "Occultist": 1,
            "Ghost": 1,
            "Maniac": 1,
            "Reborn": 1,
        }
        return max_counts.get(role_name, 0)

    def assign_role(self, player, role_name):
        role = None
        if role_name == "Don Mafia":
            role = DonMafia()
        elif role_name == "Vampire":
            role = Vampire()
        elif role_name == "Werewolf":
            role = Werewolf()
        elif role_name == "Zombie":
            role = Mafia()  # Mafia is renamed to Zombie
        elif role_name == "Villager":
            role = Villager()
        elif role_name == "Doctor":
            role = Doctor()
        elif role_name == "Hunter":
            role = Hunter()
        elif role_name == "Witch":
            role = Witch()
        elif role_name == "Occultist":
            role = Occultist()
        elif role_name == "Ghost":
            role = Ghost()
        elif role_name == "Maniac":
            role = Maniac()
        elif role_name == "Reborn":
            role = Reborn()
            # Prompt the Reborn player to choose their alignment
            self.prompt_reborn_choice(player)
            return  # Exit the method after handling Reborn choice
        # Add new role assignments here
        if role:
            player.assign_role(role)
            player.button.background_color = self.get_color(role.color)
            player.button.text = f"{player.name}\n[Role: {player.role.name}]"
            player.role_popup.dismiss()

    def prompt_reborn_choice(self, player):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        label = Label(text="Choose your path:")
        btn_hunter = Button(text="Become a Hunter", size_hint_y=None, height=40)
        btn_werewolf = Button(text="Become a Werewolf", size_hint_y=None, height=40)

        btn_hunter.bind(
            on_press=lambda instance: self.set_reborn_role(player, "Hunter")
        )
        btn_werewolf.bind(
            on_press=lambda instance: self.set_reborn_role(player, "Werewolf")
        )

        content.add_widget(label)
        content.add_widget(btn_hunter)
        content.add_widget(btn_werewolf)

        popup = Popup(
            title="Reborn Choice",
            content=content,
            size_hint=(None, None),
            size=(300, 200),
        )
        popup.open()
        player.reborn_popup = popup

    def set_reborn_role(self, player, choice):
        if choice == "Hunter":
            role = Hunter()
            role.is_reborn = True  # Flag to indicate this Hunter is from Reborn
            role.name = "Reborn (Hunter)"  # Update role name
        elif choice == "Werewolf":
            role = Werewolf()
            role.is_reborn = True  # Flag to indicate this Werewolf is from Reborn
            role.name = "Reborn (Werewolf)"  # Update role name
        player.assign_role(role)
        player.button.background_color = self.get_color(role.color)
        player.button.text = f"{player.name}\n[Role: {player.role.name}]"
        player.reborn_popup.dismiss()
        player.role_popup.dismiss()

    def get_color(self, color_name):
        colors = {
            "red": [1, 0, 0, 1],
            "darkred": [0.6, 0, 0, 1],
            "purple": [0.5, 0, 0.5, 1],
            "brown": [0.65, 0.16, 0.16, 1],
            "gray": [0.5, 0.5, 0.5, 1],
            "green": [0, 1, 0, 1],
            "blue": [0, 0, 1, 1],
            "pink": [1, 0.75, 0.8, 1],
            "darkpurple": [0.4, 0, 0.4, 1],
            "lightgray": [0.8, 0.8, 0.8, 1],
            "black": [0, 0, 0, 1],
            "gold": [1, 0.84, 0, 1],
            # Add colors for new roles here
        }
        return colors.get(color_name.lower(), [1, 1, 1, 1])

    def next_phase(self, instance):
        if self.current_phase == "Role Assignment":
            if any(p.role is None for p in self.players):
                popup = Popup(
                    title="Error",
                    content=Label(text="Please assign roles to all players."),
                    size_hint=(None, None),
                    size=(400, 200),
                )
                popup.open()
                return
            self.current_phase = "Night"
            self.phase_label.text = f"Current Phase: {self.current_phase}"
            self.next_phase_button.disabled = True  # Disable during the night
            self.night_phase()
        elif self.current_phase == "Day":
            self.current_phase = "Discussion"
            self.phase_label.text = f"Current Phase: {self.current_phase}"
            self.next_phase_button.text = "Start Voting"
            popup = Popup(
                title="Discussion Phase",
                content=Label(text="Discussion phase started. Proceed to voting when ready."),
                size_hint=(None, None),
                size=(400, 200),
            )
            popup.open()
        elif self.current_phase == "Discussion":
            self.current_phase = "Voting"
            self.phase_label.text = f"Current Phase: {self.current_phase}"
            self.next_phase_button.text = "Confirm Votes"
            self.voting_phase()
        elif self.current_phase in ["Voting", "Revote"]:
            result = self.game_rules.resolve_votes()
            if isinstance(result, Player):
                eliminated_player = result
                eliminated_player.button.disabled = True
                eliminated_player.button.text = f"{eliminated_player.name}\n[Role: {eliminated_player.role.name}]\n(Eliminated)"
                eliminated_player.button.background_color = [0.5, 0.5, 0.5, 1]
                popup = Popup(
                    title="Player Eliminated",
                    content=Label(text=f"{eliminated_player.name} has been eliminated."),
                    size_hint=(None, None),
                    size=(400, 200),
                )
                popup.open()
            elif result == "Tie":
                self.handle_tie()
                return  # Exit the method to allow for tie handling

            win_condition = self.game_rules.check_win_condition()
            if win_condition:
                popup = Popup(
                    title="Game Over",
                    content=Label(text=win_condition),
                    size_hint=(None, None),
                    size=(400, 200),
                )
                popup.bind(on_dismiss=self.return_to_main_menu)
                popup.open()
                self.next_phase_button.disabled = True
            else:
                self.game_rules.reset_night_actions()
                self.current_phase = "Night"
                self.phase_label.text = f"Current Phase: {self.current_phase}"
                self.next_phase_button.text = "Next Phase"
                self.next_phase_button.disabled = True  # Disable during the night
                self.night_phase()

    def return_to_main_menu(self, instance):
        self.manager.current = "mainmenu"

    def night_phase(self):
        popup = Popup(
            title="Night Phase",
            content=Label(text="Night has fallen. Roles will perform their actions."),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

        # Order: Don Mafia, Mafia, Vampire, Werewolf, Maniac, Hunter, Witch, Occultist, Doctor
        self.night_roles = [
            "DonMafia",
            "Mafia",
            "Vampire",
            "Werewolf",
            "Maniac",
            "Hunter",
            "Witch",
            "Occultist",
            "Doctor",
        ]
        self.current_night_role_index = 0
        self.process_night_role()

    def process_night_role(self):
        if self.current_night_role_index >= len(self.night_roles):
            # All roles have acted, skip to day
            self.reset_player_buttons()
            night_log, summary = self.game_rules.execute_night_actions()
            self.display_night_summary(summary)
            self.current_phase = "Day"
            self.phase_label.text = f"Current Phase: {self.current_phase}"
            self.next_phase_button.text = "Start Discussion"
            self.next_phase_button.disabled = False
            return

        role_name = self.night_roles[self.current_night_role_index]
        role_class = globals()[role_name]
        active_players = [
            p for p in self.players if p.alive and isinstance(p.role, role_class) and not p.has_acted
        ]

        # Adjust for Mafia roles based on Don Mafia's status
        if role_name == "Mafia":
            don_mafia_alive = any(
                isinstance(p.role, DonMafia) and p.alive for p in self.players
            )
            if don_mafia_alive:
                # Don Mafia is alive, Mafias do not act
                active_players = []
            else:
                # Don Mafia is dead, Mafias act collectively
                # Allow only one Mafia to select the target
                if any(p.has_acted for p in active_players):
                    active_players = []  # Already acted
                else:
                    pass  # Keep active_players as is

        if active_players:
            # Highlight active players
            for player in self.players:
                if player in active_players:
                    player.button.background_color = self.get_color(player.role.color)
                    player.button.disabled = False
                else:
                    player.button.disabled = True
            # Display prompt for current role
            role_prompt = Popup(
                title=f"{role_name}'s Turn",
                content=Label(text=f"{role_name}, please select your action."),
                size_hint=(None, None),
                size=(400, 200),
            )
            role_prompt.open()
        else:
            # No active players or all have acted, proceed to next role
            self.current_night_role_index += 1
            self.reset_player_buttons()
            self.process_night_role()
            return

    def record_night_action(self, player):
        if not player.alive or player.has_acted:
            return

        if isinstance(player.role, Hunter):
            # Hunter has a choice to shoot or check
            content = BoxLayout(orientation="vertical", spacing=10, padding=10)
            btn_check = Button(text="Check a Player", size_hint_y=None, height=40)
            btn_shoot = Button(text="Shoot a Player", size_hint_y=None, height=40)

            btn_check.bind(
                on_press=lambda instance: self.hunter_check(player)
            )
            btn_shoot.bind(
                on_press=lambda instance: self.hunter_shoot(player)
            )

            content.add_widget(btn_check)
            content.add_widget(btn_shoot)

            popup = Popup(
                title="Hunter Action",
                content=content,
                size_hint=(None, None),
                size=(300, 200),
            )
            popup.open()
            player.hunter_action_popup = popup
            return

        # Prepare valid targets based on the player's role
        valid_targets = []

        if isinstance(player.role, DonMafia):
            # Don Mafia can target anyone except themselves
            valid_targets = [t for t in self.players if t.alive and t != player]
        elif isinstance(player.role, Mafia):
            # If Don Mafia is alive, Mafias cannot act
            don_mafia_alive = any(
                isinstance(p.role, DonMafia) and p.alive for p in self.players
            )
            if don_mafia_alive:
                # Mafias cannot act
                player.has_acted = True
                self.check_all_players_acted()
                return
            else:
                # Don Mafia is dead, Mafias act collectively
                # Allow only one Mafia to select the target
                if any(p.has_acted for p in [p for p in self.players if p.alive and isinstance(p.role, Mafia)]):
                    # Another Mafia has already chosen the target
                    player.has_acted = True
                    self.check_all_players_acted()
                    return
                else:
                    # Mafia can target anyone except themselves and other Mafias
                    valid_targets = [
                        t for t in self.players if t.alive and not t.role.is_mafia_aligned()
                    ]
        elif isinstance(player.role, Witch) or isinstance(player.role, Occultist):
            # Can target anyone except themselves
            valid_targets = [t for t in self.players if t.alive and t != player]
        elif isinstance(player.role, Maniac):
            # Maniac can target anyone except themselves
            valid_targets = [t for t in self.players if t.alive and t != player]
        elif isinstance(player.role, Doctor):
            # Doctor can heal anyone including themselves
            valid_targets = [t for t in self.players if t.alive]
        else:
            valid_targets = []

        if not valid_targets:
            player.has_acted = True
            self.check_all_players_acted()
            return

        # Create popup for selecting targets
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        scroll_view = ScrollView(size_hint=(1, None), size=(300, 400))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for target in valid_targets:
            btn = Button(
                text=f"{target.name} ({target.role.name})", size_hint_y=None, height=40
            )
            btn.bind(
                on_press=lambda btn_instance, t=target: self.set_night_action(
                    player, t
                )
            )
            grid.add_widget(btn)

        scroll_view.add_widget(grid)
        content.add_widget(scroll_view)

        popup = Popup(
            title=f"{player.role.name} Action",
            content=content,
            size_hint=(None, None),
            size=(350, 500),
        )
        popup.open()
        player.action_popup = popup

    def hunter_check(self, player):
        player.hunter_action_popup.dismiss()
        valid_targets = [t for t in self.players if t.alive and t != player]

        if not valid_targets:
            player.has_acted = True
            self.check_all_players_acted()
            return

        # Create popup for selecting target to check
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        scroll_view = ScrollView(size_hint=(1, None), size=(300, 400))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for target in valid_targets:
            btn = Button(
                text=f"{target.name} ({target.role.name})", size_hint_y=None, height=40
            )
            btn.bind(
                on_press=lambda btn_instance, t=target: self.set_night_action(
                    player, t
                )
            )
            grid.add_widget(btn)

        scroll_view.add_widget(grid)
        content.add_widget(scroll_view)

        popup = Popup(
            title="Hunter Check",
            content=content,
            size_hint=(None, None),
            size=(350, 500),
        )
        popup.open()
        player.action_popup = popup

    def hunter_shoot(self, player):
        player.hunter_action_popup.dismiss()
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Bullet options
        btn_normal = Button(text=f"Normal Bullet ({player.role.normal_bullets} left)", size_hint_y=None, height=40)
        btn_silver = Button(text=f"Silver Bullet ({player.role.silver_bullets} left)", size_hint_y=None, height=40)

        btn_normal.bind(
            on_press=lambda instance: self.select_shoot_target(player, "normal")
        )
        btn_silver.bind(
            on_press=lambda instance: self.select_shoot_target(player, "silver")
        )

        content.add_widget(btn_normal)
        content.add_widget(btn_silver)

        popup = Popup(
            title="Choose Bullet Type",
            content=content,
            size_hint=(None, None),
            size=(300, 200),
        )
        popup.open()
        player.bullet_choice_popup = popup

    def select_shoot_target(self, player, bullet_type):
        player.bullet_choice_popup.dismiss()
        if bullet_type == "normal" and player.role.normal_bullets == 0:
            popup = Popup(
                title="No Bullets",
                content=Label(text="You have no normal bullets left."),
                size_hint=(None, None),
                size=(400, 200),
            )
            popup.open()
            return
        elif bullet_type == "silver" and player.role.silver_bullets == 0:
            popup = Popup(
                title="No Bullets",
                content=Label(text="You have no silver bullets left."),
                size_hint=(None, None),
                size=(400, 200),
            )
            popup.open()
            return

        valid_targets = [t for t in self.players if t.alive and t != player]

        if not valid_targets:
            player.has_acted = True
            self.check_all_players_acted()
            return

        # Create popup for selecting target to shoot
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        scroll_view = ScrollView(size_hint=(1, None), size=(300, 400))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for target in valid_targets:
            btn = Button(
                text=f"{target.name} ({target.role.name})", size_hint_y=None, height=40
            )
            btn.bind(
                on_press=lambda btn_instance, t=target: self.set_hunter_shoot_action(
                    player, bullet_type, t
                )
            )
            grid.add_widget(btn)

        scroll_view.add_widget(grid)
        content.add_widget(scroll_view)

        popup = Popup(
            title="Select Target to Shoot",
            content=content,
            size_hint=(None, None),
            size=(350, 500),
        )
        popup.open()
        player.shoot_target_popup = popup

    def set_hunter_shoot_action(self, player, bullet_type, target):
        player.shoot_target_popup.dismiss()
        player.has_acted = True
        player.shooting_action = {"bullet_type": bullet_type, "target": target}
        action_popup = Popup(
            title="Action Recorded",
            content=Label(text=f"Hunter will shoot {target.name} with a {bullet_type} bullet."),
            size_hint=(None, None),
            size=(400, 200),
        )
        action_popup.open()
        # Disable player button after action
        player.button.disabled = True
        action_popup.bind(on_dismiss=lambda instance: self.check_all_players_acted())

    def set_night_action(self, player, target):
        player.action_target = target
        player.has_acted = True
        player.action_popup.dismiss()
        action_popup = Popup(
            title="Action Recorded",
            content=Label(text=f"{player.role.name} targets {target.name}."),
            size_hint=(None, None),
            size=(400, 200),
        )
        action_popup.open()
        # Proceed to next role if applicable
        if isinstance(player.role, DonMafia):
            self.current_night_role_index += 1
            self.reset_player_buttons()
            action_popup.bind(on_dismiss=lambda instance: self.process_night_role())
        else:
            # Disable player button after action
            player.button.disabled = True
            action_popup.bind(on_dismiss=lambda instance: self.check_all_players_acted())

    def check_all_players_acted(self):
        role_name = self.night_roles[self.current_night_role_index]
        role_class = globals()[role_name]
        active_players = [
            p for p in self.players if p.alive and isinstance(p.role, role_class)
        ]

        # Adjust for Mafia roles
        if role_name == "Mafia":
            don_mafia_alive = any(
                isinstance(p.role, DonMafia) and p.alive for p in self.players
            )
            if don_mafia_alive:
                active_players = []  # Mafias do not act
            else:
                # If any Mafia has acted, consider all have acted (since they act collectively)
                if any(p.has_acted for p in active_players):
                    active_players = []  # Consider as all have acted
                else:
                    pass  # Wait for a Mafia to act

        if all(p.has_acted for p in active_players):
            self.current_night_role_index += 1
            self.reset_player_buttons()
            self.process_night_role()

    def reset_player_buttons(self):
        for player in self.players:
            if player.alive:
                player.button.disabled = True  # Disable buttons by default
                player.button.background_color = self.get_color(player.role.color)
                player.button.text = f"{player.name}\n[Role: {player.role.name}]"
            else:
                player.button.disabled = True
                player.button.background_color = [0.5, 0.5, 0.5, 1]
                player.button.text = f"{player.name}\n[Role: {player.role.name}]\n(Eliminated)"

    def display_night_summary(self, summary):
        summary_text = "\n".join(summary)
        popup = Popup(
            title="Night Summary",
            content=Label(text=summary_text),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

    def voting_phase(self):
        # Enable voting for alive players not disabled by Witch or Occultist
        for player in self.players:
            if player.alive and not player.disabled:
                player.button.disabled = False
            else:
                player.button.disabled = True

    def cast_vote(self, player):
        if not player.alive or player.disabled:
            return
        # Check if player is allowed to vote during revote
        if self.current_phase == "Revote" and player in self.tied_players:
            popup = Popup(
                title="Cannot Vote",
                content=Label(text="You cannot vote during the revote."),
                size_hint=(None, None),
                size=(400, 200),
            )
            popup.open()
            return

        # Create a ScrollView to accommodate all candidate options
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        scroll_view = ScrollView(size_hint=(1, None), size=(300, 400))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        # Determine eligible candidates
        if self.current_phase == "Revote":
            # Only tied players can be voted for
            candidates = [p for p in self.tied_players if p.alive]
        else:
            # All alive players except self and disabled
            candidates = [
                p
                for p in self.players
                if p.alive and p != player and not p.disabled
            ]

        for target in candidates:
            btn = Button(
                text=f"{target.name} ({target.role.name})",
                size_hint_y=None,
                height=40,
            )
            btn.bind(
                on_press=lambda btn_instance, t=target: self.record_vote(player, t)
            )
            grid.add_widget(btn)

        scroll_view.add_widget(grid)
        content.add_widget(scroll_view)

        popup = Popup(
            title=f"{player.name} Votes",
            content=content,
            size_hint=(None, None),
            size=(350, 500),
        )
        popup.open()
        player.vote_popup = popup

    def record_vote(self, player, target):
        target.votes += 1
        player.vote_popup.dismiss()
        popup = Popup(
            title="Vote Recorded",
            content=Label(text=f"{player.name} voted for {target.name}."),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()
        player.button.disabled = True  # Disable the button after voting to prevent multiple votes

    def handle_tie(self):
        popup = Popup(
            title="Tie in Votes",
            content=Label(text="There is a tie. Proceed to revote."),
            size_hint=(None, None),
            size=(400, 200),
        )
        popup.open()

        # Reset votes and proceed to revote among tied players
        max_votes = max(p.votes for p in self.players if p.alive)
        self.tied_players = [
            p for p in self.players if p.votes == max_votes and p.alive
        ]

        for player in self.players:
            player.reset_votes()
            if player.alive and not player.disabled and player not in self.tied_players:
                player.button.disabled = False  # Only untied, alive, non-disabled players can vote
            else:
                player.button.disabled = True  # Tied players cannot vote

        self.current_phase = "Revote"
        self.phase_label.text = f"Current Phase: {self.current_phase}"
        self.next_phase_button.text = "Confirm Votes"

    def view_logbook(self, instance):
        log_text = "\n".join(self.game_rules.logbook)
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        log_label = Label(text=log_text, size_hint_y=None)
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(log_label)
        content.add_widget(scroll_view)
        close_button = Button(text="Close", size_hint=(1, 0.1))
        content.add_widget(close_button)
        popup = Popup(
            title="Logbook", content=content, size_hint=(None, None), size=(500, 500)
        )
        close_button.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    MafiaApp().run()
