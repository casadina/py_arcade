#! /usr/bin/env python3
"""02_draw_sprites.py - Opening a window in Arcade"""
import arcade

# Constraints
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

CHARACTER_SCALING = 1
TILE_SCALING = 0.5


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """Call the parent class and set up the window."""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Sprite lists
        self.wall_list = None
        self.player_list = None

        self.player_sprite = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set-up the game here. Call this function to restart the game."""
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        # Player setup
        image_source = ":resources:images" \
                       "/animated_characters/female_adventurer" \
                       "/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

        # Create the ground
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(
                ":resources:images/tiles/grassMid.png",
                TILE_SCALING
            )
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        # coordinates [x, y] used for crates
        coordinate_list = [[512, 96], [256, 96], [768, 96]]

        for coordinate in coordinate_list:
            # Add a crate to the ground.
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png",
                TILE_SCALING
            )
            wall.position = coordinate
            self.wall_list.append(wall)

    def on_draw(self):
        """Render the screen."""
        # Clears screen to the background color
        arcade.start_render()

        self.wall_list.draw()
        self.player_list.draw()


def main():
    """Main program code."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
