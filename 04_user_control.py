#! /usr/bin/env python3
"""02_draw_sprites.py - Opening a window in Arcade"""
import arcade
from arcade import key

# Constraints
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5


class Player(arcade.Sprite):
    """A class to encapsulate the player sprite."""

    def update(self):
        """ Move the player"""
        # Check for out of bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1


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
        self.up_pressed = False
        self.down_pressed = False

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

        for coordinate in coordinate_list:
            # Add a crate to the ground.
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
            )
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

    def on_draw(self):
        """Render the screen."""
        # Clears screen to the background color
        arcade.start_render()

        # Draw scene
        self.scene.draw()

    def on_key_press(self, button: int, modifiers: int):
        """Called whenever a key is pressed."""
        if button == key.UP or button == key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif button == key.DOWN or button == key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif button == key.LEFT or button == key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif button == key.RIGHT or button == key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, button: int, modifiers: int):
        """Called when the user releases a key."""
        if button == key.UP or button == key.W:
            self.player_sprite.change_y = 0
        elif button == key.DOWN or button == key.S:
            self.player_sprite.change_y = 0
        elif button == key.LEFT or button == key.A:
            self.player_sprite.change_x = 0
        elif button == key.RIGHT or button == key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time: float):
        """Movement and game logic."""

        # Move the player with the physics engine
        self.physics_engine.update()


def main():
    """Main program code."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
