import random
from typing import Self

from game.common.avatar import Avatar
from game.common.enums import *
from game.common.game_object import GameObject
from game.common.map.occupiable import Occupiable
from game.common.map.tile import Tile
from game.common.map.wall import Wall
from game.common.stations.occupiable_station import OccupiableStation
from game.common.stations.station import Station
from game.utils.vector import Vector


class GameBoard(GameObject):
    """
    `GameBoard Class Notes:`

    Map Size:
    ---------
        map_size is a Vector object, allowing you to specify the size of the (x, y) plane of the game board.
        For example, a Vector object with an 'x' of 5 and a 'y' of 7 will create a board 5 tiles wide and
        7 tiles long.

        Example:
        ::
            _ _ _ _ _  y = 0
            |       |
            |       |
            |       |
            |       |
            |       |
            |       |
            _ _ _ _ _  y = 6

    -----

    Locations:
    ----------
        This is the bulkiest part of the generation.

        The locations field is a dictionary with a key of a tuple of Vectors, and the value being a list of
        GameObjects (the key **must** be a tuple instead of a list because Python requires dictionary keys to be
        immutable).

        This is used to assign the given GameObjects the given coordinates via the Vectors. This is done in two ways:

        Statically:
            If you want a GameObject to be at a specific coordinate, ensure that the key-value pair is
            *ONE* Vector and *ONE* GameObject.
            An example of this would be the following:
            ::
                locations = { (vector_2_4) : [station_0] }

            In this example, vector_2_4 contains the coordinates (2, 4). (Note that this naming convention
            isn't necessary, but was used to help with the concept). Furthermore, station_0 is the
            GameObject that will be at coordinates (2, 4).

        Dynamically:
            If you want to assign multiple GameObjects to different coordinates, use a key-value
            pair of any length.

            **NOTE**: The length of the tuple and list *MUST* be equal, otherwise it will not
            work. In this case, the assignments will be random. An example of this would be the following:
            ::
                locations =
                {
                    (vector_0_0, vector_1_1, vector_2_2) : [station_0, station_1, station_2]
                }

            (Note that the tuple and list both have a length of 3).

            When this is passed in, the three different vectors containing coordinates (0, 0), (1, 1), or
            (2, 2) will be randomly assigned station_0, station_1, or station_2.

            If station_0 is randomly assigned at (1, 1), station_1 could be at (2, 2), then station_2 will be at (0, 0).
            This is just one case of what could happen.

        Lastly, another example will be shown to explain that you can combine both static and
        dynamic assignments in the same dictionary:
        ::
            locations =
                {
                    (vector_0_0) : [station_0],
                    (vector_0_1) : [station_1],
                    (vector_1_1, vector_1_2, vector_1_3) : [station_2, station_3, station_4]
                }

        In this example, station_0 will be at vector_0_0 without interference. The same applies to
        station_1 and vector_0_1. However, for vector_1_1, vector_1_2, and vector_1_3, they will randomly
        be assigned station_2, station_3, and station_4.

    -----

    Walled:
    -------
        This is simply a bool value that will create a wall barrier on the boundary of the game_board. If
        walled is True, the wall will be created for you.

        For example, let the dimensions of the map be (5, 7). There will be wall Objects horizontally across
        x = 0 and x = 4. There will also be wall Objects vertically at y = 0 and y = 6

        Below is a visual example of this, with 'x' being where the wall Objects are.

        Example:
        ::
            x x x x x   y = 0
            x       x
            x       x
            x       x
            x       x
            x       x
            x x x x x   y = 6
    """

    def __init__(self, seed: int | None = None, map_size: Vector = Vector(),
                 locations: dict[Vector, list[GameObject]] | None = None, walled: bool = False):

        super().__init__()
        # game_map is initially going to be None. Since generation is slow, call generate_map() as needed
        self.game_map: dict[Vector, list[Tile]] | None = None
        self.seed: int | None = seed
        random.seed(seed)
        self.object_type: ObjectType = ObjectType.GAMEBOARD
        self.event_active: int | None = None
        self.map_size: Vector = map_size
        # when passing Vectors as a tuple, end the tuple of Vectors with a comma so it is recognized as a tuple
        self.locations: dict | None = locations
        self.walled: bool = walled

    @property
    def seed(self) -> int:
        return self.__seed

    @seed.setter
    def seed(self, seed: int | None) -> None:
        if self.game_map is not None:
            raise RuntimeError(f'{self.__class__.__name__} variables cannot be changed once generate_map is run.')
        if seed is not None and not isinstance(seed, int):
            raise ValueError(
                f'{self.__class__.__name__}.seed must be an int. '
                f'It is a(n) {seed.__class__.__name__} with the value of {seed}.')
        self.__seed = seed

    @property
    def game_map(self) -> dict[Vector, list[Tile]] | None:
        return self.__game_map

    @game_map.setter
    def game_map(self, game_map: dict[Vector, list[Tile]] | None) -> None:
        if game_map is not None and (not isinstance(game_map, dict) or len(game_map) == 0 or
                                     any(map(lambda x: not isinstance(x, list), game_map.values())) or
                                     any([not isinstance(sublist[0], Tile) for sublist in game_map.values()])):
            raise ValueError(
                f'{self.__class__.__name__}.game_map must be a dict[Vector, list[Tile]].'
                f'It has a value of {game_map}.'
            )

        self.__game_map = game_map

    @property
    def map_size(self) -> Vector:
        return self.__map_size

    @map_size.setter
    def map_size(self, map_size: Vector) -> None:
        if self.game_map is not None:
            raise RuntimeError(f'{self.__class__.__name__} variables cannot be changed once generate_map is run.')
        if map_size is None or not isinstance(map_size, Vector):
            raise ValueError(
                f'{self.__class__.__name__}.map_size must be a Vector. '
                f'It is a(n) {map_size.__class__.__name__} with the value of {map_size}.')
        self.__map_size = map_size

    @property
    def locations(self) -> dict:
        return self.__locations

    @locations.setter
    def locations(self, locations: dict[tuple[Vector]:list[GameObject]] | None) -> None:
        if self.game_map is not None:
            raise RuntimeError(f'{self.__class__.__name__} variables cannot be changed once generate_map is run.')
        if locations is not None and not isinstance(locations, dict):
            raise ValueError(
                f'Locations must be a dict. The key must be a tuple of Vector Objects, '
                f'and the value a list of GameObject. '
                f'It is a(n) {locations.__class__.__name__} with the value of {locations}.')

        self.__locations = locations

    @property
    def walled(self) -> bool:
        return self.__walled

    @walled.setter
    def walled(self, walled: bool) -> None:
        if self.game_map is not None:
            raise RuntimeError(f'{self.__class__.__name__} variables cannot be changed once generate_map is run.')
        if walled is None or not isinstance(walled, bool):
            raise ValueError(
                f'{self.__class__.__name__}.walled must be a bool. '
                f'It is a(n) {walled.__class__.__name__} with the value of {walled}.')

        self.__walled = walled

    def generate_map(self) -> None:
        # Dictionary Init
        self.game_map = self.__map_init()

    def __map_init(self) -> dict[Vector, list[Tile]]:
        tile: list[Tile] = [Tile(), ]
        x: int = 0
        y: int = 0

        output: dict[Vector, list[Tile]] = {}

        for iteration in range(self.map_size.x * self.map_size.y):
            x = iteration % self.map_size.x

            coords: Vector = Vector(x, y)

            to_place: list[GameObject] | list = self.locations.get(coords, [])

            output.update({coords: [Tile(), ] + to_place})

            # Add walls
            if self.walled and (x == 0 or x == self.map_size.x or y == 0 or y == self.map_size.y):
                # add a Wall object to the tile to create border
                output[coords][0].occupied_by = Wall()

            if coords in self.locations.keys() and self.__can_place_validator(coords, tile):
                for index, obj in enumerate(self.locations[coords]):
                    output[coords][index].occupied_by = obj

                # this doesn't account for assigning multiple things in the stack
                # output[coords][1].occupied_by = self.locations[coords]

            # Increment coords
            if x == self.map_size.x - 1:
                x = 0
                y += 1

        return output

    def __can_place_validator(self, coords: Vector, locations_list: dict[tuple[Vector]:list[GameObject]]) -> bool:
        for i in range(len(locations_list)):
            if not isinstance(locations_list[i], Occupiable) and i < len(locations_list):
                raise AttributeError(f'{self.__class__.__name__} Current location is unoccupiable. '
                                     f'It is a(n) {locations_list[i].__class__.__name__} '
                                     f'and is at {coords}. This object must be at the end  of the locations list.')
            return True

    # def generate_map(self) -> None:
    #     # generate map
    #     self.game_map = [[Tile() for _ in range(self.map_size.x)] for _ in range(self.map_size.y)]
    #
    #     if self.walled:
    #         for x in range(self.map_size.x):
    #             if x == 0 or x == self.map_size.x - 1:
    #                 for y in range(self.map_size.y):
    #                     self.game_map[y][x].occupied_by = Wall()
    #             self.game_map[0][x].occupied_by = Wall()
    #             self.game_map[self.map_size.y - 1][x].occupied_by = Wall()
    #
    #     self.__populate_map()
    #
    # def __populate_map(self) -> None:
    #     for k, v in self.locations.items():
    #         if len(k) == 0 or len(v) == 0:  # Key-Value lengths must be > 0 and equal
    #             raise ValueError(
    #                 f'A key-value pair from game_board.locations has a length of 0. '
    #                 f'The length of the keys is {len(k)} and the length of the values is {len(v)}.')
    #
    #         # random.sample returns a randomized list which is used in __help_populate()
    #         j = random.sample(k, k=len(k))
    #         self.__help_populate(j, v)
    #
    # def __occupied_filter(self, game_object_list: list[GameObject]) -> list[GameObject]:
    #     """
    #     A helper method that returns a list of game objects that have the 'occupied_by' attribute.
    #     :param game_object_list:
    #     :return: a list of game object
    #     """
    #     return [game_object for game_object in game_object_list if hasattr(game_object, 'occupied_by')]
    #
    # def __help_populate(self, vector_list: list[Vector], game_object_list: list[GameObject]) -> None:
    #     """
    #     A helper method that helps populate the game map.
    #     :param vector_list:
    #     :param game_object_list:
    #     :return: None
    #     """
    #
    #     zipped_list: [tuple[list[Vector], list[GameObject]]] = list(zip(vector_list, game_object_list))
    #     last_vec: Vector = zipped_list[-1][0]
    #
    #     remaining_objects: list[GameObject] | None = self.__occupied_filter(game_object_list[len(zipped_list):]) \
    #         if len(self.__occupied_filter(game_object_list)) > len(zipped_list) \
    #         else None
    #
    #     # Will cap at smallest list when zipping two together
    #     for vector, game_object in zipped_list:
    #         if isinstance(game_object, Avatar):  # If the GameObject is an Avatar, assign it the coordinate position
    #             game_object.position = vector
    #
    #         temp_tile: GameObject = self.game_map[vector.y][vector.x]
    #
    #         while temp_tile.occupied_by is not None and hasattr(temp_tile.occupied_by, 'occupied_by'):
    #             temp_tile = temp_tile.occupied_by
    #
    #         if temp_tile.occupied_by is not None:
    #             raise ValueError(
    #                 f'Last item on the given tile doesn\'t have the \'occupied_by\' attribute. '
    #                 f'It is a(n) {temp_tile.occupied_by.__class__.__name__} with the value of {temp_tile.occupied_by}.')
    #
    #         temp_tile.occupied_by = game_object
    #
    #     if remaining_objects is None:
    #         return
    #
    #     # stack remaining game_objects on last vector
    #     temp_tile: GameObject = self.game_map[last_vec.y][last_vec.x]
    #
    #     while temp_tile.occupied_by is not None and hasattr(temp_tile.occupied_by, 'occupied_by'):
    #         temp_tile = temp_tile.occupied_by
    #
    #     for game_object in remaining_objects:
    #         if not hasattr(temp_tile, 'occupied_by') or temp_tile.occupied_by is not None:
    #             raise ValueError(
    #                 f'Last item on the given tile doesn\'t have the \'occupied_by\' attribute.'
    #                 f' It is a(n) {temp_tile.occupied_by.__class__.__name__} with the value of {temp_tile.occupied_by}.')
    #         temp_tile.occupied_by = game_object
    #         temp_tile = temp_tile.occupied_by

    # Returns the Vector and a list of GameObject for whatever objects you are trying to get
    def get_objects(self, look_for: ObjectType) -> list[tuple[Vector, list[GameObject]]]:
        """
        Zips together the game map's keys and values. A nested for loop then iterates through the zipped lists, and
        looks for any objects that have the same object type that was passed in. A list of tuples containing the
        coordinates and the objects found is returned.
        """

        results: list[tuple[Vector, list[GameObject]]] = []
        found: list[GameObject] = []

        # Zips the keys and values together
        zipped: list[tuple[Vector, list[GameObject]]] = zip(self.game_map.keys(), self.game_map.values())

        # Loops through the zipped list
        for couple in zipped:
            for obj in couple[1]:
                if obj.object_type is look_for:
                    found.append(obj)  # add the matching object to the found list

            # add values to result if something was found
            if len(found) > 0:
                results.append((couple[0], found))  # Add tuple pairings and objects found
                found = []  # reset the found list

        return results

    # Add the objects to the end of to_return (a list of GameObject)
    #     def __get_objects_help(self, look_for: ObjectType, temp: GameObject | Tile, to_return: list[GameObject]):
    #         while hasattr(temp, 'occupied_by'):
    #             if temp.object_type is look_for:
    #                 to_return.append(temp)
    #
    #             # The final temp is the last occupied by option which is either an Avatar, Station, or None
    #             temp = temp.occupied_by
    #
    #         if temp is not None and temp.object_type is look_for:
    #             to_return.append(temp)

    def to_json(self) -> dict:
        data: dict[str, object] = super().to_json()

        # data['game_map'] = None if self.game_map is None else \
        #     {coord: tiles for (coord, tiles) in list(zip([vector.to_json() for vector in self.game_map.keys()],
        #                                                  [self.game_map[key][0].to_json() for key in
        #                                                   self.game_map.keys()]))}
        data['game_map_vectors'] = [vec.to_json() for vec in self.game_map.keys()] if self.game_map is not None \
            else None
        data['game_map_objects'] = [[obj.to_json() for obj in v] for v in
                                    self.game_map.values()] if self.game_map is not None else None

        # data["game_map"] = [tile.to_json() for tile in tiles] if self.game_map is not None else None
        data["seed"] = self.seed
        data["map_size"] = self.map_size.to_json()
        data["location_vectors"] = [vec.to_json() for vec in self.locations.keys()] if self.locations is not None \
            else None
        data["location_objects"] = [[obj.to_json() for obj in v] for v in
                                    self.locations.values()] if self.locations is not None else None
        data["walled"] = self.walled
        data['event_active'] = self.event_active
        return data

    def generate_event(self, start: int, end: int) -> None:
        self.event_active = random.randint(start, end)

    def __from_json_helper(self, data: dict) -> GameObject:
        temp: ObjectType = ObjectType(data['object_type'])
        match temp:
            case ObjectType.TILE:
                return Tile().from_json(data)
            case ObjectType.WALL:
                return Wall().from_json(data)
            case ObjectType.OCCUPIABLE_STATION:
                return OccupiableStation().from_json(data)
            case ObjectType.STATION:
                return Station().from_json(data)
            case ObjectType.AVATAR:
                return Avatar().from_json(data)
            # If adding more ObjectTypes that can be placed on the game_board, specify here
            case _:
                raise ValueError(
                    f'The object type of the object is not handled properly. The object type passed in is {temp}.')

    def from_json(self, data: dict) -> Self:
        super().from_json(data)
        self.seed: int | None = data["seed"]
        self.map_size: Vector = Vector().from_json(data["map_size"])

        self.locations: dict[Vector, list[GameObject]] = {
            Vector().from_json(k): [self.__from_json_helper(obj) for obj in v] for k, v in
            zip(data["location_vectors"], data["location_objects"])} if data["location_vectors"] is not None else None

        self.walled: bool = data["walled"]
        self.event_active: int = data['event_active']

        self.game_map: dict[Vector, list[GameObject]] = {
            Vector().from_json(k): [self.__from_json_helper(obj) for obj in v] for k, v in
            zip(data["game_map_vectors"], data["game_map_objects"])} if data["game_map_vectors"] is not None else None
        # self.game_map: dict[Vector, list[Tile]] = [
        #     [Tile().from_json(tile) for tile in y] for y in temp] if temp is not None else None
        return self
