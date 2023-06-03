import pygame
import pygame as pyg

from Visualiser2.config import Config
from Visualiser2.utils.spritesheet import SpriteSheet
from game.utils.vector import Vector


class ByteSprite(pyg.sprite.Sprite):
    active_sheet: list[pyg.Surface]  # The current spritesheet being used.
    spritesheets: list[list[pyg.Surface]]
    object_type: int
    layer: int
    rect: pyg.Rect
    screen: pyg.Surface
    __frame_index: int  # Selects the sprite from the spritesheet to be used. Used for animation
    __config: Config = Config()

    def __init__(self, screen: pyg.Surface, filename: str, num_of_states: int, colorkey: pygame.Color | None,
                 object_type: int, layer: int, top_left: Vector = Vector(0, 0)):
        # Add implementation here for selecting the sprite sheet to use
        super().__init__()
        self.spritesheet_parser: SpriteSheet = SpriteSheet(filename)
        self.spritesheets = [self.spritesheet_parser.load_strip(
            pyg.Rect(0, self.__config.TILE_SIZE * row, self.__config.TILE_SIZE, self.__config.TILE_SIZE * (row + 1)),
            self.__config.NUMBER_OF_FRAMES_PER_TURN, colorkey)
            for row in range(num_of_states)]

        self.spritesheets = [
            [frame := pyg.transform.scale(frame, (self.__config.TILE_SIZE * self.__config.SCALE,) * 2) for frame in
             sheet] for sheet in self.spritesheets]

        self.rect = pyg.Rect(top_left.as_tuple(), (self.__config.TILE_SIZE * self.__config.SCALE,) * 2)

        self.active_sheet = self.spritesheets[0]
        self.object_type = object_type
        self.screen = screen
        self.layer = layer

    @property
    def active_sheet(self):
        return self.__active_sheet

    @property
    def spritesheets(self):
        return self.__spritesheets

    @property
    def object_type(self):
        return self.__object_type

    @property
    def layer(self):
        return self.__layer

    @property
    def rect(self):
        return self.__rect

    @property
    def screen(self):
        return self.__screen

    @active_sheet.setter
    def active_sheet(self, sheet: list[pyg.Surface]) -> None:
        if sheet is None or not isinstance(sheet, list) and \
                any(map(lambda sprite: not isinstance(sprite, pyg.Surface), sheet)):
            raise ValueError(f'{self.__class__.__name__}.active_sheet must be a list of pyg.Surface objects.')
        self.__active_sheet = sheet

    @spritesheets.setter
    def spritesheets(self, spritesheets: list[list[pyg.Surface]]) -> None:
        if spritesheets is None or (
                not isinstance(spritesheets, list) or any(map(lambda sheet: not isinstance(sheet, list), spritesheets))
                or any([any(map(lambda sprite: not isinstance(sprite, pyg.Surface), sheet))
                        for sheet in spritesheets])):
            raise ValueError(f'{self.__class__.__name__}.spritesheets must be a list of lists of pyg.Surface objects.')

        self.__spritesheets = spritesheets

    @object_type.setter
    def object_type(self, object_type: int) -> None:
        if object_type is None or not isinstance(object_type, int):
            raise ValueError(f'{self.__class__.__name__}.object_type must be an int.')

        if object_type < 0:
            raise ValueError(f'{self.__class__.__name__}.object_type can\'t be negative.')
        self.__object_type = object_type

    @layer.setter
    def layer(self, layer: int) -> None:
        if layer is None or not isinstance(layer, int):
            raise ValueError(f'{self.__class__.__name__}.layer must be an int.')

        if layer < 0:
            raise ValueError(f'{self.__class__.__name__}.layer can\'t be negative.')
        self.__layer = layer

    @rect.setter
    def rect(self, rect: pyg.Rect):
        if rect is None or not isinstance(rect, pyg.Rect):
            raise ValueError(f'{self.__class__.__name__}.rect must be a pyg.Rect object.')
        self.__rect = rect

    @screen.setter
    def screen(self, screen: pyg.Surface):
        if screen is None or not isinstance(screen, pyg.Surface):
            raise ValueError(f'{self.__class__.__name__}.screen must be a pyg.Screen object.')
        self.__screen = screen

    def select_active_sheet(self, data: dict, layer: int, pos: Vector) -> None:
        self.__frame_index = 0  # Starts the new spritesheet at the beginning

        # The coordinates for the top left of the rectangle of the sheet to be used
        self.rect.topleft = (
        pos.x * self.__config.TILE_SIZE * self.__config.SCALE + self.__config.GAME_BOARD_MARGIN_LEFT,
        pos.y * self.__config.TILE_SIZE * self.__config.SCALE + self.__config.GAME_BOARD_MARGIN_TOP)
        # Add implementation here for selecting the sprite sheet to use

    def render(self, layer: int):
        if layer is None or layer != self.layer:
            return

        # Places the given sprite at the rectangle's location
        self.screen.blit(self.active_sheet[self.__frame_index], self.rect)

        # selects the next sprite for the next frame
        self.__frame_index = (self.__frame_index + 1) % self.__config.NUMBER_OF_FRAMES_PER_TURN
