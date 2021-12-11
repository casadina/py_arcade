#! /usr/bin/env python3
"""ladders_animated_moving_platforms.py - Add moving platforms and ladders."""

import collections
import os
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
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 30

# Player starting position
PLAYER_START_X = SPRITE_PIXEL_SIZE * TILE_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING

# Constants used to track player's direction
RIGHT_FACING = 0
LEFT_FACING = 1

# Layer names from our TileMap
LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_DONT_TOUCH = "Don't Touch"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"


def load_texture_pair(filename):
    """Load a texture pair, with the second being a mirror image."""
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class PhysicsEngine(arcade.PhysicsEnginePlatformer):
    """A slightly modified platformer physics engine."""
    def can_jump(self, y_distance: float = 5, x_distance: float = 5) -> bool:
        """
        Method that looks to see if there is a floor under or if the player can wall jump.

        :returns: True if there is a platform below us
        :rtype: bool
        """

        # Move down to see if we are on a platform
        self.player_sprite.center_y -= y_distance

        # Check for wall hit
        y_hit_list = arcade.check_for_collision_with_lists(
            self.player_sprite, self.walls + self.platforms
        )

        self.player_sprite.center_y += y_distance

        # Move left to see if we are next to a wall
        self.player_sprite.center_x -= x_distance

        # Check for left wall hit
        left_hit_list = arcade.check_for_collision_with_lists(
            self.player_sprite, self.walls + self.platforms
        )

        self.player_sprite.center_x += x_distance

        # Move right to see if we are next to a wall
        self.player_sprite.center_x += x_distance

        # Check for left wall hit
        right_hit_list = arcade.check_for_collision_with_lists(
            self.player_sprite, self.walls + self.platforms
        )

        self.player_sprite.center_x -= x_distance

        possible = (len(y_hit_list) > 0,
                    len(left_hit_list) > 0,
                    len(right_hit_list) > 0)

        if True in possible:
            print(possible)
            return True
        else:
            return False


class FPSCounter:
    """A class to detect frames per second."""
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        """Determine tick amount."""
        t_1 = time.perf_counter()
        dt = t_1 - self.time
        self.time = t_1
        self.frame_times.append(dt)

    def get_fps(self) -> float:
        """Return FPS as a float."""
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        return len(self.frame_times) / sum(self.frame_times)


