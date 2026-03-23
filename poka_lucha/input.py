from enum import Enum
from typing import Callable, Dict, List, Tuple
import pygame

class InputAction(Enum):
    """Enumeration of possible game actions."""
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    PUNCH = "punch"
    KICK = "kick"
    BLOCK = "block"
    PAUSE = "pause"


class InputHandler:
    """Handles input from keyboard and game controllers, routed per player."""

    def __init__(self):
        # key → (player_index, action)
        self.key_bindings: Dict[int, Tuple[int, InputAction]] = {}
        # button → action (player determined by joystick id)
        self.controller_bindings: Dict[int, InputAction] = {}
        # joystick id → player index
        self.joystick_players: Dict[int, int] = {}
        # joystick id → Joystick object (must be kept alive)
        self._joysticks: Dict[int, pygame.joystick.JoystickType] = {}
        # player index → set of currently pressed actions
        self.pressed_actions: Dict[int, set] = {}
        # callbacks receive the player index that triggered the action
        self.action_callbacks: Dict[InputAction, List[Callable[[int], None]]] = {}

        self._setup_default_bindings()

    def _setup_default_bindings(self):
        """Set up default keyboard and controller mappings."""
        self.key_bindings = {
            # Player 0: QASD + E
            pygame.K_a:      (0, InputAction.MOVE_LEFT),
            pygame.K_d:      (0, InputAction.MOVE_RIGHT),
            pygame.K_q:      (0, InputAction.PUNCH),
            pygame.K_w:      (0, InputAction.KICK),
            pygame.K_e:      (0, InputAction.BLOCK),
            pygame.K_ESCAPE: (0, InputAction.PAUSE),
            # Player 1: UJIL + O
            pygame.K_j:      (1, InputAction.MOVE_LEFT),
            pygame.K_l:      (1, InputAction.MOVE_RIGHT),
            pygame.K_u:      (1, InputAction.PUNCH),
            pygame.K_i:      (1, InputAction.KICK),
            pygame.K_o:      (1, InputAction.BLOCK),
        }

        # Controller button bindings (pygame joystick button indices)
        self.controller_bindings = {
            0: InputAction.PUNCH,   # A button
            1: InputAction.KICK,    # B button
            2: InputAction.BLOCK,   # X button
            7: InputAction.PAUSE,   # Start button
        }

    def assign_joystick(self, joy_id: int, player: int):
        """Manually assign a joystick id to a player index."""
        self.joystick_players[joy_id] = player

    def register_action_callback(self, action: InputAction, callback: Callable[[int], None]):
        """Register a callback for an action. Callback receives the player index."""
        if action not in self.action_callbacks:
            self.action_callbacks[action] = []
        self.action_callbacks[action].append(callback)

    def handle_event(self, event: pygame.event.Event):
        """Process input events."""
        if event.type == pygame.KEYDOWN:
            self._handle_key_down(event.key)
        elif event.type == pygame.KEYUP:
            self._handle_key_up(event.key)
        elif event.type == pygame.JOYBUTTONDOWN:
            self._handle_button_down(event.joy, event.button)
        elif event.type == pygame.JOYBUTTONUP:
            self._handle_button_up(event.joy, event.button)
        elif event.type == pygame.JOYAXISMOTION:
            self._handle_axis_motion(event.joy, event.axis, event.value)
        elif event.type == pygame.JOYDEVICEADDED:
            joy_id = event.device_index
            joystick = pygame.joystick.Joystick(joy_id)
            self._joysticks[joy_id] = joystick
            if joy_id not in self.joystick_players:
                self.joystick_players[joy_id] = len(self.joystick_players)

    def _player_actions(self, player: int) -> set:
        if player not in self.pressed_actions:
            self.pressed_actions[player] = set()
        return self.pressed_actions[player]

    def _handle_key_down(self, key: int):
        if key in self.key_bindings:
            player, action = self.key_bindings[key]
            self._trigger_action(player, action)

    def _handle_key_up(self, key: int):
        if key in self.key_bindings:
            player, action = self.key_bindings[key]
            self._player_actions(player).discard(action)

    def _handle_button_down(self, joy_id: int, button: int):
        if button in self.controller_bindings and joy_id in self.joystick_players:
            player = self.joystick_players[joy_id]
            self._trigger_action(player, self.controller_bindings[button])

    def _handle_button_up(self, joy_id: int, button: int):
        if button in self.controller_bindings and joy_id in self.joystick_players:
            player = self.joystick_players[joy_id]
            self._player_actions(player).discard(self.controller_bindings[button])

    AXIS_DEADZONE = 0.2

    def _handle_axis_motion(self, joy_id: int, axis: int, value: float):
        """Handle analog stick motion. Axis 0 = left stick X → MOVE_LEFT/MOVE_RIGHT."""
        if axis != 0 or joy_id not in self.joystick_players:
            return
        player = self.joystick_players[joy_id]
        actions = self._player_actions(player)
        if value < -self.AXIS_DEADZONE:
            actions.add(InputAction.MOVE_LEFT)
            actions.discard(InputAction.MOVE_RIGHT)
        elif value > self.AXIS_DEADZONE:
            actions.add(InputAction.MOVE_RIGHT)
            actions.discard(InputAction.MOVE_LEFT)
        else:
            actions.discard(InputAction.MOVE_LEFT)
            actions.discard(InputAction.MOVE_RIGHT)

    def _trigger_action(self, player: int, action: InputAction):
        self._player_actions(player).add(action)
        if action in self.action_callbacks:
            for callback in self.action_callbacks[action]:
                callback(player)

    def is_action_pressed(self, action: InputAction, player: int) -> bool:
        """Check if an action is currently pressed for a given player."""
        return action in self.pressed_actions.get(player, set())
