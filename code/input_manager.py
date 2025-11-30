import pygame

_DEADZONE = 0.2
_TOUCH_MOVE_THRESHOLD = 0.02
_MAX_TOUCH_DISTANCE = 0.25


class InputManager:
    """Aggregates keyboard, touch, and gamepad input into a unified control state."""

    def __init__(self, screen_size):
        self.screen_width, self.screen_height = screen_size
        self.gameplay_active = False

        # Aggregated control state
        self._move_vector = pygame.math.Vector2()
        self._gamepad_axes = pygame.math.Vector2()
        self._touch_move_vector = pygame.math.Vector2()
        self.attack_active = False
        self.magic_active = False

        # Event-based toggles
        self._start_requested = False
        self._menu_toggle_requested = False
        self._weapon_switch_requested = False
        self._magic_switch_requested = False
        self._menu_nav = 0
        self._confirm_requested = False
        self._primary_scheme = None
        self._quit_requested = False

        # Touch bookkeeping
        self._touch_move_id = None
        self._touch_move_origin = pygame.math.Vector2()
        self._touch_attack_ids = set()
        self._touch_magic_ids = set()

        # Gamepad bookkeeping
        pygame.joystick.init()
        self._joysticks = []
        self._gamepad_attack = False
        self._gamepad_magic = False
        self._refresh_joysticks()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_gameplay_active(self, is_active: bool):
        self.gameplay_active = is_active
        if not is_active:
            self._clear_touch_inputs()

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event.key)
        elif event.type == pygame.FINGERDOWN:
            self._handle_touch_down(event)
        elif event.type == pygame.FINGERMOTION:
            self._handle_touch_motion(event)
        elif event.type == pygame.FINGERUP:
            self._handle_touch_up(event)
        elif event.type == pygame.JOYAXISMOTION:
            self._handle_joy_axis(event)
        elif event.type == pygame.JOYBUTTONDOWN:
            self._handle_joy_button(event.button, pressed=True)
        elif event.type == pygame.JOYBUTTONUP:
            self._handle_joy_button(event.button, pressed=False)
        elif event.type == pygame.JOYHATMOTION:
            self._handle_joy_hat(event)
        elif event.type == pygame.JOYDEVICEADDED:
            self._refresh_joysticks()
        elif event.type == pygame.JOYDEVICEREMOVED:
            self._refresh_joysticks()

    def update(self):
        """Recompute continuous control values each frame."""
        keys = pygame.key.get_pressed()
        keyboard_move = pygame.math.Vector2()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            keyboard_move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            keyboard_move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            keyboard_move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            keyboard_move.x += 1

        combined = keyboard_move + self._gamepad_axes + self._touch_move_vector
        if combined.length_squared() > 1:
            combined = combined.normalize()
        self._move_vector = combined

        keyboard_attack = keys[pygame.K_h]
        keyboard_magic = keys[pygame.K_j]
        self.attack_active = (
            keyboard_attack
            or self._gamepad_attack
            or bool(self._touch_attack_ids)
        )
        self.magic_active = (
            keyboard_magic
            or self._gamepad_magic
            or bool(self._touch_magic_ids)
        )

    def get_move_vector(self):
        return self._move_vector

    def get_primary_scheme(self):
        return self._primary_scheme

    def consume_start_request(self) -> bool:
        if self._start_requested:
            self._start_requested = False
            return True
        return False

    def consume_menu_toggle(self) -> bool:
        if self._menu_toggle_requested:
            self._menu_toggle_requested = False
            return True
        return False

    def consume_weapon_switch(self) -> bool:
        if self._weapon_switch_requested:
            self._weapon_switch_requested = False
            return True
        return False

    def consume_magic_switch(self) -> bool:
        if self._magic_switch_requested:
            self._magic_switch_requested = False
            return True
        return False

    def consume_menu_nav(self) -> int:
        nav = self._menu_nav
        self._menu_nav = 0
        return nav

    def consume_confirm_action(self) -> bool:
        if self._confirm_requested:
            self._confirm_requested = False
            return True
        return False

    def consume_quit_request(self) -> bool:
        if self._quit_requested:
            self._quit_requested = False
            return True
        return False

    # ------------------------------------------------------------------
    # Internal handlers
    # ------------------------------------------------------------------
    def _handle_keydown(self, key):
        if key == pygame.K_SPACE:
            self._start_requested = True
            self._confirm_requested = True
            self._set_primary_scheme('keyboard')
        elif key == pygame.K_ESCAPE:
            self._menu_toggle_requested = True
            self._set_primary_scheme('keyboard')
        elif key in (pygame.K_RETURN, pygame.K_z):
            self._confirm_requested = True
            self._set_primary_scheme('keyboard')
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._menu_nav = 1
            self._set_primary_scheme('keyboard')
        elif key in (pygame.K_LEFT, pygame.K_a):
            self._menu_nav = -1
            self._set_primary_scheme('keyboard')
        elif key == pygame.K_k:
            self._weapon_switch_requested = True
            self._set_primary_scheme('keyboard')
        elif key == pygame.K_l:
            self._magic_switch_requested = True
            self._set_primary_scheme('keyboard')
        elif key == pygame.K_q:
            self._quit_requested = True
            self._set_primary_scheme('keyboard')

    def _handle_keyup(self, key):
        # Currently nothing to do on key release; kept for future use.
        pass

    def _handle_touch_down(self, event):
        if not self.gameplay_active:
            self._start_requested = True
            self._set_primary_scheme('touch')
            return

        x = event.x
        y = event.y
        finger_id = event.finger_id

        if x <= 0.45 and self._touch_move_id is None:
            self._touch_move_id = finger_id
            self._touch_move_origin.update(x, y)
            self._touch_move_vector.update(0, 0)
        elif x >= 0.55:
            if y < 0.5:
                self._touch_magic_ids.add(finger_id)
            else:
                self._touch_attack_ids.add(finger_id)
        else:
            # Center tap toggles menu
            self._menu_toggle_requested = True
            self._set_primary_scheme('touch')
        if x <= 0.2 and y <= 0.2:
            self._quit_requested = True
            self._set_primary_scheme('touch')

    def _handle_touch_motion(self, event):
        if event.finger_id != self._touch_move_id:
            return
        dx = event.x - self._touch_move_origin.x
        dy = event.y - self._touch_move_origin.y
        dx = max(-_MAX_TOUCH_DISTANCE, min(_MAX_TOUCH_DISTANCE, dx))
        dy = max(-_MAX_TOUCH_DISTANCE, min(_MAX_TOUCH_DISTANCE, dy))
        if abs(dx) < _TOUCH_MOVE_THRESHOLD and abs(dy) < _TOUCH_MOVE_THRESHOLD:
            self._touch_move_vector.update(0, 0)
            return
        normalized = pygame.math.Vector2(
            dx / _MAX_TOUCH_DISTANCE,
            -dy / _MAX_TOUCH_DISTANCE
        )
        if normalized.length_squared() > 1:
            normalized = normalized.normalize()
        self._touch_move_vector = normalized

    def _handle_touch_up(self, event):
        finger_id = event.finger_id
        was_attack = finger_id in self._touch_attack_ids
        was_magic = finger_id in self._touch_magic_ids
        if finger_id == self._touch_move_id:
            self._touch_move_id = None
            self._touch_move_vector.update(0, 0)
        self._touch_attack_ids.discard(finger_id)
        self._touch_magic_ids.discard(finger_id)
        if was_attack or was_magic:
            self._confirm_requested = True
            self._set_primary_scheme('touch')

    def _handle_joy_axis(self, event):
        if event.axis == 0:
            self._gamepad_axes.x = self._apply_deadzone(event.value)
            if event.value <= -0.6:
                self._menu_nav = -1
            elif event.value >= 0.6:
                self._menu_nav = 1
            if event.value != 0:
                self._set_primary_scheme('gamepad')
        elif event.axis == 1:
            self._gamepad_axes.y = self._apply_deadzone(event.value)
            if event.value != 0:
                self._set_primary_scheme('gamepad')

    def _handle_joy_button(self, button, pressed):
        if button == 0:  # A / Cross
            self._gamepad_attack = pressed
            if pressed:
                self._confirm_requested = True
                self._set_primary_scheme('gamepad')
        elif button == 1:  # B / Circle
            self._gamepad_magic = pressed
            if pressed:
                self._set_primary_scheme('gamepad')
        elif button in (6, 7):  # Back / Start
            if pressed:
                if button == 7:
                    self._start_requested = True
                else:
                    self._menu_toggle_requested = True
                self._set_primary_scheme('gamepad')
        elif button == 2 and pressed:
            self._weapon_switch_requested = True
            self._set_primary_scheme('gamepad')
        elif button == 3 and pressed:
            self._magic_switch_requested = True
            self._set_primary_scheme('gamepad')
        elif button == 4 and pressed:
            self._quit_requested = True
            self._set_primary_scheme('gamepad')

    def _handle_joy_hat(self, event):
        x, _ = event.value
        if x != 0:
            self._menu_nav = int(x)
            self._set_primary_scheme('gamepad')

    def _apply_deadzone(self, value):
        return 0 if abs(value) < _DEADZONE else value

    def _refresh_joysticks(self):
        self._joysticks = []
        for idx in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(idx)
            joystick.init()
            self._joysticks.append(joystick)

    def _clear_touch_inputs(self):
        self._touch_move_id = None
        self._touch_move_vector.update(0, 0)
        self._touch_attack_ids.clear()
        self._touch_magic_ids.clear()

    def _set_primary_scheme(self, scheme):
        if not self._primary_scheme:
            self._primary_scheme = scheme