class Player(arcade.Sprite):
    """A class to encapsulate the player sprite."""

    def __init__(self):
        super().__init__()

        self.character_face_direction = RIGHT_FACING

        # Flipping images
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Tracking state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # --- Load Textures ---

        main_path = ":resources:images/animated_characters/male_person/malePerson"

        # Load textures
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Load textures for walking
        self.walk_textures = [
            load_texture_pair(f"{main_path}_walk{i}.png") for i in range(8)]

        # Load textures for climbing
        self.climbing_textures = [
            arcade.load_texture(f"{main_path}_climb{i}.png") for i in range(2)]

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used.
        # Alternate ideas:
        # [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

    def show_direction(self):
        """Show player's direction."""
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

    def show_climbing(self):
        """Shows climbing animation"""
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return True
        else:
            return False

    def show_jumping(self):
        """Shows jumping animation."""
        if self.change_y != 0 and not self.is_on_ladder and not self.jumping:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return True

    def show_idle(self):
        """Shows idle animation."""
        if self.change_x == 0 and not self.climbing:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return True

    def show_walking(self):
        """Shows walking animation."""
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]
        return True

    def update_animation(self, delta_time: float = 1 / 60):
        """Updates the player animation."""
        print(self.climbing)
        # Check for out of bounds
        self.left = max(self.left, 0)

        self.show_direction()
        if self.show_climbing():
            return
        elif self.show_jumping():
            return
        elif self.show_idle():
            return
        else:
            self.show_walking()


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        """Call the parent class and set up the window."""
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

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

        # Keys are set as a tuple for easier access
        self.vertical = (key.UP, key.W, key.DOWN, key.S)
        self.up = (key.UP, key.W)
        self.down = (key.DOWN, key.S)
        self.left = (key.LEFT, key.A)
        self.right = (key.RIGHT, key.D)

        # Our TileMap Object
        self.tile_map = None

        # Right edge of the map
        self.end_of_map = 0

        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over_sound = arcade.load_sound(":resources:sounds/gameover1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Set-up the game here. Call this function to restart the game."""

        # Setup the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = f":resources:tiled_maps/map_with_ladders.json"

        # Layer specific options are defined on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DONT_TOUCH: {
                "use_spatial_hash": True,
             },
        }

        # Read in tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene
        # Automatically adds all layers as SpriteLists in proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.player_sprite = Player()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)

        # Set up game information for GUI
        self.score = 0
        self.lives_left = 5

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Create the physics engine
        self.physics_engine = PhysicsEngine(
            self.player_sprite,
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS],
            gravity_constant=GRAVITY,
            ladders=self.scene[LAYER_NAME_LADDERS],
            walls=self.scene[LAYER_NAME_PLATFORMS]
        )

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

    def display_gui_info(self):
        """Display GUI information."""
        arcade.draw_rectangle_filled(center_x=SCREEN_WIDTH / 14,
                                     center_y=SCREEN_HEIGHT - SCREEN_HEIGHT / 10,
                                     width=SCREEN_WIDTH / 7,
                                     height=SCREEN_HEIGHT / 4,
                                     color=arcade.color.IRRESISTIBLE,
                                     )
        self.gui_label("Score", self.score, 0, 95)
        self.gui_label("Coins Left", self.coins_left, 0, 90)
        self.gui_label("Time", round(self.timer), 0, 85)
        self.gui_label("Lives", self.lives_left, 0, 80)
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
        self.display_gui_info()
        self.fps.tick()

    def on_key_press(self, button: int, modifiers: int):
        """Called whenever a key is pressed."""
        if button in self.up:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
                self.player_sprite.is_on_ladder = True
            elif self.physics_engine.can_jump(128):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif button in self.down:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif button in self.left:
            self.left_pressed = True
        elif button in self.right:
            self.right_pressed = True

    def on_key_release(self, button: int, modifiers: int):
        """Called when the user releases a key."""
        if button in self.vertical and self.physics_engine.is_on_ladder():
            self.player_sprite.change_y = 0
        else:
            self.player_sprite.is_on_ladder = False
        if button in self.left:
            self.left_pressed = False
        elif button in self.right:
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
        """Ensure the camera is centered on the player."""
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

        self.camera.move_to(player_centered, 0.2)

    def player_coin_collision(self):
        """
        Detects player collision with coins, then removes the coin sprite.
        This will play a sound and add 1 to the score.
        """
        # Detect coin collision
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_COINS]
        )

        # Loop through each coin we hit and remove it
        for coin in coin_hit_list:
            # Figure out point value
            if "Points" not in coin.properties:
                print("Warning, collected a coin without a Points property.")
            else:
                points = int(coin.properties["Points"])
                self.score += points

            # Remove the coin and add to score
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)

    def reset_player(self):
        """Reset's player to start position."""
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y

    def stop_player(self):
        """Stop player movement."""
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

    def game_over(self):
        """Sets game over and resets position."""
        self.stop_player()
        self.reset_player()
        self.lives_left -= 1

        arcade.play_sound(self.game_over_sound)

    def fell_off_map(self):
        """Detect if the player fell off the map and then reset position if so."""
        if self.player_sprite.center_y < -100:
            self.game_over()

    def touched_dont_touch(self):
        """Detect collision on Don't Touch layer. Reset player if collision."""
        if arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_DONT_TOUCH]
        ):
            self.game_over()

    def at_end_of_level(self):
        """Checks if player at end of level, and if so, load the next level."""
        if self.player_sprite.center_x >= self.end_of_map:
            self.level += 1

            # Load the next level
            self.setup()

    def update(self, delta_time: float):
        """Movement and game logic."""
        self.timer += delta_time

        # Move the player with the physics engine
        self.update_player_velocity()
        self.player_sprite.update_animation()
        self.physics_engine.update()

        self.scene.update_animation(
            delta_time, [LAYER_NAME_COINS, LAYER_NAME_BACKGROUND]
        )
        self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

        # Detect collisions and level state
        self.player_coin_collision()
        self.fell_off_map()

        # Position the camera
        self.center_camera_to_player()


def main():
    """Main program code."""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
