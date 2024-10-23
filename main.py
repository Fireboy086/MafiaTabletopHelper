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

from roles import Mafia, Villager, Doctor, Sheriff, Prostitute  # Add new roles as needed
from players import Player
from rules import GameRules

class MafiaApp(App):
    def build(self):
        self.title = "Mafia Tabletop Helper"
        Window.size = (800, 600)
        self.sm = ScreenManager()
        self.sm.add_widget(MainMenuScreen(name='mainmenu'))
        self.sm.add_widget(GameScreen(name='game'))
        return self.sm

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        self.title_label = Label(text="Mafia Tabletop Helper", font_size='40sp')
        self.player_count_label = Label(text="Enter number of players (5 to 20):")
        self.player_count_input = TextInput(multiline=False, input_filter='int', font_size='20sp', halign='center')

        self.start_button = Button(text="Start Game", font_size='24sp', size_hint=(1, 0.2))
        self.start_button.bind(on_press=self.start_game)

        layout.add_widget(self.title_label)
        layout.add_widget(self.player_count_label)
        layout.add_widget(self.player_count_input)
        layout.add_widget(self.start_button)
        self.add_widget(layout)

    def start_game(self, instance):
        try:
            player_count = int(self.player_count_input.text)
            if player_count < 5:
                raise ValueError("At least 5 players are required.")
            if player_count > 20:
                raise ValueError("The maximum number of players is 20.")
            self.manager.get_screen('game').setup_game(player_count)
            self.manager.current = 'game'
        except ValueError as e:
            popup = Popup(title='Error', content=Label(text=str(e)),
                          size_hint=(None, None), size=(400, 200))
            popup.open()

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.players = []
        self.game_rules = None
        self.current_phase = "Role Assignment"
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)
        self.log_button = None

    def setup_game(self, player_count):
        self.layout.clear_widgets()
        self.players = [Player(player_id=i+1) for i in range(player_count)]
        self.game_rules = GameRules(self.players)
        self.current_phase = "Role Assignment"

        self.phase_label = Label(text=f"Current Phase: {self.current_phase}", font_size='24sp')
        self.layout.add_widget(self.phase_label)

        self.player_grid = GridLayout(cols=5, spacing=10, size_hint_y=None)
        self.player_grid.bind(minimum_height=self.player_grid.setter('height'))

        for player in self.players:
            btn = Button(
                text=f"{player.name}\n[Role: {'Unassigned'}]",
                size_hint_y=None, height=100, font_size='18sp', markup=True
            )
            btn.bind(on_press=self.on_player_button_press)
            btn.player = player
            player.button = btn
            self.player_grid.add_widget(btn)

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.player_grid)
        self.layout.add_widget(scroll_view)

        self.controls = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)

        self.next_phase_button = Button(text="Next Phase", font_size='20sp')
        self.next_phase_button.bind(on_press=self.next_phase)

        self.log_button = Button(text="View Logbook", font_size='20sp')
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
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        roles = ["Mafia", "Villager", "Doctor", "Sheriff", "Prostitute"]  # Add new roles here
        for role_name in roles:
            btn = Button(text=role_name, size_hint_y=None, height=40)
            btn.bind(on_press=lambda btn_instance, rn=role_name: self.assign_role(player, rn))
            content.add_widget(btn)
        popup = Popup(title=f'Assign Role to {player.name}', content=content,
                      size_hint=(None, None), size=(300, 400))
        popup.open()
        player.role_popup = popup

    def assign_role(self, player, role_name):
        role = None
        if role_name == "Mafia":
            role = Mafia()
        elif role_name == "Villager":
            role = Villager()
        elif role_name == "Doctor":
            role = Doctor()
        elif role_name == "Sheriff":
            role = Sheriff()
        elif role_name == "Prostitute":
            role = Prostitute()
        # Add new role assignments here
        if role:
            player.assign_role(role)
            player.button.background_color = self.get_color(role.color)
            player.button.text = f"{player.name}\n[Role: {player.role.name}]"
            player.role_popup.dismiss()

    def get_color(self, color_name):
        colors = {
            "red": [1, 0, 0, 1],
            "gray": [0.5, 0.5, 0.5, 1],
            "green": [0, 1, 0, 1],
            "blue": [0, 0, 1, 1],
            "pink": [1, 0.75, 0.8, 1],
            # Add colors for new roles here
        }
        return colors.get(color_name.lower(), [1, 1, 1, 1])

    def next_phase(self, instance):
        if self.current_phase == "Role Assignment":
            if any(p.role is None for p in self.players):
                popup = Popup(title='Error', content=Label(text='Please assign roles to all players.'),
                              size_hint=(None, None), size=(400, 200))
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
            popup = Popup(title='Discussion Phase',
                          content=Label(text='Discussion phase started. Proceed to voting when ready.'),
                          size_hint=(None, None), size=(400, 200))
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
                popup = Popup(title='Player Eliminated', content=Label(text=f'{eliminated_player.name} has been eliminated.'),
                              size_hint=(None, None), size=(400, 200))
                popup.open()
            elif result == "Tie":
                self.handle_tie()
                return  # Exit the method to allow for tie handling

            win_condition = self.game_rules.check_win_condition()
            if win_condition:
                popup = Popup(title='Game Over', content=Label(text=win_condition),
                              size_hint=(None, None), size=(400, 200))
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
        self.manager.current = 'mainmenu'

    def night_phase(self):
        popup = Popup(title='Night Phase', content=Label(text='Night has fallen. Roles will perform their actions.'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

        # Order: Mafia, Doctor, Sheriff, Prostitute
        self.night_roles = ['Mafia', 'Doctor', 'Sheriff', 'Prostitute']  # Add new roles here
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
        active_players = [p for p in self.players if p.alive and isinstance(p.role, role_class) and not p.has_acted]

        if active_players:
            # Highlight active players
            for player in self.players:
                if player in active_players:
                    player.button.background_color = self.get_color(player.role.color)
                    player.button.disabled = False
                else:
                    player.button.disabled = True
            # Display prompt for current role
            role_prompt = Popup(title=f"{role_name}'s Turn",
                                content=Label(text=f"{role_name}, please select your target."),
                                size_hint=(None, None), size=(400, 200))
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

        # Create a ScrollView to accommodate all player options
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        scroll_view = ScrollView(size_hint=(1, None), size=(300, 400))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        if isinstance(player.role, Mafia):
            # Mafia cannot target other Mafia
            valid_targets = [t for t in self.players if t.alive and t != player and not isinstance(t.role, Mafia)]
        else:
            valid_targets = [t for t in self.players if t.alive and t != player]

        for target in valid_targets:
            btn = Button(text=f"{target.name} ({target.role.name})", size_hint_y=None, height=40)
            btn.bind(on_press=lambda btn_instance, t=target: self.set_night_action(player, t))
            grid.add_widget(btn)
        if isinstance(player.role, Doctor):
            # Allow self-healing
            btn = Button(text=f"{player.name} ({player.role.name}) (Self-Heal)", size_hint_y=None, height=40)
            btn.bind(on_press=lambda btn_instance, t=player: self.set_night_action(player, t))
            grid.add_widget(btn)

        scroll_view.add_widget(grid)
        content.add_widget(scroll_view)

        popup = Popup(title=f'{player.role.name} Action', content=content,
                      size_hint=(None, None), size=(350, 500))
        popup.open()
        player.action_popup = popup

    def set_night_action(self, player, target):
        player.action_target = target
        player.has_acted = True
        player.action_popup.dismiss()
        action_popup = Popup(title='Action Recorded', content=Label(text=f'{player.role.name} targets {target.name}.'),
                      size_hint=(None, None), size=(400, 200))
        action_popup.open()
        # Proceed to next role if applicable
        if isinstance(player.role, Mafia):
            # Proceed to next role immediately after one Mafia acts
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
        active_players = [p for p in self.players if p.alive and isinstance(p.role, role_class)]
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
        popup = Popup(title='Night Summary', content=Label(text=summary_text),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def voting_phase(self):
        # Enable voting for alive players not disabled by Prostitute
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
            popup = Popup(title='Cannot Vote',
                          content=Label(text='You cannot vote during the revote.'),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        # Create a ScrollView to accommodate all candidate options
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        scroll_view = ScrollView(size_hint=(1, None), size=(300, 400))
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        # Determine eligible candidates
        if self.current_phase == "Revote":
            # Only tied players can be voted for
            candidates = [p for p in self.tied_players if p.alive]
        else:
            # All alive players except self and disabled
            candidates = [p for p in self.players if p.alive and p != player and not p.disabled]

        for target in candidates:
            btn = Button(text=f"{target.name} ({target.role.name})", size_hint_y=None, height=40)
            btn.bind(on_press=lambda btn_instance, t=target: self.record_vote(player, t))
            grid.add_widget(btn)

        scroll_view.add_widget(grid)
        content.add_widget(scroll_view)

        popup = Popup(title=f'{player.name} Votes', content=content,
                      size_hint=(None, None), size=(350, 500))
        popup.open()
        player.vote_popup = popup

    def record_vote(self, player, target):
        target.votes += 1
        player.vote_popup.dismiss()
        popup = Popup(title='Vote Recorded', content=Label(text=f'{player.name} voted for {target.name}.'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
        player.button.disabled = True  # Disable the button after voting to prevent multiple votes

    def handle_tie(self):
        popup = Popup(
            title='Tie in Votes',
            content=Label(text='There is a tie. Proceed to revote.'),
            size_hint=(None, None), size=(400, 200)
        )
        popup.open()

        # Reset votes and proceed to revote among tied players
        max_votes = max(p.votes for p in self.players if p.alive)
        self.tied_players = [p for p in self.players if p.votes == max_votes and p.alive]

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
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        log_label = Label(text=log_text, size_hint_y=None)
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(log_label)
        content.add_widget(scroll_view)
        close_button = Button(text="Close", size_hint=(1, 0.1))
        content.add_widget(close_button)
        popup = Popup(title='Logbook', content=content,
                      size_hint=(None, None), size=(500, 500))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    MafiaApp().run()
