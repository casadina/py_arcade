#! /usr/bin/env python3
"""camera.py - Adding a camera for bigger levels."""

import collections
import time

import arcade
from arcade import key

# Constraints
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Scale sprites from original size. 1 is original.
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        """Determine tick amount."""
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self) -> float:
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)


class Player(arcade.Sprite):
    """A class to encapsulate the player sprite."""

    def update(self):
        """ Move the player"""
        # Check for out of bounds
        if self.left < 0:
            self.left = 0


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """Call the parent class and set up the window."""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialize Scene and player
        self.scene, self.player_sprite = None, None

        # Initialize physics engine
        self.physics_engine = None

        # Track current state of key press
        self.left_pressed = False
        self.right_pressed = False

        # Set cameras. Separate needed due to scrolling issues.
        self.camera = None
        self.gui_camera = None

        # Game information
        self.score = 0
        self.lives_left = 0
        self.timer = 0
        self.fps = FPSCounter()

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set-up the game here. Call this function to restart the game."""

        # Initialize Scene
        self.scene = arcade.Scene()

        # Create sprite lists
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        # Player setup
        image_source = ":resources:images" \
                       "/animated_characters/female_adventurer" \
                       "/femaleAdventurer_idle.png"
        self.player_sprite = Player(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # Create the ground
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(
                ":resources:images/tiles/grassMid.png", TILE_SCALING
            )
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        # coordinates [x, y] used for crates
        coordinate_list = [[512, 96], [256, 96], [768, 96]]

        # Loop to add crates to the ground.
        for coordinate in coordinate_list:
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
            )
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        # Loop to place coins for character to pick up.
        for x in range(128, 1250, 256):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            coin.center_x = x
            coin.center_y = 96
            self.scene.add_sprite("Coins", coin)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )

        # Setup the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Set up game information for GUI
        self.score = 0

    @property
    def current_fps(self) -> float:
        """Determine current fps."""
        return self.fps.get_fps()

    @property
    def coins_left(self) -> int:
        """Determine coins remaining."""
        return len(self.scene["Coins"])

    @staticmethod
    def gui_label(text: str, var: any, x: int, y: int):
        """
        Simplify arcade.draw_text.

        Keyword arguments:
        text -- This is the label.
        var -- This is the variable value.
        x -- This is the percent point of the screen's x x that it will start at.
        y -- This is the percent point of the screen's y it will start at.
        """
        x, y = x / 100, y / 100
        arcade.draw_text(
            text=f"{text}: {var}",
            start_x=SCREEN_WIDTH * x, start_y=SCREEN_HEIGHT * y,
            color=arcade.csscolor.WHITE,
            font_size=18,
        )

    def gui_info(self):
        """Display GUI information."""
        self.gui_label("Score", self.score, 0, 95)
        self.gui_label("Coins Left", self.coins_left, 0, 90)
        self.gui_label("Time", round(self.timer), 0, 85)
        self.gui_label("FPS", round(self.current_fps), 90, 95)

    def on_draw(self):
        """Render the screen."""
        # Clears screen to the background color
        arcade.start_render()

        # Activate our Camera
        self.camera.use()

        # Draw scene
        self.scene.draw()

        # Activate GUI camera before elements.
        self.gui_camera.use()

        # Draw score while scrolling it along the screen.
        self.gui_info()
        self.fps.tick()

    def on_key_press(self, button: int, modifiers: int):
        """Called whenever a key is pressed."""
        if button == key.UP or button == key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif button == key.LEFT or button == key.A:
            self.left_pressed = True
        elif button == key.RIGHT or button == key.D:
            self.right_pressed = True

    def on_key_release(self, button: int, modifiers: int):
        """Called when the user releases a key."""
        if button == key.LEFT or button == key.A:
            self.left_pressed = False
        elif button == key.RIGHT or button == key.D:
            self.right_pressed = False

    def update_player_velocity(self):
        """Update velocity based on key state."""
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (
                self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
                self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time: float):
        """Movement and game logic."""
        # Move the player with the physics engine
        self.timer += delta_time
        self.update_player_velocity()
        self.player_sprite.update()
        self.physics_engine.update()

        # Detect coin collision
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        # Loop through each coin we hit and remove it
        for coin in coin_hit_list:
            # Remove the coin and add to score
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main program code."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
