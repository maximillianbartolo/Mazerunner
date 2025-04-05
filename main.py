# Maze runner game
__author__ = "Max Bartolo"
__version__ = "04/2/2025"

'''
flint sessions:
https://app.flintk12.com/activity/pygame-debug-le-1fe068/session/f56d77f7-57c0-4c3c-9a5d-f0d3baf0d90a
'''

import pygame
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)

class ResourceManager:
    def __init__(self):
        self.images = {}

    def load_image(self, name, path, size=None):
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        self.images[name] = image
        return image

    def get_image(self, name):
        return self.images.get(name)


class SoundManager:
    def __init__(self):
        # Initialize the mixer
        pygame.mixer.init()

        # Dictionary to store loaded sounds
        self.sounds = {}

        # Volume settings
        self.music_volume = 0.5
        self.sfx_volume = 0.7

    def load_sound(self, name, filepath):
        """
        Load a sound effect
        :param name: Identifier for the sound
        :param filepath: Path to the sound file
        """
        try:
            sound = pygame.mixer.Sound(filepath)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Could not load sound {name}: {e}")


    def play_sound(self, name, loops=0):
        """
        Play a sound effect
        :param name: Name of the sound to play
        :param loops: Number of times to repeat (-1 for infinite)
        """
        if name in self.sounds:
            self.sounds[name].set_volume(self.sfx_volume)
            self.sounds[name].play(loops)

    def set_sfx_volume(self, volume):
        """
        Set sound effects volume
        :param volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

class Wall(pygame.sprite.Sprite):
    """This class represents the bar at the bottom that the player controls """

    def __init__(self, x, y, width, height, color):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Make a BLUE wall, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x


class Token(pygame.sprite.Sprite):
    """This class represents collectible tokens the player can gather"""

    def __init__(self, x, y):
        """Constructor function"""

        # Call the parent's constructor
        super().__init__()

        # Create a token - a small yellow circle
        self.image = pygame.Surface([10, 10])
        self.image.fill((255, 255, 0))  # Yellow tokens

        # Make our token position the passed-in location
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    """ This class represents the player sprite """

    # Set speed vector
    change_x = 0
    change_y = 0

    def __init__(self, image, x):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Set the image
        self.image = image

        # Make our top-left corner the passed-in location
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 50  # Fixed y position or make it a parameter

    def changespeed(self, x, y):
        """ Change the speed of the player. Called with a keypress. """
        self.change_x += x
        self.change_y += y

    def move(self, walls):
        """ Find a new position for the player """

        # Move left/right
        self.rect.x += self.change_x

        # Did this update cause us to hit a wall?
        block_hit_list = pygame.sprite.spritecollide(self, walls, False)
        for block in block_hit_list:
            # If we are moving right, set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            else:
                # Otherwise if we are moving left, do the opposite
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, walls, False)
        for block in block_hit_list:
            # Reset our position based on the top/bottom of the object
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            else:
                self.rect.top = block.rect.bottom


class Room(object):
    """Base class for all rooms."""

    def __init__(self):
        """Constructor, create our lists."""
        self.wall_list = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.token_list = pygame.sprite.Group()  # Add token list to all rooms

    def generate_tokens(self, count=5):
        """Generate a number of tokens in random positions"""

        # Clear any existing tokens
        self.token_list.empty()

        # Create new tokens in random positions
        for i in range(count):
            # Keep trying until we find a valid position
            while True:
                x = random.randint(40, 740)
                y = random.randint(40, 540)

                # Create a temporary token to check collisions
                temp_token = Token(x, y)

                # Check if it collides with any walls
                wall_hit = pygame.sprite.spritecollideany(temp_token, self.wall_list)

                # If no collision, this is a good spot
                if wall_hit is None:
                    self.token_list.add(temp_token)
                    break


class MovingWall(Wall):
    def __init__(self, x, y, width, height, color):

        # Call the parent (Wall) constructor with all required arguments
        super().__init__(x, y, width, height, color)

        # Movement properties
        self.change_x = 0
        self.change_y = 2  # Set a default vertical speed

        # Boundary properties to control movement
        self.boundary_top = y  # Starting y position
        self.boundary_bottom = y + 200  # How far down it can move

        self.player = None
        self.level = None

    def update(self):
        # Move vertically
        self.rect.y += self.change_y

        # Reverse direction when hitting boundaries
        if self.rect.top <= self.boundary_top or self.rect.bottom >= self.boundary_bottom:
            self.change_y *= -1  # Reverse direction

        # Player collision logic (optional)
        collisions = 0
        if self.player:

            hit = pygame.sprite.collide_rect(self, self.player)
            if hit is True:
                self.player.rect.x = 30
                self.player.rect.y = 30
                collisions += 1
                return collisions

                # Boundary checks

        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1



class Room1(Room):
    """This creates all the walls in room 1"""

    def __init__(self):
        super().__init__()
        # Make the walls. (x_pos, y_pos, width, height)

        # This is a list of walls. Each is in the form [x, y, width, height]
        walls = [[0, 0, 20, 250, WHITE],
                 [0, 350, 20, 250, WHITE],
                 [780, 0, 20, 250, WHITE],
                 [780, 350, 20, 250, WHITE],
                 [20, 0, 760, 20, WHITE],
                 [20, 580, 760, 20, WHITE],
                 [390, 50, 20, 500, BLUE]
                 ]

        # Loop through the list. Create the wall, add it to the list
        for item in walls:
            wall = Wall(item[0], item[1], item[2], item[3], item[4])
            self.wall_list.add(wall)


class Room2(Room):
    """This creates all the walls in room 2"""

    def __init__(self):
        super().__init__()

        walls = [[0, 0, 20, 250, RED],
                 [0, 350, 20, 250, RED],
                 [780, 0, 20, 250, RED],
                 [780, 350, 20, 250, RED],
                 [20, 0, 760, 20, RED],
                 [20, 580, 760, 20, RED],
                 [190, 50, 20, 500, GREEN],
                 [590, 50, 20, 500, GREEN]
                 ]

        for item in walls:
            wall = Wall(item[0], item[1], item[2], item[3], item[4])
            self.wall_list.add(wall)
        walls = [[0, 0, 20, 250, PURPLE],
                 [0, 350, 20, 250, PURPLE],
                 [780, 0, 20, 250, PURPLE],
                 [780, 350, 20, 250, PURPLE],
                 [20, 0, 760, 20, PURPLE],
                 [20, 580, 760, 20, PURPLE]
                 ]

class Room3(Room):
    def __init__(self):
        super().__init__()

        # Define the walls for Room3
        walls = [[0, 0, 20, 250, PURPLE],
                 [0, 350, 20, 250, PURPLE],
                 [780, 0, 20, 250, PURPLE],
                 [780, 350, 20, 250, PURPLE],
                 [20, 0, 760, 20, PURPLE],
                 [20, 580, 760, 20, PURPLE]
                 ]

        # Add the walls to the wall list
        for item in walls:
            wall = Wall(item[0], item[1], item[2], item[3], item[4])
            self.wall_list.add(wall)

        # Add additional walls with different patterns
        for x in range(100, 800, 100):
            for y in range(50, 451, 300):
                wall = Wall(x, y, 20, 200, RED)
                self.wall_list.add(wall)

        for x in range(150, 700, 100):
            block = MovingWall(x, 200, 20, 200, WHITE)  # Positioned within screen
            block.boundary_top = 50  # Minimum y position
            block.boundary_bottom = 500  # Maximum y position
            block.change_y = 2  # Vertical speed
            block.player = None  # Will be set later
            block.level = self
            self.wall_list.add(block)

        # Add a custom moving wall


def generate_tokens(self, count=5):
    """Generate a number of tokens in random positions"""
    import random

    # Clear any existing tokens
    self.token_list.empty()

    # Create new tokens in random positions
    for i in range(count):
        # Keep trying until we find a valid position
        while True:
            x = random.randint(40, 740)
            y = random.randint(40, 540)

            # Create a temporary token to check collisions
            temp_token = Token(x, y)

            # Check if it collides with any walls
            wall_hit = pygame.sprite.spritecollideany(temp_token, self.wall_list)

            # If no collision, this is a good spot
            if wall_hit is None:
                self.token_list.add(temp_token)
                break


def main():
    """ Main Program """

    # Call this function so the Pygame library can initialize itself
    pygame.init()
    pygame.mixer.init()
    # Create an 800x600 sized screen
    screen = pygame.display.set_mode([800, 600])

    # Set the title of the window
    pygame.display.set_caption('Maze Runner')

    # Create a resource manager (if you want to use images)
    resources = ResourceManager()

    # Load player image (make sure the path is correct)

    # Preload multiple player images
    resources.load_image('default', 'player.png', (30, 30))
    resources.load_image('nixon', 'nixon.png', (30, 30))

    player_image=resources.load_image('default', 'player.png', (30, 30))

    player = Player(player_image, 50)
    movingsprites = pygame.sprite.Group()
    movingsprites.add(player)

    def change_player_image(player, resources, image_name, movingsprites):
        """
        Change the player's image dynamically

        :param player: Current player sprite
        :param resources: ResourceManager instance
        :param image_name: Name of the image to load
        :param movingsprites: Sprite group to manage
        """
        try:
            # Check if image exists in resources
            new_image = resources.get_image(image_name)

            if new_image is None:
                print(f"Image {image_name} not found in resources")
                return player

            # Create a new player with the new image
            new_player = Player(new_image, player.rect.x)

            # Copy the current player's position and speed
            new_player.rect.x = player.rect.x
            new_player.rect.y = player.rect.y
            new_player.change_x = player.change_x
            new_player.change_y = player.change_y

            # Replace the old player in the sprite group
            movingsprites.remove(player)
            movingsprites.add(new_player)

            return new_player

        except Exception as e:
            print(f"Error changing player image: {e}")
            return player

    '''Initialize Sound Manager'''
    sound_manager = SoundManager()

    # Load sounds
    sound_manager.load_sound('token_collect', 'blip1.wav')

    # Add a score variable
    score = 0

    rooms = []

    room = Room1()
    rooms.append(room)

    room = Room2()
    rooms.append(room)

    room = Room3()
    rooms.append(room)

    # Generate tokens in each room
    for room in rooms:
        room.generate_tokens()

    current_room_no = 0
    current_room = rooms[current_room_no]

    clock = pygame.time.Clock()
    for room in rooms:
        # If the room has moving walls, set the player
        for wall in room.wall_list:
            if isinstance(wall, MovingWall):
                wall.player = player


    done = False

    while not done:
        # --- Event Processing ---

        if player.rect.x > 745 and player.rect.y > 545:
            if current_room_no == 1:
                # Ensure 'nixon' image is loaded before changing
                if resources.get_image('nixon'):
                    player = change_player_image(player, resources, 'nixon', movingsprites)
                else:
                    print("Nixon image not loaded")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.changespeed(-5, 0)
                if event.key == pygame.K_RIGHT:
                    player.changespeed(5, 0)
                if event.key == pygame.K_UP:
                    player.changespeed(0, -5)
                if event.key == pygame.K_DOWN:
                    player.changespeed(0, 5)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.changespeed(5, 0)
                if event.key == pygame.K_RIGHT:
                    player.changespeed(-5, 0)
                if event.key == pygame.K_UP:
                    player.changespeed(0, 5)
                if event.key == pygame.K_DOWN:
                    player.changespeed(0, -5)

        # Update moving walls
        for wall in current_room.wall_list:
            if isinstance(wall, MovingWall):
                wall.update()

        # --- Game Logic ---
        player.move(current_room.wall_list)

        # Check if player has collected any tokens

        # Add to score for each token collected
        token_hit_list = pygame.sprite.spritecollide(player, current_room.token_list, True)
        for token in token_hit_list:
            score += 10
            sound_manager.play_sound('token_collect')
              # Each token worth 10 points

        # Room transition logic
        if player.rect.x < -15:
            if current_room_no == 0:
                current_room_no = 2
                current_room = rooms[current_room_no]
                player.rect.x = 790
            elif current_room_no == 2:
                current_room_no = 1
                current_room = rooms[current_room_no]
                player.rect.x = 790
            else:
                current_room_no = 0
                current_room = rooms[current_room_no]
                player.rect.x = 790

        if player.rect.x > 801:
            if current_room_no == 0:
                current_room_no = 1
                current_room = rooms[current_room_no]
                player.rect.x = 0
            elif current_room_no == 1:
                current_room_no = 2
                current_room = rooms[current_room_no]
                player.rect.x = 0
            else:
                current_room_no = 0
                current_room = rooms[current_room_no]
                player.rect.x = 0



        # --- Drawing ---
        screen.fill(BLACK)

        movingsprites.draw(screen)
        current_room.wall_list.draw(screen)
        current_room.token_list.draw(screen)  # Draw the tokens

        # Display score
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {score} Room: {current_room_no + 1} x: {player.rect.x} y: {player.rect.y}", True, BLACK)
        screen.blit(text, (0, 0))

        pygame.display.flip()
        clock.tick(60)


    pygame.quit()


if __name__ == "__main__":
    main()
